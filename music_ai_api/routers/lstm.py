from fastapi import APIRouter, BackgroundTasks
import pretty_midi
from pydantic import BaseModel
import os
import numpy as np
import pandas as pd
import random

import tensorflow as tf
from utils.midi_utils import notes_to_midi
from generation.lstm_generator import extend_scale, generate_chord_tones, generate_harmonic_intervals, predict_next_note

router = APIRouter()

def mse_with_positive_pressure(y_true: tf.Tensor, y_pred: tf.Tensor):
  mse = (y_true - y_pred) ** 2
  positive_pressure = 10 * tf.maximum(-y_pred, 0.0)
  return tf.reduce_mean(mse + positive_pressure)

model = tf.keras.models.load_model('models/ckpt_best.model_v1.keras',
                                   custom_objects={'mse_with_positive_pressure': mse_with_positive_pressure})

# Константи
SEQ_LENGTH = 25
VOCAB_SIZE = 128
VELOCITY_RANGE = 128

class RawNotes(BaseModel):
    interval: float
    pitch: float
    velocity: float
    duration: float
    polyphony: float
    step: float

class GenerateRequest(BaseModel):
    start_notes: list[RawNotes] | None = None
    num_predictions: int
    temperature: float

def generate_melody(start_notes, num_predictions, temperature):
    """Генерація мелодії за допомогою LSTM"""
    if start_notes is None:
        start_notes = [random.uniform(0, 1) for _ in range(SEQ_LENGTH)]
    
    start_notes_array = np.array([[note.interval, note.pitch, note.velocity, note.duration, note.polyphony, note.step] for note in start_notes[:SEQ_LENGTH]])
    while len(start_notes_array) < SEQ_LENGTH:
        start_notes_array = np.concatenate((start_notes_array, start_notes_array))
    start_notes_array = start_notes_array[:SEQ_LENGTH]

    key_order = ['pitch', 'step', 'duration','interval','velocity','polyphony']
    notes = {name: start_notes_array[:, i] for i, name in enumerate(key_order)}
    start_notes = pd.DataFrame(notes)

    interval_mean = start_notes['interval'].mean()
    interval_std = start_notes['interval'].std()
    velocity_range = 128

    sample_notes = np.stack([start_notes[key] for key in key_order], axis=1)


    sample_notes[:, 3] -= interval_mean / interval_std

    normalization_factors = np.array([
        VOCAB_SIZE,           # Pitch
        1,                    # Step (no normalization)
        1,                    # Duration (no normalization)
        1,                    # Interval already processed
        velocity_range,         # Velocity (divide by max, assuming min is 0)
        1                     # Polyphony (no normalization or encode if classification)
    ])

    # sequences
    input_notes = (
        sample_notes[:SEQ_LENGTH] /normalization_factors)
    
    generated_notes = []

    prev_pitch = input_notes[-1, 0] * VOCAB_SIZE
    prev_start = 0

    for _ in range(num_predictions):
        pitch, step, duration, interval, velocity, polyphony = predict_next_note(input_notes, model, temperature)

        pitch = prev_pitch + interval
        start = prev_start + step
        end = start + duration

        # Нормалізація для наступного прогнозу
        normalized_pitch = pitch / VOCAB_SIZE
        normalized_interval = (interval - interval_mean) / interval_std
        normalized_velocity = velocity / VELOCITY_RANGE

        next_input_note = np.array([normalized_pitch, step, duration, normalized_interval, normalized_velocity, polyphony])
        generated_notes.append((normalized_pitch, step, duration, normalized_interval, normalized_velocity, polyphony, start, end))

        # Define a scale relative to C-Major for simplicity; this could be any scale.
        c_major_scale = np.array([0, 2, 4, 5, 7, 9, 11])  # W-W-H-W-W-W-H steps

        # Extend the C Major scale across multiple octaves
        extended_c_major_scale = extend_scale(c_major_scale, octaves=0)

        '''Users: choose parameter to set your Polyphonic Mode'''
        polyphony_mode = 'harmonic_intervals'  # Choose 'chord_tones' Or 'harmonic_intervals'

        def generate_notes_based_on_polyphony(polyphony_mode, root_note, polyphony, scale, step, duration, velocity, start, end):
            if polyphony_mode == 'chord_tones':
                additional_pitches = generate_chord_tones(root_note, polyphony, scale)
            elif polyphony_mode == 'harmonic_intervals':
                additional_pitches = generate_harmonic_intervals(root_note, polyphony)
            else:
                raise ValueError("Invalid polyphony_mode. Choose 'chord_tones' or 'harmonic_intervals'.")

            for additional_pitch in additional_pitches:
                # Apply variations to velocity and duration
                var_velocity = np.clip(velocity + np.random.randint(-10, 11), 0, 127)
                var_duration = np.maximum(0, duration + np.random.uniform(-0.1, 0.1))

                generated_notes.append((additional_pitch, step, var_duration, interval, var_velocity, polyphony, start, end))

        #Generate polyphonic notes:
        if polyphony > 0:
            root_note = pitch
            # Get the notes in the scale for the current root note
            current_extended_scale = (root_note + extended_c_major_scale) % 128
            generate_notes_based_on_polyphony(polyphony_mode, root_note, polyphony, current_extended_scale, step, duration, velocity, start, end)


        # Update the input notes for the next prediction
        input_notes = np.delete(input_notes, 0, axis=0)
        input_notes = np.append(input_notes, np.expand_dims(next_input_note, 0), axis=0)

        # Update the previous values for the next iteration
        prev_start = start
        prev_pitch = pitch

    generated_notes = pd.DataFrame(
        generated_notes, columns=(*key_order, 'start', 'end'))

    print("Generated motes\n", generated_notes)
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0, name="Acoustic Grand Piano")
    pm.instruments.append(instrument)
    instrument_name = pretty_midi.program_to_instrument_name(instrument.program)
    out_file = 'generated_midis/output.mid'
    notes_to_midi(
        generated_notes, out_file=out_file, instrument_name=instrument_name)
    return out_file 

@router.post("/generate")
def generate_music(request: GenerateRequest):
    midi_file = generate_melody(request.start_notes, request.num_predictions, request.temperature)
    return {"message": "LSTM мелодія згенерована", "midi_file": midi_file}
