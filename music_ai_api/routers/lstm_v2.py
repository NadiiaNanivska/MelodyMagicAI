import asyncio
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
import numpy as np
import pandas as pd
from sklearn.calibration import LabelEncoder
import tensorflow as tf

from dto.request.lstm_dto import GenerateRequest, RawNotes
from generation.loss_functions import diversity_loss
from dto.response.generate_response import GenerateResponse
from utils.midi_utils_v2 import (
    classify_duration,
    convert_duration_to_seconds,
    get_note_durations_for_tempo,
    notes_to_midi_categorical
)
from generation.lstm_generator import predict_next_note_categorical
from common.constants import INSTRUMENT_NAMES, SEQ_LENGTH, PITCH_VOCAB_SIZE, EXECUTOR
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class MelodyGenerator:
    """Клас для генерації мелодій використовуючи LSTM модель."""

    def __init__(self, model_path: str):
        """
        Ініціалізація генератора мелодій.
        Args:
            model_path: Шлях до збереженої моделі LSTM
        Raises:
            RuntimeError: Якщо не вдалося завантажити модель
        """
        try:
            self.model = tf.keras.models.load_model(
                model_path,
                custom_objects={'diversity_loss': diversity_loss}
            )
            self.key_order = ['pitch', 'step', 'duration']
            self.label_encoder = self._init_label_encoder()
            logger.info(f"Модель успішно завантажено з {model_path}")
        except Exception as e:
            logger.error(f"Не вдалося завантажити модель: {e}")
            raise RuntimeError(f"Не вдалося ініціалізувати генератор мелодій: {e}")

    def _init_label_encoder(self) -> LabelEncoder:
        """Ініціалізує LabelEncoder на тренувальних даних."""
        try:
            all_notes = pd.read_parquet('common/dataset_categorical.parquet')
            train_notes = np.stack([all_notes[key] for key in self.key_order], axis=1)
            label_encoder = LabelEncoder()
            label_encoder.fit(train_notes[:, 2])
            return label_encoder
        except Exception as e:
            logger.error(f"Не вдалося ініціалізувати label encoder: {e}")
            raise RuntimeError(f"Не вдалося ініціалізувати label encoder: {e}")

    def _prepare_input_notes(
        self,
        start_notes: Optional[List[RawNotes]],
        note_durations: dict
    ) -> np.ndarray:
        """Підготовка вхідних нот для генерації."""
        if start_notes is None:
            return np.random.uniform(0, 1, (SEQ_LENGTH, 3))
        notes_array = np.array([[int(note.pitch), note.step, classify_duration(note.duration, note_durations)] 
                for note in start_notes[:SEQ_LENGTH]], dtype=object)
        
        repetitions = -(-SEQ_LENGTH // len(notes_array)) 
        notes_array = np.tile(notes_array, (repetitions, 1))
        return notes_array[:SEQ_LENGTH]

    def generate_melody(
        self,
        start_notes: Optional[List[RawNotes]],
        num_predictions: int,
        temperature: float,
        tempo: int
    ) -> str:
        """
        Генерація мелодії за допомогою LSTM.
        Args:
            start_notes: Початкові ноти для генерації
            num_predictions: Кількість нот для генерації
            temperature: Температура для семплінгу
            tempo: Темп мелодії (BPM)
        Returns:
            str: Назва згенерованого MIDI файлу
        """
        try:
            note_durations = get_note_durations_for_tempo(tempo)
            start_notes_array = self._prepare_input_notes(start_notes, note_durations)

            # Транспозиція в діапазон моделі
            # Зберігаємо інформацію про початкові висоти нот для подальшої транспозиції
            original_pitches = start_notes_array[:, 0].copy()
            original_avg_pitch = np.mean(original_pitches)
            model_preferred_range = (50, 80)  # Діапазон, в якому зазвичай генерує модель
            target_avg_pitch = sum(model_preferred_range) / 2
            bridge_length = min(8, SEQ_LENGTH // 2)
            for i in range(bridge_length):
                ratio = (i + 1) / bridge_length
                idx = SEQ_LENGTH - bridge_length + i
                shifted_pitch = original_pitches[idx] * (1 - ratio) + target_avg_pitch * ratio
                start_notes_array[idx, 0] = shifted_pitch
            
            notes = {name: start_notes_array[:, i] for i, name in enumerate(self.key_order)}
            start_notes_df = pd.DataFrame(notes)

            sample_notes = np.stack([start_notes_df[key] for key in self.key_order], axis=1)

            normalization_factors = np.array([PITCH_VOCAB_SIZE, 1, 1])

            pitch = sample_notes[:, 0].astype(np.float64)
            duration = sample_notes[:, 1].astype(np.float64)
            note_type_encoded = self.label_encoder.transform(sample_notes[:, 2]).astype(np.float64)
            sample_notes = np.stack([pitch, duration, note_type_encoded], axis=1)

            input_notes = (sample_notes[:SEQ_LENGTH] / normalization_factors)

            generated_notes = []
            prev_start = 0

            for _ in range(num_predictions):
                pitch, step, duration = predict_next_note_categorical(input_notes, self.model, temperature)
                duration_label = self.label_encoder.inverse_transform(np.array([int(duration)]))[0]
                duration_in_seconds = convert_duration_to_seconds(duration_label, tempo)
                
                start = prev_start + step
                end = start + duration_in_seconds

                normalized_pitch = pitch / PITCH_VOCAB_SIZE
                next_input_note = np.array([normalized_pitch, step, duration])
                generated_notes.append((int(pitch), float(step), duration_label, duration_in_seconds, float(start), float(end)))

                input_notes = np.delete(input_notes, 0, axis=0)
                input_notes = np.append(input_notes, np.expand_dims(next_input_note, 0), axis=0)
                prev_start = start

            notes_df = pd.DataFrame(generated_notes, columns=['pitch', 'step', 'duration_label', 'duration', 'start', 'end'])
            logger.debug(f"Згенеровані ноти у вигляді таблиці:\n{notes_df}")

            # Транспозиція згенерованих нот у діапазон вхідної послідовності
            # Обчислюємо необхідний зсув висоти для відповідності початковій середній висоті
            generated_avg_pitch = notes_df['pitch'].mean()
            pitch_shift = int(round(original_avg_pitch - generated_avg_pitch))
            notes_df['pitch'] = notes_df['pitch'].apply(
                lambda p: max(0, min(127, p + pitch_shift))
            )
            logger.debug(f"Згенеровані ноти після транспозиції:\n{notes_df}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_file = f'output_{timestamp}.mid'
            
            self._save_midi(notes_df, tempo, out_file)
            return out_file
            
        except Exception as e:
            logger.error(f"Не вдалося згенерувати мелодію: {e}")
            raise e

    def _save_midi(
        self,
        notes_df: pd.DataFrame,
        tempo: int,
        out_file: str
    ) -> None:
        """Зберігає згенеровані ноти у MIDI-файл."""
        logger.info(f"Початок збереження MIDI-файлу: {out_file}")
        try:
            instrument_name = INSTRUMENT_NAMES.get(0, "Unknown Instrument")
            notes_to_midi_categorical(
                notes_df,
                out_file='generated_midis/' + out_file,
                instrument_name=instrument_name,
                bpm=tempo
            )
        except Exception as e:
            logger.error(f"Помилка при збереженні MIDI-файлу {out_file}: {str(e)}")
            raise

melody_generator = MelodyGenerator('models/ckpt_best.model_lstm_attention_categorical.keras')

@router.post("/generate")
async def generate_music(request: GenerateRequest) -> dict:
    logger.info(f"Отримано запит на генерацію музики: темп={request.tempo}, "
                f"кількість нот={request.num_predictions}, "
                f"температура={request.temperature}")
    try:
        midi_file = await asyncio.get_event_loop().run_in_executor(
            EXECUTOR, 
            melody_generator.generate_melody, 
            request.start_notes,
            request.num_predictions,
            request.temperature,
            request.tempo
        )
        logger.info(f"Мелодію успішно згенеровано: {midi_file}")
        return GenerateResponse(message="Мелодія згенерована успішно", midi_file=midi_file).model_dump()
    except Exception as e:
        logger.error(f"Помилка при генерації музики: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
