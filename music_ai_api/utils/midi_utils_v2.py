import pandas as pd
import pretty_midi
import logging
from common.constants import ROUND_PRECISION, valid_durations

logger = logging.getLogger(__name__)

def get_note_durations_for_tempo(bpm):
    if bpm is None:
        logger.warning("Попередження: Інформацію про темп не знайдено в MIDI файлі. Неможливо обчислити абсолютні тривалості.")
        return None
    seconds_per_whole = (60 / bpm) * 4
    note_durations = {
        valid_durations[num]: round(seconds_per_whole / num, ROUND_PRECISION)
        for num in valid_durations if valid_durations[num] is not None
    }
    return note_durations

def classify_duration(duration, note_durations):
      duration = round(duration, ROUND_PRECISION)
      return min(note_durations, key=lambda note: abs(note_durations[note] - duration))

def find_key_by_value(dict_obj, value):
    for key, val in dict_obj.items():
        if val == value:
            return key
    return None

def convert_duration_to_seconds(duration_label, bpm):
    # Тривалість цілої ноти в секундах
    seconds_per_whole = (60 / bpm) * 4
    if isinstance(duration_label, pd.Series):
        duration_label = duration_label.item()
    key = find_key_by_value(valid_durations, duration_label)
    duration_in_seconds = seconds_per_whole / key
    return duration_in_seconds

def notes_to_midi_categorical(
  notes: pd.DataFrame,
  out_file: str,
  instrument_name: str,
  bpm = 120,
  velocity: int = 100
) -> pretty_midi.PrettyMIDI:

  pm = pretty_midi.PrettyMIDI()
  instrument = pretty_midi.Instrument(
      program=pretty_midi.instrument_name_to_program(
          instrument_name))

  prev_start = 0
  for i, note in notes.iterrows():
    duration_in_seconds = convert_duration_to_seconds(note['duration'], bpm)
    start = float(prev_start + note['step'])
    end = float(start + duration_in_seconds)
    note = pretty_midi.Note(
        velocity=velocity,
        pitch=int(note['pitch']),
        start=start,
        end=end,
    )
    instrument.notes.append(note)
    prev_start = start

  pm.instruments.append(instrument)
  pm.write(out_file)
  return pm