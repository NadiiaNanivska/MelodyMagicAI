from typing import List
from mido import Message, MetaMessage, MidiFile, MidiTrack
from utils.ffn_utils.cloudinary_utils import upload_mido_midi
from utils.ffn_utils.midi_message_generator import MidiMessageGenerator
from utils.ffn_models.note_info import NoteInfo

def get_track(note_infos: List[NoteInfo], track_number):
    track = MidiTrack()
    track.append(Message('program_change', program=0, time=0))
    message_generator = MidiMessageGenerator(note_infos, track_number)
    for midi_message in message_generator.get_midi_note_messages():
        track.append(midi_message)
    return track

def get_midi_file(track_note_infos: List[List[NoteInfo]], qpm: int = 120):
    mid = MidiFile(type=1)
    tempo_track = get_tempo_track(qpm)
    mid.tracks.append(tempo_track)
    for track_number, note_infos in enumerate(track_note_infos):
        track = get_track(note_infos, track_number + 1)
        mid.tracks.append(track) 
    return mid

def get_tempo_track(qpm):
    tempo_in_microseconds = int(60_000_000 / qpm)
    tempo_track = MidiTrack()
    tempo_track.append(MetaMessage('set_tempo', tempo=tempo_in_microseconds, time=0))
    return tempo_track

def generate_midi(name, track_note_infos: List[List[NoteInfo]], qpm: int = 120):
    midi_file = get_midi_file(track_note_infos, qpm)
    upload_mido_midi(mid=midi_file, out_file=name)
    midi_file.save(name)
