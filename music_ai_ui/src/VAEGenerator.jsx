import React, { useState, useEffect, useRef } from 'react';
import { Button, message, Upload, Row, Col, List, Modal } from 'antd';
import 'html-midi-player';
import * as mm from '@magenta/music';
import { UploadOutlined } from '@ant-design/icons';


const VAEGenerator = () => {
    const [messageApi, contextHolder] = message.useMessage();
    const uploadedMidiRef = useRef(null);
    const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
    const key = 'updatable';
    const warning = (content) => messageApi.open({ key, type: 'warning', content });
    const success = (content) => messageApi.open({ key, type: 'success', content });
    const loading = (content) => messageApi.open({ key, type: 'loading', content, duration: 0 });

    const [musicVAE, setMusicVAE] = useState(null);
    const [generatedSequence, setGeneratedSequence] = useState(null);
    const [melodyStart, setMelodyStart] = useState(null);
    const [melodyEnd, setMelodyEnd] = useState(null);
    const [interpolatedMelodies, setInterpolatedMelodies] = useState([]);

    useEffect(() => {
        const loadVAE = async () => {
            try {
                const vae = new mm.MusicVAE(
                    'https://storage.googleapis.com/magentadata/js/checkpoints/music_vae/mel_4bar_med_lokl_q2'
                );
                await vae.initialize();
                setMusicVAE(vae);
                success('MusicVAE завантажено!');
            } catch (error) {
                warning('Помилка при завантаженні MusicVAE.');
            }
        };
        loadVAE();
    }, []);

    const generateVariations = async () => {
        if (!musicVAE) {
            warning('MusicVAE ще не завантажено.');
            return;
        }

        try {
            loading('Генерація мелодії...');
            let sequence;

            // Якщо melodyStart є (завантажено початкову мелодію), використовуємо її для генерації варіацій
            if (uploadedMidiRef.current) {
                console.log('Генерація варіацій за допомогою завантаженого файлу...');
                const quantizedSequence = mm.sequences.quantizeNoteSequence(uploadedMidiRef.current, 4);
                // sequence = await musicVAE.interpolate([quantizedSequence, quantizedSequence], 1);
                sequence = await musicVAE.similar(quantizedSequence, 1, 0.5);
            } else {
                console.log('Генерація випадкової музики...');
                sequence = await musicVAE.sample(1);
            }
            setGeneratedSequence(sequence[0]);
            success('Варіації згенеровано!');
        } catch (error) {
            warning('Не вдалося згенерувати варіації.');
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
    };

    const handleUploadCancel = () => {
        setIsUploadModalVisible(false);
    };

    const playVariation = async () => {
        if (!generatedSequence) {
            warning('Спочатку згенеруйте варіацію.');
            return;
        }

        try {
            const player = new mm.Player();
            player.start(generatedSequence);
            success('Відтворення варіації! 🎶');
        } catch (error) {
            warning('Сталася помилка при відтворенні варіації.');
        }
    };

    const handleMidiUpload = async (file, isStart = true) => {
        const reader = new FileReader();
        reader.onload = async (e) => {
            let sequence = mm.midiToSequenceProto(e.target.result);
            sequence = mm.sequences.quantizeNoteSequence(sequence, 4);
            if (isStart) {
                setMelodyStart(sequence);
                success('Завантажено початкову мелодію!');
            } else {
                setMelodyEnd(sequence);
                success('Завантажено кінцеву мелодію!');
            }
        };
        reader.readAsArrayBuffer(file);
        return false;
    };

    const interpolateMelodies = async () => {
        if (!musicVAE || !melodyStart || !melodyEnd) {
            warning('Завантажте дві мелодії перед інтерполяцією.');
            return;
        }

        try {
            loading('Інтерполяція між двома мелодіями...');
            const interpolated = await musicVAE.interpolate([melodyStart, melodyEnd], 5);
            setInterpolatedMelodies(interpolated);
            success('Мелодії інтерпольовано! 🎼');
        } catch (error) {
            console.log(error);
            warning('Не вдалося виконати інтерполяцію.');
        }
    };

    const playInterpolated = async (index) => {
        if (!interpolatedMelodies.length) {
            warning('Спочатку виконайте інтерполяцію.');
            return;
        }

        try {
            const player = new mm.Player();
            player.start(interpolatedMelodies[index]);
            success(`Відтворюється інтерпольована мелодія ${index + 1}! 🎶`);
        } catch (error) {
            warning(error.message);
        }
    };

    return (
        <>
            {contextHolder}
            <Row gutter={16}>
                <Col span={12}>
                    <h3>Генерація варіацій</h3>
                    <Modal title="Завантажити аудіофайл" visible={isUploadModalVisible} onOk={handleUploadOk} onCancel={handleUploadCancel} cancelText="Скасувати">
                        <Upload customRequest={handleUpload} showUploadList={true} accept=".mid, .midi, .wav">
                            <Button icon={<UploadOutlined />}>Натисніть, щоб завантажити аудіо</Button>
                        </Upload>
                    </Modal>
                    <Button type="primary" onClick={generateVariations} style={{ marginRight: 10 }}>
                        Згенерувати мелодію
                    </Button>
                    <Button type="dashed" onClick={playVariation}>
                        Відтворити мелодію
                    </Button>
                    <Button style={{ marginLeft: 10 }} onClick={showUploadModal}>
                        Додати MIDI-файл
                    </Button>
                </Col>
                <Col span={12}>
                    <h3>Інтерполяція мелодій</h3>
                    <div style={{ marginBottom: '20px' }}>
                        <Upload beforeUpload={(file) => handleMidiUpload(file, true)} showUploadList={false}>
                            <Button style={{ marginRight: 10 }}>Додайте 1 мелодію</Button>
                        </Upload>
                        <Upload beforeUpload={(file) => handleMidiUpload(file, false)} showUploadList={false}>
                            <Button>Додайте 2 мелодію</Button>
                        </Upload>
                    </div>
                    <Button type="primary" onClick={interpolateMelodies} style={{ marginRight: 10 }}>
                        Інтерполювати мелодії
                    </Button>
                </Col>
            </Row>
            <Row style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
                <div style={{ marginTop: '20px' }}>
                    <section style={{ margin: '35px 0 0 0' }} id="section1">
                        <midi-visualizer
                            type="staff"
                            src="https://cdn.jsdelivr.net/gh/cifkao/html-midi-player@2b12128/twinkle_twinkle.mid">
                        </midi-visualizer>
                    </section>
                </div>
            </Row>
            <Row style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
                {interpolatedMelodies.length > 0 && (
                    <div style={{ marginTop: '20px', marginLeft: '50px' }}>
                        <h4>Інтерпольовані мелодії</h4>
                        <List
                            grid={{
                                gutter: 100,
                                column: 3,
                            }}
                            itemLayout="horizontal"
                            dataSource={interpolatedMelodies}
                            renderItem={(item, index) => (
                                <List.Item
                                    style={{ cursor: 'pointer', width: '120px' }}
                                    onClick={() => playInterpolated(index)}>
                                    <List.Item.Meta
                                        description={`Відтворити мелодію ${index + 1}`}
                                    />
                                </List.Item>
                            )}
                        />
                    </div>
                )}
            </Row>
        </>
    );
};

export default VAEGenerator;
