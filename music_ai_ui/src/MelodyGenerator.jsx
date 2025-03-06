import React, { useState, useCallback, useEffect, useReducer, useRef } from 'react';
import { Layout, Button, Select, InputNumber, Typography, message } from 'antd';
import VirtualPiano from './VirtualPiano';
import MidiPlayer from './MidiPlayer';

const { Content } = Layout;
const { Title } = Typography;
const { Option } = Select;

const midiToNote = (midiNumber) => {
    const notes = [
        'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'
    ];
    const octave = Math.floor(midiNumber / 12) - 1;
    const noteName = notes[midiNumber % 12];
    return `${noteName}${octave}`;
};

const MelodyGenerator = () => {
    const [messageApi, contextHolder] = message.useMessage();
    const warning = (content) => {
        messageApi.open({
            key,
            type: 'warning',
            content: content,
        });
    };
    const success = (content) => {
        messageApi.open({
            key,
            type: 'success',
            content: content,
        });
    };

    const key = 'updatable';
    const [style, setStyle] = useState('classical');
    const [tempo, setTempo] = useState(120);
    const [length, setLength] = useState(30);

    const startingNotesRef = useRef([]);
    const [startingNotes, setStartingNotes] = useState([]);

    const [midiNotes, setMidiNotes] = useState([]);
    useEffect(() => {
        setMidiNotes([60, 62, 64, 65, 67, 69, 71, 72]);
    }, []);

    const [width, setWidth] = useState(null);
    const div = useCallback(node => {
        if (node !== null) {
            setWidth(node.getBoundingClientRect().width);
        }
    }, []);

    const handleNoteSelect = useCallback((note) => {
        if (startingNotesRef.current.length < length / 5) {
            note = midiToNote(note);
            startingNotesRef.current.push(note);
            setStartingNotes((prev) => [...prev, note]);
        } else {
            warning(`You can only select up to ${length / 5} notes.`);
        }
    }, [startingNotesRef.current, length]);

    const generateMelody = async () => {
        console.log('Starting notes:', startingNotesRef.current);
        try {
            // Send request to generate melody
            success('Melody generated and downloaded successfully! 🎵');
        } catch (error) {
            warning('Failed to download the MIDI file.');
        }
    };

    const playMelody = async () => {
        try {
            // Send request to load the MIDI file and render MidiPlayer with correct file url
            success('Playing melody! 🎶');
        } catch (error) {
            warning(error.message);
        }
    };

    const randomMelody = () => {
        const randomNotes = Array.from({ length: 5 }, () => midiToNote(60 + Math.floor(Math.random() * 12)));
        setStartingNotes(randomNotes);
        success('Random melody created! 🎲');
    };

    return (
        <>
            {contextHolder}
            <Layout style={{ minHeight: '100%', minWidth: '100%' }} ref={div}>
                <Content style={{ textAlign: 'center' }}>
                    <Title level={2}>AI Melody Generator</Title>

                    <div style={{ margin: '20px 0' }}>
                        <Select value={style} onChange={setStyle} style={{ width: 200, marginRight: 20 }}>
                            <Option value="classical">Classical</Option>
                            <Option value="jazz">Jazz</Option>
                            <Option value="pop">Pop</Option>
                            <Option value="rock">Rock</Option>
                        </Select>

                        <InputNumber min={60} max={200} value={tempo} onChange={setTempo} style={{ marginRight: 20 }} /> BPM
                        <InputNumber min={4} max={64} value={length} onChange={setLength} style={{ marginLeft: 20 }} /> Notes
                    </div>

                    <div style={{ padding: '20px' }}>
                        <Button type="primary" onClick={generateMelody} style={{ marginRight: 10 }}>
                            Generate Melody
                        </Button>
                        <Button onClick={randomMelody} style={{ marginRight: 10 }}>
                            Random Melody
                        </Button>
                        <Button type="dashed" onClick={playMelody}>
                            Play Melody
                        </Button>
                    </div>
                    <div style={{ height: 'fit-content' }}>
                        <VirtualPiano onNoteSelect={handleNoteSelect} parentWidth={width} />
                        <MidiPlayer />
                    </div>
                    <div style={{ height: '20px' }}>
                        <h3>Starting Notes:</h3>
                        <div><p>{startingNotes.join(', ')}</p></div>
                    </div>
                </Content>
            </Layout>
        </>
    );
};

export default MelodyGenerator;
