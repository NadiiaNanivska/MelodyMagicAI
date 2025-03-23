from utils.ffn_utils.dataset_one_hot_encoder import get_to_one_hot_encoding
from utils.ffn_utils.sequence_length_splitter import split_into_sequences
from utils.ffn_models.voices import voices
from utils.ffn_models.chorales_dataset import ChoralesDataset
import os
import numpy as np


def load_custom_midi_data(midi_files_dir, test_size=0.2, random_seed=42):
    """
    Завантажує дані з директорії з MIDI-файлами і формує датасет.
    
    Args:
        midi_files_dir (str): Шлях до директорії з MIDI-файлами.
        test_size (float): Частка тестових даних.
        random_seed (int): Зерно для випадкового розподілу.
        
    Returns:
        tuple: MIDI-дані та об'єкт ChoralesDataset.
    """
    # Створення структури даних для пісень
    sequence_data = {'soprano': [], 'alto': [], 'tenor': [], 'bass': []}
    
    # Отримуємо список файлів у директорії
    midi_files = [f for f in os.listdir(midi_files_dir) if f.endswith('.mid') or f.endswith('.midi')]
    
    # Перевірка, чи є достатньо файлів
    if len(midi_files) < 4:
        print(f"Увага: знайдено лише {len(midi_files)} MIDI-файлів, а потрібно мінімум 4.")
        print("Будемо використовувати доступні файли і дублювати їх, якщо потрібно.")
        
        # Якщо файлів менше 4, дублюємо наявні файли
        while len(midi_files) < 4:
            midi_files.append(midi_files[0])  # Дублюємо перший файл
    
    # Відбираємо перші 4 файли
    midi_files = midi_files[:4]
    print(f"Використовуємо файли: {midi_files}")
    
    # Зберігаємо дані MIDI для повернення
    midi_data_all = []
    
    # Обробляємо кожен MIDI-файл
    for idx, midi_file in enumerate(midi_files):
        midi_file_path = os.path.join(midi_files_dir, midi_file)
        print(f"Обробка файлу {idx+1}/4: {midi_file}")
        
        # Завантаження MIDI-файлу
        midi_data = analyze_simultaneous_pitches(midi_file_path)
        midi_data_all.append(midi_data)
        
        # Уявимо, що кожен MIDI-файл містить одну пісню
        song = midi_data
        
        # Для кожного голосу, отримуємо one-hot кодування та розбиваємо на послідовності
        for voice in voices.values():
            one_hot_encoding = get_to_one_hot_encoding(song, voice)
            sequences_split = split_into_sequences(one_hot_encoding)
            
            # Додаємо послідовності в дані
            sequence_data[voice.name] += sequences_split
    
    return (
        midi_data_all,
        ChoralesDataset(sequence_data)
    )


from mido import MidiFile
import numpy as np
from collections import defaultdict

def analyze_simultaneous_pitches(midi_file_path):
    """
    Аналізує MIDI-файл і визначає pitch-значення нот, які звучать одночасно.
    
    Args:
        midi_file_path (str): Шлях до MIDI-файлу.
        
    Returns:
        list: Список масивів з 4 елементів, що представляють одночасні pitch-значення.
    """
    # Завантаження MIDI-файлу
    mid = MidiFile(midi_file_path)
    
    # Створюємо словник для зберігання нот (активних і вимкнених) за часом
    note_events = defaultdict(list)
    
    # Поточний час у тіках
    current_time = 0
    
    # Словник для відстеження активних нот по каналах
    active_notes = {}
    
    # Обробка повідомлень MIDI
    for track in mid.tracks:
        current_time = 0
        for msg in track:
            current_time += msg.time
            
            # Перевіряємо, чи це повідомлення note_on або note_off
            if msg.type == 'note_on' and msg.velocity > 0:
                # Нота включена
                channel_note = (msg.channel, msg.note)
                active_notes[channel_note] = (msg.note, current_time)  # Зберігаємо pitch замість назви
                
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                # Нота виключена
                channel_note = (msg.channel, msg.note)
                if channel_note in active_notes:
                    note_pitch, start_time = active_notes[channel_note]
                    
                    # Додаємо подію включення ноти з pitch
                    note_events[start_time].append({"event": "note_on", "pitch": note_pitch, "channel": msg.channel})
                    
                    # Додаємо подію виключення ноти з pitch
                    note_events[current_time].append({"event": "note_off", "pitch": note_pitch, "channel": msg.channel})
                    
                    # Видаляємо ноту з активних
                    del active_notes[channel_note]
    
    # Знаходимо всі унікальні часові точки подій
    time_points = sorted(note_events.keys())
    
    # Створюємо словник для зберігання активних нот у кожен момент часу
    active_notes_at_time = {}
    currently_active = set()
    
    # Проходимо через всі часові точки
    for t in time_points:
        # Обробляємо події в цій часовій точці
        for event in note_events[t]:
            if event["event"] == "note_on":
                currently_active.add((event["pitch"], event["channel"]))
            elif event["event"] == "note_off":
                if (event["pitch"], event["channel"]) in currently_active:
                    currently_active.remove((event["pitch"], event["channel"]))
        
        # Зберігаємо поточний набір активних pitch
        active_notes_at_time[t] = [pitch for pitch, _ in currently_active]
    
    # Фільтруємо, щоб залишити лише точки з унікальними наборами нот
    unique_combinations = {}
    prev_pitches = None
    
    for t in sorted(active_notes_at_time.keys()):
        current_pitches = tuple(sorted(active_notes_at_time[t]))
        if current_pitches != prev_pitches and len(current_pitches) > 0:
            unique_combinations[t] = list(current_pitches)
        prev_pitches = current_pitches
    
    # Формуємо результат як список масивів по 4 елементи
    result_arrays = []
    
    for t in sorted(unique_combinations.keys()):
        pitches = unique_combinations[t]
        
        # Якщо кількість нот менше 4, доповнюємо нулями
        while len(pitches) < 4:
            pitches.append(0)
        
        # Якщо кількість нот більше 4, обрізаємо до 4
        if len(pitches) > 4:
            pitches = pitches[:4]
        
        result_arrays.append(pitches)
    
    return result_arrays