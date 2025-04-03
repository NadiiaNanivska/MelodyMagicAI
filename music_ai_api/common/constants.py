from music21 import duration

ROUND_PRECISION = 4
SEQ_LENGTH = 50
VOCAB_SIZE = 128

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