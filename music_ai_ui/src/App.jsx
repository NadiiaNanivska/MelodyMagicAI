import React, { useState, useRef } from 'react';
import { Layout, Menu, Button, Typography, Upload, message } from 'antd';
import { PlayCircleOutlined, UploadOutlined, DownloadOutlined, EditOutlined } from '@ant-design/icons';
import MelodyGenerator from './MelodyGenerator';
import HarmonizeMelody from './HarmonizeMelody';
import './App.css';

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

const App = () => {
  const [activeKey, setActiveKey] = useState("1");
  const uploadedMidiRef = useRef(null); // 🔥 Використовуємо useRef замість useState

  const handleUpload = (info) => {
    const file = info.file;
    if (!file.name.endsWith(".mid") && !file.name.endsWith(".midi")) {
      message.error("Please upload a valid MIDI file.");
      return false;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      uploadedMidiRef.current = e.target.result;  // 🔥 Зберігаємо MIDI у useRef
      message.success("MIDI file uploaded successfully!");
    };
    reader.readAsArrayBuffer(file);

    return false;
  };

  const renderContent = () => {
    switch (activeKey) {
      case "1":
        return <MelodyGenerator uploadedMidiRef={uploadedMidiRef} />;
      case "2":
        return <HarmonizeMelody uploadedMidiRef={uploadedMidiRef} />;
      case "3":
        return (
          <Upload 
            customRequest={handleUpload} 
            showUploadList={false}
            accept=".mid, .midi, .wav"
          >
            <Button icon={<UploadOutlined />}>Click to Upload Audio</Button>
          </Upload>
        );
      case "4":
        return <Button icon={<DownloadOutlined />}>Download Audio File</Button>;
      default:
        return <div>Select a menu item</div>;
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
          <Menu.Item key="3" icon={<UploadOutlined />}>
            Upload Audio file
          </Menu.Item>
          <Menu.Item key="4" icon={<DownloadOutlined />}>
            Download Audio file
          </Menu.Item>
        </Menu>
      </Sider>

      <Layout>
        <Header style={{ background: '#001529', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
          <Title level={3} style={{ color: '#fff', textAlign: 'center', display: 'contents' }}>
            AI-Powered Music Generator
          </Title>
        </Header>

        <Content style={{ margin: '40px 20px 20px 20px', background: '#fff', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
          {renderContent()}
        </Content>

        <Footer style={{ textAlign: 'center' }}>
          © 2025 MusicMelodyAI — Your AI Melody Companion
        </Footer>
      </Layout>
    </Layout>
  );
};

export default App;
