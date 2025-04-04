from datetime import datetime
import logging
from typing import List, Optional, Tuple

from fastapi import APIRouter, HTTPException
from pretty_midi import pretty_midi
import numpy as np
import pandas as pd
from sklearn.calibration import LabelEncoder
import tensorflow as tf

from dto.request.lstm_dto import GenerateRequest, RawNotes
from generation.loss_functions import diversity_loss
from utils.midi_utils_v2 import (
    classify_duration,
    convert_duration_to_seconds,
    get_note_durations_for_tempo,
    notes_to_midi_categorical
)
from generation.lstm_generator import predict_next_note_categorical
from common.constants import INSTRUMENT_NAMES, SEQ_LENGTH, PITCH_VOCAB_SIZE

logger = logging.getLogger(__name__)
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
            logger.info(f"Model loaded successfully from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Failed to initialize melody generator: {e}")

    def _init_label_encoder(self) -> LabelEncoder:
        """Ініціалізує і навчає LabelEncoder на тренувальних даних."""
        try:
            all_notes = pd.read_parquet('common/dataset_categorical.parquet')
            train_notes = np.stack([all_notes[key] for key in self.key_order], axis=1)
            label_encoder = LabelEncoder()
            label_encoder.fit(train_notes[:, 2])
            return label_encoder
        except Exception as e:
            logger.error(f"Failed to initialize label encoder: {e}")
            raise RuntimeError(f"Label encoder initialization failed: {e}")

    def _prepare_input_notes(
        self,
        start_notes: Optional[List[RawNotes]],
        note_durations: dict,
        tempo: int
    ) -> np.ndarray:
        """Підготовка вхідних нот для генерації."""
        if start_notes is None:
            return np.random.uniform(0, 1, (SEQ_LENGTH, 3))
            
        notes_array = np.array([[note.pitch, note.step, classify_duration(note.duration, note_durations)] 
                for note in start_notes[:SEQ_LENGTH]])
        
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
            start_notes_array = self._prepare_input_notes(start_notes, note_durations, tempo)
            
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
                duration_label = self.label_encoder.inverse_transform(np.array([int(duration)]))
                duration_in_seconds = convert_duration_to_seconds(duration_label, tempo)
                
                start = prev_start + step
                end = start + duration_in_seconds

                normalized_pitch = pitch / PITCH_VOCAB_SIZE
                next_input_note = np.array([normalized_pitch, step, duration])
                generated_notes.append((pitch, step, duration_label, start, end))

                input_notes = np.delete(input_notes, 0, axis=0)
                input_notes = np.append(input_notes, np.expand_dims(next_input_note, 0), axis=0)
                prev_start = start

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_file = f'output_{timestamp}.mid'
            
            self._save_midi(generated_notes, self.key_order, tempo, out_file)
            logger.info(f"Generated melody saved to {out_file}")
            return out_file
            
        except Exception as e:
            logger.error(f"Melody generation failed: {e}")
            raise e

    def _save_midi(
        self,
        generated_notes: List[Tuple],
        key_order: List[str],
        tempo: int,
        out_file: str
    ) -> None:
        """Зберігає згенеровані ноти у MIDI файл."""
        notes_df = pd.DataFrame(generated_notes, columns=(*key_order, 'start', 'end'))
        pm = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(program=0, name="Acoustic Grand Piano")
        pm.instruments.append(instrument)
        instrument_name = INSTRUMENT_NAMES.get(instrument.program, "Unknown Instrument")
        
        notes_to_midi_categorical(
            notes_df,
            out_file='generated_midis/' + out_file,
            instrument_name=instrument_name,
            bpm=tempo
        )

# Ініціалізація генератора мелодій
melody_generator = MelodyGenerator('models/ckpt_best.model_lstm_attention_categorical_new.keras')

@router.post("/generate")
async def generate_music(request: GenerateRequest) -> dict:
    """API endpoint для генерації мелодії."""
    try:
        midi_file = melody_generator.generate_melody(
            request.start_notes,
            request.num_predictions,
            request.temperature,
            request.tempo
        )
        return {
            "message": "LSTM мелодія згенерована",
            "midi_file": midi_file
        }
    except Exception as e:
        logger.error(f"Music generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
