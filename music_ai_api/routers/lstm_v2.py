from fastapi import APIRouter, BackgroundTasks
import music21
from music21 import *
from pydantic import BaseModel
import os
import numpy as np
import pandas as pd
import tensorflow as tf

router = APIRouter()

SEQ_LENGTH = 40
VOCAB_SIZE = 364

model = tf.keras.models.load_model('models/best_model_kaggle_pond.keras')

class RawNotes(BaseModel):
    pitch: float
    duration: float

class GenerateRequest(BaseModel):
    start_notes: list[RawNotes] | None = None
    num_predictions: int
    temperature: float

def convertRequestToNotes(start_notes):
    notes = []
    notes_tmp = []
    for note in start_notes:
        notes_tmp.append(str(note.pitch) + '|' + str(note.duration))
    notes = notes_tmp
    while len(notes) < SEQ_LENGTH:
        notes += notes_tmp
    return notes

def generate_melody(start_notes, num_predictions, temperature):
    seed_sequence, _, reverse_mapping = prepare_sequences(convertRequestToNotes(start_notes), SEQ_LENGTH)
    print(seed_sequence)
    generated_notes = generate_music(
        model,
        SEQ_LENGTH,
        seed_sequence,
        reverse_mapping,
        VOCAB_SIZE,
        num_predictions,
        temperature
    )
    generated_melody = convert_to_music21(generated_notes)
    filename = 'output.mid'
    generated_melody.write('midi', filename)


def generate_music(model, seq_length, seed, reverse_mapping, n_vocab, num_notes, diversity=1.0):
    current_sequence = seed.copy()
    current_sequence = current_sequence.reshape(1, seq_length, 1)
    generated_notes = []
    for i in range(num_notes):
        prediction = model.predict(current_sequence, verbose=0)[0]
        prediction = np.log(prediction) / diversity
        exp_preds = np.exp(prediction)
        prediction = exp_preds / np.sum(exp_preds)
        index = np.random.choice(len(prediction), p=prediction)
        result = reverse_mapping[index]
        generated_notes.append(result)
        new_note = np.zeros((1, 1, 1))
        new_note[0, 0, 0] = index / float(n_vocab)
        current_sequence = np.concatenate((current_sequence[:, 1:, :], new_note), axis=1)
    return generated_notes

def convert_to_music21(note_list):
    melody = stream.Stream()
    offset = 0
    for note_str in note_list:
        parts = note_str.split('|')
        pitch_str = parts[0]
        duration_val = float(parts[1])
        if '.' in pitch_str or pitch_str.isdigit():
            chord_notes = pitch_str.split('.')
            notes_in_chord = []
            for p in chord_notes:
                note_obj = music21.note.Note(int(p))
                notes_in_chord.append(note_obj)
            chord_obj = chord.Chord(notes_in_chord)
            chord_obj.duration.quarterLength = duration_val
            chord_obj.offset = offset
            melody.append(chord_obj)
        else:
            note_obj = music21.note.Note(pitch_str)
            note_obj.duration.quarterLength = duration_val
            note_obj.offset = offset
            melody.append(note_obj)
        offset += duration_val
    return melody

def prepare_sequences(corpus, seq_length=40):
    unique_notes = sorted(list(set(corpus)))
    mapping = dict((c, i) for i, c in enumerate(unique_notes))
    reverse_mapping = dict((i, c) for i, c in enumerate(unique_notes))
    n_vocab = len(unique_notes)
    input_sequences = []
    output_notes = []
    for i in range(0, len(corpus) - seq_length, 1):
        sequence_in = corpus[i:i + seq_length]
        sequence_out = corpus[i + seq_length]
        input_sequences.append([mapping[char] for char in sequence_in])
        output_notes.append(mapping[sequence_out])
    n_patterns = len(input_sequences)
    X = np.reshape(input_sequences, (n_patterns, seq_length, 1)) / float(n_vocab)
    return X, mapping, reverse_mapping

@router.post("/generate")
def generate(request: GenerateRequest):
    midi_file = generate_melody(request.start_notes, request.num_predictions, request.temperature)
    return {"message": "LSTM мелодія згенерована", "midi_file": midi_file}