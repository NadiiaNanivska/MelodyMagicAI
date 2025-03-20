import React, { useState, useRef } from 'react';
import { Layout, Menu, Button, Typography, Upload, message, Modal } from 'antd';
import { PlayCircleOutlined, UploadOutlined, DownloadOutlined, EditOutlined } from '@ant-design/icons';
import MelodyGenerator from './MelodyGenerator';
import HarmonizeMelody from './HarmonizeMelody';
import './App.css';

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

const App = () => {
  const [activeKey, setActiveKey] = useState("1");
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
  const currentPageRef = useRef(null);
  const uploadedMidiRef = useRef(null);

  const handleUpload = (info) => {
    const file = info.file;
    if (!file.name.endsWith(".mid") && !file.name.endsWith(".midi")) {
      message.error("Please upload a valid MIDI file.");
      return false;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      uploadedMidiRef.current = e.target.result;
      message.success("MIDI file uploaded successfully!");
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

  const renderContent = () => {
    switch (activeKey) {
      case "1":
        currentPageRef.current = <MelodyGenerator uploadedMidiRef={uploadedMidiRef} />;
        return <MelodyGenerator uploadedMidiRef={uploadedMidiRef} />;
      case "2":
        currentPageRef.current = <HarmonizeMelody uploadedMidiRef={uploadedMidiRef} />;
        return <HarmonizeMelody uploadedMidiRef={uploadedMidiRef} />;
      default:
        return currentPageRef.current;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', minWidth: '100vw' }}>
      <Sider collapsible>
        <div className="logo" style={{ padding: '20px', textAlign: 'center', color: '#fff' }}>
          🎵MusicMelodyAI
        </div>
        <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline" onClick={({ key }) => setActiveKey(key)}>
          <Menu.Item key="1" icon={<PlayCircleOutlined />}>
            Generate Melody
          </Menu.Item>
          <Menu.Item key="2" icon={<EditOutlined />}>
            Harmonize Melody
          </Menu.Item>
          <Menu.Item key="3" icon={<UploadOutlined />} onClick={showUploadModal}>
            Upload Audio file
          </Menu.Item>
        </Menu>
      </Sider>

      <Layout>
        <Header style={{ background: '#001529', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
          <Title level={3} style={{ color: '#fff', textAlign: 'center', display: 'contents' }}>
            AI-Powered Music Generator
          </Title>
        </Header>

        <Content style={{ margin: '20px 20px 20px 20px', background: '#fff', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
          {renderContent()}
        </Content>

        {/* <Footer style={{ textAlign: 'center' }}>
          © 2025 MusicMelodyAI — Your AI Melody Companion
        </Footer> */}
      </Layout>

      <Modal title="Upload Audio File" visible={isUploadModalVisible} onOk={handleUploadOk} onCancel={handleUploadCancel}>
        <Upload customRequest={handleUpload} showUploadList={true} accept=".mid, .midi, .wav">
          <Button icon={<UploadOutlined />}>Click to Upload Audio</Button>
        </Upload>
      </Modal>
    </Layout>
  );
};

export default App;
