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
  const currentPageRef = useRef(null);
  const [messageApi, contextHolder] = message.useMessage();

  const renderContent = () => {
    switch (activeKey) {
      case "1":
        currentPageRef.current = <MelodyGenerator />;
        return <MelodyGenerator />;
      case "2":
        currentPageRef.current = <HarmonizeMelody />;
        return <HarmonizeMelody />;
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
      </Layout>
    </>
  );
};

export default App;
