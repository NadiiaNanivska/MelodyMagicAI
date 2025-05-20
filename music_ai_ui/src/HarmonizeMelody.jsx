import React, { useState, useRef } from "react";
import { Button, message, Modal, Upload } from "antd";
import { UploadOutlined} from '@ant-design/icons';
import MidiPlayer from "./MidiPlayer";
import 'html-midi-player';

const base_server_url = "http://127.0.0.1:8000/api";

const HarmonizeMelody = () => {
    const [messageApi, contextHolder] = message.useMessage();
    const key = 'updatable';
    const [harmonizedMidiUrl, setHarmonizedMidiUrl] = useState(null);
    const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
    const uploadedMidiRef = useRef(null);
    const warning = (content) => messageApi.open({ key, type: 'warning', content });
    const error = (content) => messageApi.open({ key, type: 'error', content });
    const success = (content) => messageApi.open({ key, type: 'success', content, duration: 2 });
    const loading = (content = 'Гармонізація...') => {
        messageApi.open({
            key,
            type: 'loading',
            content,
            duration: 0
        });
    };

    const harmonizeMelody = async () => {
        const formData = new FormData();
        formData.append(
            "file",
            new Blob([uploadedMidiRef.current], { type: "audio/midi" }),
            "melody.mid"
        );

        try {
            loading("Гармонізація мелодії...");
            const harmonizeResponse = await fetch(`${base_server_url}/ffn/harmonize`, {
                method: "POST",
                body: formData,
            });

            if (!harmonizeResponse.ok) {
                error("Не вдалось гармонізувати мелодію.");
                return;
            }

            const { midi_file } = await harmonizeResponse.json();
            success("Мелодія успішно гармонізована!");

            console.log("Harmonized MIDI filename:", midi_file);

            const harmonizedUrl = `${base_server_url}/preview/${midi_file}`;
            setHarmonizedMidiUrl(harmonizedUrl);
            messageApi.destroy();
        } catch (err) {
            console.error("Error:", err);
            error("Помилка.");
        }
    };

    const handleUpload = (info) => {
    const file = info.file;
    if (!file.name.endsWith(".mid") && !file.name.endsWith(".midi")) {
      error("Завантажте валідний аудіофайл");
      return false;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      uploadedMidiRef.current = e.target.result;
      success("Аудіофайл успішно додано");
    };
    reader.readAsArrayBuffer(file);

    return false;
  };

  const showUploadModal = () => {
    setIsUploadModalVisible(true);
  };

  const handleUploadOk = () => {
    setIsUploadModalVisible(false);
    if (uploadedMidiRef.current) {
      harmonizeMelody();
    } else {
      warning("Спочатку додайте файл для гармонізації");
    }
  };

  const handleUploadCancel = () => {
    setIsUploadModalVisible(false);
  };

    return (
        <>
            {contextHolder}
            <div style={{ textAlign: "center", padding: "20px" }}>
                <Modal title="Завантажити аудіофайл" visible={isUploadModalVisible} onOk={handleUploadOk} onCancel={handleUploadCancel} cancelText="Скасувати">
                          <Upload customRequest={handleUpload} showUploadList={true} accept=".mid, .midi, .wav">
                            <Button icon={<UploadOutlined />}>Натисніть, щоб завантажити аудіо</Button>
                          </Upload>
                        </Modal>
                <h2>Гармонізація</h2>

                {uploadedMidiRef.current ? (
                    <p>Файл додано</p>
                ) : (
                    <p>Жодного файлу не додано</p>
                )}

                <div style={{ marginTop: 20 }}>
                    <Button type="primary" onClick={showUploadModal}>
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
                            <midi-visualizer type="staff" src='https://cdn.jsdelivr.net/gh/cifkao/html-midi-player@2b12128/twinkle_twinkle.mid'></midi-visualizer>
                            <MidiPlayer harmonizedMidiUrl={harmonizedMidiUrl} />
                        </section>
                    </div>
                )}
            </div>
        </>
    );
};

export default HarmonizeMelody;
