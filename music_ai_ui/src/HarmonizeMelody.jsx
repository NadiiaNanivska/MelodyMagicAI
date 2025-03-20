import React, { useState } from "react";
import { Button, message } from "antd";
import MidiPlayer from "./MidiPlayer";

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
                <h2>🎼 Harmonize Melody</h2>

                {uploadedMidiRef.current ? (
                    <p>File Loaded: melody.mid</p>
                ) : (
                    <p>No MIDI file uploaded</p>
                )}

                <div style={{ marginTop: 20 }}>
                    <Button type="primary" onClick={harmonizeMelody}>
                        Harmonize Melody
                    </Button>
                </div>

                {harmonizedMidiUrl && (
                    <div style={{ marginTop: 20 }}>
                        <a href={harmonizedMidiUrl} download="harmonized_melody.mid">
                            <Button>
                                Download Harmonized MIDI
                            </Button>
                        </a>
                        <MidiPlayer fileUrl={harmonizedMidiUrl} showMidiPlayer={true} />
                    </div>
                )}
            </div>
        </>
    );
};

export default HarmonizeMelody;
