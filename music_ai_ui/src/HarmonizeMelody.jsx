import React, { useState } from "react";
import { Button, message } from "antd";
import MidiPlayer from "./MidiPlayer";
import 'html-midi-player';

const base_server_url = "http://127.0.0.1:8000/api";

const HarmonizeMelody = ({ uploadedMidiRef }) => {
    const [messageApi, contextHolder] = message.useMessage();
    const key = 'updatable';
    const [harmonizedMidiUrl, setHarmonizedMidiUrl] = useState(null);

    const error = (content) => messageApi.open({ key, type: 'error', content });
    const success = (content) => messageApi.open({ key, type: 'success', content, duration: 2 });
    const loading = (content = 'Processing...') => {
        messageApi.open({
            key,
            type: 'loading',
            content,
            duration: 0
        });
    };

    const harmonizeMelody = async () => {
        if (!uploadedMidiRef.current) {
            error("No MIDI file uploaded!");
            return;
        }

        console.log("Uploading MIDI file...");

        const formData = new FormData();
        formData.append(
            "file",
            new Blob([uploadedMidiRef.current], { type: "audio/midi" }),
            "melody.mid"
        );

        try {
            loading("Uploading MIDI file...");
            const uploadResponse = await fetch(`${base_server_url}/upload_midi`, {
                method: "POST",
                body: formData,
            });

            if (!uploadResponse.ok) {
                error("Failed to upload MIDI file.");
                return;
            }

            const { filename } = await uploadResponse.json();
            success("File uploaded successfully!");

            console.log("Uploaded MIDI filename:", filename);

            loading("Harmonizing melody...");
            const harmonizeResponse = await fetch(`${base_server_url}/ffn/harmonize/${filename}`, {
                method: "GET",
            });

            if (!harmonizeResponse.ok) {
                error("Failed to harmonize melody.");
                return;
            }

            const { midi_file } = await harmonizeResponse.json();
            success("Melody harmonized!");

            console.log("Harmonized MIDI filename:", midi_file);

            const harmonizedUrl = `${base_server_url}/preview/${midi_file}`;
            setHarmonizedMidiUrl(harmonizedUrl);
            messageApi.destroy();
        } catch (err) {
            console.error("Error:", err);
            error("Something went wrong.");
        }
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
                            <midi-visualizer type="staff" src={harmonizedMidiUrl}></midi-visualizer>
                            {harmonizedMidiUrl && (
                                <MidiPlayer harmonizedMidiUrl={harmonizedMidiUrl} />
                            )}
                        </section>
                    </div>
                )}
            </div>
        </>
    );
};

export default HarmonizeMelody;
