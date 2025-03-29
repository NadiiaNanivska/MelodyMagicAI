from datetime import datetime
from fastapi import APIRouter
import pretty_midi
from pydantic import BaseModel
import numpy as np
import pandas as pd
import random

import tensorflow as tf
from utils.midi_utils import notes_to_midi
from generation.lstm_generator import predict_next_note

router = APIRouter()

def mse_with_positive_pressure(y_true: tf.Tensor, y_pred: tf.Tensor):
  mse = (y_true - y_pred) ** 2
  positive_pressure = 10 * tf.maximum(-y_pred, 0.0)
  return tf.reduce_mean(mse + positive_pressure)

model = tf.keras.models.load_model('models/ckpt_best.model_v2_3.keras',
                                   custom_objects={'mse_with_positive_pressure': mse_with_positive_pressure})

print(model.summary())

# Константи
SEQ_LENGTH = 50
VOCAB_SIZE = 128

class RawNotes(BaseModel):
    pitch: float
    duration: float
    step: float

class GenerateRequest(BaseModel):
    start_notes: list[RawNotes] | None = None
    num_predictions: int
    temperature: float
    tempo: int

def generate_melody(start_notes, num_predictions, temperature, tempo):
    """Генерація мелодії за допомогою LSTM"""
    if start_notes is None:
        start_notes = [random.uniform(0, 1) for _ in range(SEQ_LENGTH)]
    
    start_notes_array = np.array([[note.pitch, note.duration,note.step] for note in start_notes[:SEQ_LENGTH]])
    while len(start_notes_array) < SEQ_LENGTH:
        start_notes_array = np.concatenate((start_notes_array, start_notes_array))
    start_notes_array = start_notes_array[:SEQ_LENGTH]

    key_order = ['pitch', 'step', 'duration']
    notes = {name: start_notes_array[:, i] for i, name in enumerate(key_order)}
    start_notes = pd.DataFrame(notes)

    sample_notes = np.stack([start_notes[key] for key in key_order], axis=1)

    normalization_factors = np.array([
        VOCAB_SIZE,           
        1,                    
        1
    ])

    # sequences
    input_notes = (
        sample_notes[:SEQ_LENGTH] /normalization_factors)
    
    generated_notes = []

    prev_start = 0

    for _ in range(num_predictions):
        pitch, step, duration = predict_next_note(input_notes, model, temperature)

        start = prev_start + step
        end = start + duration

        # Нормалізація для наступного прогнозу
        normalized_pitch = pitch / VOCAB_SIZE

        next_input_note = np.array([normalized_pitch, step, duration])
        generated_notes.append((pitch, step, duration, start, end))

        input_notes = np.delete(input_notes, 0, axis=0)
        input_notes = np.append(input_notes, np.expand_dims(next_input_note, 0), axis=0)

        prev_start = start

    generated_notes = pd.DataFrame(
        generated_notes, columns=(*key_order, 'start', 'end'))

    print("Generated motes\n", generated_notes)
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0, name="Acoustic Grand Piano")
    pm.instruments.append(instrument)
    instrument_name = pretty_midi.program_to_instrument_name(instrument.program)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = f'output_{timestamp}.mid'    
    notes_to_midi(
        generated_notes, out_file='generated_midis/' + out_file, instrument_name=instrument_name, tempo=tempo)
    return out_file 

@router.post("/generate")
def generate_music(request: GenerateRequest):
    midi_file = generate_melody(request.start_notes, request.num_predictions, request.temperature, request.tempo)
    return {"message": "LSTM мелодія згенерована", "midi_file": midi_file}
