import numpy as np
import utils.ffn_utils.constants as constants
from utils.ffn_models.song_note_range_tracker import SongNoteRangeTracker
from utils.ffn_models.voice import Voice


def get_to_one_hot_encoding(song: list, voice: Voice):
    one_hot_encoding = np.zeros((len(song), voice.range.range_and_silence_length()))
    note_range_tracker = SongNoteRangeTracker(voice)

    for song_position, song_segment in enumerate(song):
        voice_note = note_range_tracker.get_next_note(song_segment)

        if voice_note == -1:
            one_hot_encoding[song_position][constants.SILENCE_INDEX] = 1
            continue

        hot_encoding_note_pos = voice_note - voice.range.min_note + 1
        one_hot_encoding[song_position][hot_encoding_note_pos] = 1


    return one_hot_encoding