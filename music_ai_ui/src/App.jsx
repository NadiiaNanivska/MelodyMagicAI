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
  const [messageApi, contextHolder] = message.useMessage();
  const key = 'updatable';
  const error = (content) => messageApi.open({ key, type: 'error', content });
  const warning = (content) => messageApi.open({ key, type: 'warning', content });
  const success = (content) => messageApi.open({ key, type: 'success', content });

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
    <>
      {contextHolder}
      <Layout style={{ minHeight: '100vh', minWidth: '100vw' }}>
        <Sider collapsible>
          <div className="logo" style={{ padding: '20px', textAlign: 'center', color: '#fff' }}>
            🎵MusicMelodyAI
          </div>
          <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline" onClick={({ key }) => setActiveKey(key)}>
            <Menu.Item key="1" icon={<PlayCircleOutlined />}>
              Генерація мелодії
            </Menu.Item>
            <Menu.Item key="2" icon={<EditOutlined />}>
              Гармонізація мелодії
            </Menu.Item>
            <Menu.Item key="3" icon={<UploadOutlined />} onClick={showUploadModal}>
              Завантажити аудіофайл
            </Menu.Item>
          </Menu>
        </Sider>

        <Layout>
          <Header style={{ background: '#001529', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
            <Title level={3} style={{ color: '#fff', textAlign: 'center', display: 'contents' }}>
              Генератор музики на основі ШІ
            </Title>
          </Header>

          <Content style={{ margin: '20px 20px 20px 20px', background: '#fff', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
            {renderContent()}
          </Content>
        </Layout>

        <Modal title="Завантажити аудіофайл" visible={isUploadModalVisible} onOk={handleUploadOk} onCancel={handleUploadCancel}>
          <Upload customRequest={handleUpload} showUploadList={true} accept=".mid, .midi, .wav">
            <Button icon={<UploadOutlined />}>Натисніть, щоб завантажити аудіо</Button>
          </Upload>
        </Modal>
      </Layout>
    </>
  );
};

export default App;
