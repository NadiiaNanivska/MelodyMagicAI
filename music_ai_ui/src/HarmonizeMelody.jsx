import React, { useState } from "react";
import { Button, message } from "antd";
import MidiPlayer from "./MidiPlayer";
import 'html-midi-player';

const base_server_url = "http://127.0.0.1:8000";

const HarmonizeMelody = ({ uploadedMidiRef }) => {
    const [messageApi, contextHolder] = message.useMessage();
    const key = 'updatable';
    const [harmonizedMidiUrl, setHarmonizedMidiUrl] = useState(null);

    const error = (content) => messageApi.open({ key, type: 'error', content });
    const loading = () => {
        messageApi.open({
            key,
            type: 'loading',
            content: 'Melody harmonizing...',
            duration: 0
        });
        setTimeout(messageApi.destroy, 2500);
    };

    const harmonizeMelody = async () => {
        if (!uploadedMidiRef.current) {
            error("No MIDI file uploaded!");
            return;
        }

        console.log("Harmonizing melody...");

        const formData = new FormData();
        formData.append(
            "file",
            new Blob([uploadedMidiRef.current], { type: "audio/midi" }),
            "melody.mid"
        );

        const response = await fetch(`${base_server_url}/api/download/output.mid`, {
            method: "GET",
            type: "audio/midi",
            //   body: formData,
        });

        loading();

        if (!response.ok) {
            error("Failed to harmonize melody.");
            return;
        }

        const harmonizedMidi = await response.blob();
        console.log("Harmonized MIDI:", harmonizedMidi);
        const url = URL.createObjectURL(harmonizedMidi);
        console.log("Harmonized MIDI URL:", url);
        setHarmonizedMidiUrl(url);
        messageApi.destroy();
    };

    return (
        <>
            {contextHolder}
            <div style={{ textAlign: "center", padding: "20px" }}>
                <h2>Гармонізація</h2>

                {uploadedMidiRef.current ? (
                    <p>Файл додано</p>
                ) : (
                    <p>Жодного файлу не додано</p>
                )}

                <div style={{ marginTop: 20 }}>
                    <Button type="primary" onClick={harmonizeMelody}>
                        Гармонізувати
                    </Button>
                </div>

                {harmonizedMidiUrl && (
                    <div style={{ marginTop: 20 }}>
                        <a href={harmonizedMidiUrl} download="harmonized_melody.mid">
                            <Button>
                                Завантажити отриманий midi-файл
                            </Button>
                        </a>
                        <section style={{ margin: '35px 0 0 0' }} id="section1">
                            <midi-visualizer
                                type="staff"
                                src="https://cdn.jsdelivr.net/gh/cifkao/html-midi-player@2b12128/twinkle_twinkle.mid">
                            </midi-visualizer>
                            {harmonizedMidiUrl && (
                                <MidiPlayer
                                    harmonizedMidiUrl={`http://127.0.0.1:8000/api/download/${harmonizedMidiUrl}`}
                                />
                            )}
                        </section>
                    </div>
                )}
            </div>
        </>
    );
};

export default HarmonizeMelody;
