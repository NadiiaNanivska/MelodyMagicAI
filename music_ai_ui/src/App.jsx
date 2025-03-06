import React, { useState } from 'react';
import { Layout, Menu, Button, Typography, Upload, message } from 'antd';
import { PlayCircleOutlined, UploadOutlined, DownloadOutlined, EditOutlined } from '@ant-design/icons';
import MelodyGenerator from './MelodyGenerator';
import './App.css';

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

const App = () => {
  const [activeKey, setActiveKey] = useState("1");

  // Обробник для завантаження файлів
  const handleUpload = (file) => {
    message.success("MIDI file uploaded successfully!");
    return false;  // Призупинити автоматичне завантаження
  };

  const renderContent = () => {
    switch (activeKey) {
      case "1":
        return <MelodyGenerator />;
      case "2":
        return <div>Harmonize Melody component</div>;
      case "3":
        return (
          <Upload 
            customRequest={handleUpload} 
            showUploadList={false}
            accept=".mid, .midi"
          >
            <Button icon={<UploadOutlined />}>Click to Upload MIDI</Button>
          </Upload>
        );
      case "4":
        return <Button icon={<DownloadOutlined />}>Download MIDI File</Button>;
      default:
        return <div>Select a menu item</div>;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', minWidth: '100vw' }}>
      <Sider collapsible>
        <div className="logo" style={{ padding: '20px', textAlign: 'center', color: '#fff' }}>
          🎵 MusicMelodyAI
        </div>
        <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline" onClick={({ key }) => setActiveKey(key)}>
          <Menu.Item key="1" icon={<PlayCircleOutlined />}>
            Generate Melody
          </Menu.Item>
          <Menu.Item key="2" icon={<EditOutlined />}>
            Harmonize Melody
          </Menu.Item>
          <Menu.Item key="3" icon={<UploadOutlined />}>
            Upload MIDI
          </Menu.Item>
          <Menu.Item key="4" icon={<DownloadOutlined />}>
            Download MIDI
          </Menu.Item>
        </Menu>
      </Sider>

      <Layout>
        <Header style={{ background: '#001529', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
          <Title level={3} style={{ color: '#fff', textAlign: 'center', display: 'contents' }}>
            AI-Powered Music Generator
          </Title>
        </Header>

        <Content style={{ margin: '20px', background: '#fff', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
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
