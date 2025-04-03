import React, { useState, useCallback, useRef } from 'react';
import { Button, InputNumber, message } from 'antd';
import VirtualPiano from './VirtualPiano';
import MidiPlayer from './MidiPlayer';
import 'html-midi-player';

const base_server_url = "http://127.0.0.1:8000";
const SEQ_LENGTH = 50;

const midiToNote = (midiNumber) => {
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const octave = Math.floor(midiNumber / 12) - 1;
    return `${notes[midiNumber % 12]}${octave}`;
};

const LSTMGenerator = () => {
    const [messageApi, contextHolder] = message.useMessage();
    const key = 'updatable';
    const warning = (content) => messageApi.open({ key, type: 'warning', content });
    const success = (content) => messageApi.open({ key, type: 'success', content });
    const loading = (content) => messageApi.open({ key, type: 'loading', content, duration: 0 });

    const [tempo, setTempo] = useState(120);
    const [length, setLength] = useState(SEQ_LENGTH);

    const startingNotesRef = useRef([]);
    const [startingNotes, setStartingNotes] = useState([]);
    const [generatedMidiFile, setGeneratedMidiFile] = useState(null);

    const [width, setWidth] = useState(null);
    const div = useCallback((node) => {
        if (node !== null) {
            setWidth(node.getBoundingClientRect().width);
        }
    }, []);

    const handleNoteSelect = useCallback((note) => {
        if (startingNotesRef.current.length < SEQ_LENGTH) {
            const newNote = {
                pitch: note.pitch,
                step: startingNotesRef.current.length === 0 ? 0 : 1,
                duration: note.duration
            };
            startingNotesRef.current.push(newNote);
            setStartingNotes((prev) => [...prev, midiToNote(newNote.pitch)]);
        } else {
            warning(`Можна обрати не більше ${SEQ_LENGTH} нот.`);
        }
    }, [length]);

    const generateMelody = async () => {
        try {
            loading('Генерація мелодії...');

            const response = await fetch(`${base_server_url}/api/v1/lstm/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    start_notes: startingNotesRef.current,
                    num_predictions: length,
                    temperature: 1.0,
                    tempo: tempo
                }),
            });

            if (!response.ok) {
                throw new Error('Не вдалося згенерувати LSTM мелодію.');
            }

            const data = await response.json();
            console.log('LSTM generating melody response:', data);

            setGeneratedMidiFile(data.midi_file || 'output.mid');
            success('Мелодія згенерована!');
        } catch (error) {
            console.error('Generation error:', error);
            warning('Не вдалося згенерувати мелодію.');
        }
    };

    const randomMelody = () => {
        const popularDurations = [0.25, 0.5, 1, 1.5, 2];

        const randomNotes = Array.from({ length: 5 }, () => {
            const pitch = 60 + Math.floor(Math.random() * 12);

            const newNote = {
                pitch: pitch,
                step: startingNotesRef.current.length === 0 ? 0 : 1,
                duration: popularDurations[Math.floor(Math.random() * popularDurations.length)],
            };

            startingNotesRef.current.push(newNote);
            return midiToNote(60 + Math.floor(Math.random() * 12));
        });

        setStartingNotes(randomNotes);
        success('Випадкова мелодія згенерована!');
    };

    // Функція для очищення нот
    const clearStartingNotes = () => {
        startingNotesRef.current = [];
        setStartingNotes([]);
        success('Початкові ноти очищено.');
    };

    // Функція для завантаження MIDI файлу
    const downloadMidi = () => {
        if (generatedMidiFile) {
            const link = document.createElement('a');
            link.href = `${base_server_url}/api/download/${generatedMidiFile}`;
            link.download = generatedMidiFile;
            link.click();
        } else {
            warning('Мелодія ще не згенерована.');
        }
    };

    return (
        <>
            {contextHolder}
            <div ref={div}>
                <div style={{ margin: '20px 0' }}>
                    <InputNumber min={60} max={200} value={tempo} onChange={setTempo} style={{ marginRight: 20 }} /> BPM
                    <InputNumber min={SEQ_LENGTH} max={400} value={length} onChange={setLength} style={{ marginLeft: 20 }} /> К-сть нот
                </div>

                <div style={{ padding: '20px' }}>
                    <Button type="primary" onClick={generateMelody} style={{ marginRight: 10 }}>
                        Згенерувати мелодію
                    </Button>
                    <Button onClick={randomMelody} style={{ marginRight: 10 }}>
                        Випадкова початкова мелодія
                    </Button>
                    <Button onClick={clearStartingNotes} style={{ marginRight: 10 }}>
                        Очистити початкові ноти
                    </Button>
                    <Button onClick={downloadMidi} disabled={!generatedMidiFile} type="default">
                        Завантажити MIDI
                    </Button>
                </div>

                <div style={{ height: 'fit-content' }}>
                    <VirtualPiano onNoteSelect={handleNoteSelect} parentWidth={width} />
                    <section style={{ margin: '35px 0 0 0' }} id="section1">
                        <midi-visualizer
                            type="staff"
                            src="https://cdn.jsdelivr.net/gh/cifkao/html-midi-player@2b12128/twinkle_twinkle.mid">
                        </midi-visualizer>
                        {generatedMidiFile && (
                            <MidiPlayer
                                harmonizedMidiUrl={`http://127.0.0.1:8000/api/preview/${generatedMidiFile}`}
                            />
                        )}
                    </section>
                </div>

                <div style={{ height: '20px' }}>
                    <h3>Початкові ноти:</h3>
                    <p>{startingNotes.join(', ')}</p>
                </div>
            </div>
        </>
    );
};

export default LSTMGenerator;