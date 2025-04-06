from datetime import datetime
from fastapi import APIRouter
from  pretty_midi import pretty_midi
import numpy as np
import pandas as pd
import random

import tensorflow as tf
from common.constants import INSTRUMENT_NAMES, SEQ_LENGTH, PITCH_VOCAB_SIZE
from dto.request.lstm_dto import GenerateRequest
from generation.loss_functions import diversity_loss, percentile_loss
from dto.response.generate_response import GenerateResponse
from utils.midi_utils_v1 import notes_to_midi
from generation.lstm_generator import predict_next_note
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

# model = tf.keras.models.load_model('models/ckpt_best.model_v2_3.keras',
#                                    custom_objects={'mse_with_positive_pressure': mse_with_positive_pressure})

model = tf.keras.models.load_model('models/ckpt_best.model_lstm_attention_22.keras',
                                   custom_objects={'diversity_loss': diversity_loss,
                                                     'percentile_loss': percentile_loss})

logger.info(model.summary())


def generate_melody(start_notes, num_predictions, temperature, tempo):
    """Генерація мелодії за допомогою LSTM з Context Bridging та Transposition Post-Processing"""
    if start_notes is None:
        start_notes = [random.uniform(0, 1) for _ in range(SEQ_LENGTH)]
    
    # Convert start notes to array format
    start_notes_array = np.array([[note.pitch, note.duration, note.step] for note in start_notes[:SEQ_LENGTH]])
    while len(start_notes_array) < SEQ_LENGTH:
        start_notes_array = np.concatenate((start_notes_array, start_notes_array))
    start_notes_array = start_notes_array[:SEQ_LENGTH]

    # Save original pitch information for later transposition
    original_pitches = start_notes_array[:, 0].copy()
    logger.info(f"Original pitches: {original_pitches}")
    original_avg_pitch = np.mean(original_pitches)
    
    # Apply Context Bridging: Create a smooth transition to model's preferred range
    model_preferred_range = (50, 80)  # The range your model typically generates in
    target_avg_pitch = sum(model_preferred_range) / 2
    
    # Create bridge between original pitches and target range
    bridge_length = min(8, SEQ_LENGTH // 2)
    for i in range(bridge_length):
        # Gradually shift from seed to target range
        ratio = (i + 1) / bridge_length
        idx = SEQ_LENGTH - bridge_length + i
        shifted_pitch = original_pitches[idx] * (1 - ratio) + target_avg_pitch * ratio
        start_notes_array[idx, 0] = shifted_pitch
    
    key_order = ['pitch', 'step', 'duration']
    notes = {name: start_notes_array[:, i] for i, name in enumerate(key_order)}
    start_notes = pd.DataFrame(notes)

    sample_notes = np.stack([start_notes[key] for key in key_order], axis=1)

    normalization_factors = np.array([
        PITCH_VOCAB_SIZE,           
        1,                    
        1
    ])

    # sequences
    input_notes = (sample_notes[:SEQ_LENGTH] / normalization_factors)
    
    generated_notes = []
    prev_start = 0

    for _ in range(num_predictions):
        pitch, step, duration = predict_next_note(input_notes, model, temperature)

        start = prev_start + step
        end = start + duration

        normalized_pitch = pitch / PITCH_VOCAB_SIZE

        next_input_note = np.array([normalized_pitch, step, duration])
        generated_notes.append((pitch, step, duration, start, end))

        input_notes = np.delete(input_notes, 0, axis=0)
        input_notes = np.append(input_notes, np.expand_dims(next_input_note, 0), axis=0)

        prev_start = start

    generated_notes = pd.DataFrame(
        generated_notes, columns=(*key_order, 'start', 'end'))
    
    # Apply Transposition Post-Processing
    # Calculate the pitch shift needed to match original pitch average
    generated_avg_pitch = generated_notes['pitch'].mean()
    pitch_shift = int(round(original_avg_pitch - generated_avg_pitch))
    
    # Apply transposition to the generated notes
    generated_notes['pitch'] = generated_notes['pitch'].apply(
        lambda p: max(0, min(127, p + pitch_shift))
    )

    logger.info("Generated notes after transposition\n", generated_notes)
    
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0, name="Acoustic Grand Piano")
    pm.instruments.append(instrument)
    instrument_name = INSTRUMENT_NAMES.get(instrument.program, "Unknown Instrument")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = f'output_{timestamp}.mid'    
    notes_to_midi(
        generated_notes, out_file='generated_midis/' + out_file, instrument_name=instrument_name, tempo=tempo)
    return out_file

@router.post("/generate")
def generate_music(request: GenerateRequest):
    midi_file = generate_melody(request.start_notes, request.num_predictions, request.temperature, request.tempo)
    return GenerateResponse(message="Мелодія згенерована успішно", midi_file=midi_file). model_dump()
