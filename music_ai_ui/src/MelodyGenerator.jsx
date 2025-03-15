import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Layout, Button, Select, InputNumber, Typography, Tabs, message } from 'antd';
import VirtualPiano from './VirtualPiano';
import MidiPlayer from './MidiPlayer';

const { Content } = Layout;
const { Option } = Select;
const { TabPane } = Tabs;

const midiToNote = (midiNumber) => {
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const octave = Math.floor(midiNumber / 12) - 1;
    return `${notes[midiNumber % 12]}${octave}`;
};

const MelodyGenerator = ({uploadedMidiRef}) => {
    const [messageApi, contextHolder] = message.useMessage();
    const key = 'updatable';
    const warning = (content) => messageApi.open({ key, type: 'warning', content });
    const success = (content) => messageApi.open({ key, type: 'success', content });

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
            const newNote = {
                pitch: note.pitch,  
                step: startingNotesRef.current.length === 0 ? 0 : 1,
                duration: note.duration,  
                velocity: note.velocity, 
            };
            startingNotesRef.current.push(newNote);
            setStartingNotes((prev) => [...prev, midiToNote(newNote.pitch)]);
        } else {
            warning(`You can only select up to ${length / 5} notes.`);
        }
    }, [startingNotesRef.current, length]);

    const generateMelody = async () => {
        try {
            console.log('LSTM generating melody:', startingNotesRef.current);
            success('LSTM Melody generated successfully! 🎵');
        } catch (error) {
            warning('Failed to generate LSTM melody.');
        }
    };

    const generateVariations = async () => {
        try {
            console.log('VAE generating variations for:', midiNotes);
            success('VAE variations generated! 🎼');
        } catch (error) {
            warning('Failed to generate VAE variations.');
        }
    };

    const playMelody = async () => {
        try {
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
                    <Tabs defaultActiveKey="lstm" centered>
                        {/* Вкладка для LSTM */}
                        <TabPane tab="LSTM Generator" key="lstm">
                            <div style={{ margin: '20px 0' }}>
                                <InputNumber min={60} max={200} value={tempo} onChange={setTempo} style={{ marginRight: 20 }} /> BPM
                                <InputNumber min={4} max={64} value={length} onChange={setLength} style={{ marginLeft: 20 }} /> Notes
                            </div>

                            <div style={{ padding: '20px' }}>
                                <Button type="primary" onClick={generateMelody} style={{ marginRight: 10 }}>
                                    Generate LSTM Melody
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
                                <p>{startingNotes.join(', ')}</p>
                            </div>
                        </TabPane>

                        {/* Вкладка для VAE */}
                        <TabPane tab="VAE Variations" key="vae">
                            <div style={{ margin: '20px 0' }}>
                                <Select value={style} onChange={setStyle} style={{ width: 200, marginRight: 20 }}>
                                    <Option value="classical">Classical</Option>
                                    <Option value="jazz">Jazz</Option>
                                    <Option value="pop">Pop</Option>
                                    <Option value="rock">Rock</Option>
                                </Select>
                            </div>

                            <div style={{ padding: '20px' }}>
                                <Button type="primary" onClick={generateVariations} style={{ marginRight: 10 }}>
                                    Generate Variations (VAE)
                                </Button>
                                <Button type="dashed" onClick={playMelody}>
                                    Play Variation
                                </Button>
                            </div>

                            <MidiPlayer />
                        </TabPane>
                    </Tabs>
                </Content>
            </Layout>
        </>
    );
};

export default MelodyGenerator;
