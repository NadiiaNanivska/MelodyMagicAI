from concurrent.futures import ThreadPoolExecutor
from music21 import duration

all_durations = duration.typeFromNumDict
excluded_durations = {'breve', 'longa', 'maxima', 'duplex-maxima', 'zero'}
valid_durations = {
    value: name
    for value, name in all_durations.items()
    if name not in excluded_durations
}

INSTRUMENT_NAMES = {
    0: "Acoustic Grand Piano",
    1: "Bright Acoustic Piano",
    2: "Electric Grand Piano",
}

ROUND_PRECISION = 4
SEQ_LENGTH = 50
PITCH_VOCAB_SIZE = 128
DURATION_VOCAB_SIZE = len(valid_durations)

FILE_NOT_FOUND = "Файл не знайдено"

EXECUTOR = ThreadPoolExecutor(max_workers=5)