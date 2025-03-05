import React from 'react';
import { Layout, Button, Typography, Tabs } from 'antd';
import musicLogo from './assets/musicLogo.svg';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const App = () => (
  <Layout style={{ minHeight: '100vh', minWidth: '100vw' }}>
    <Header
      style={{
        background: '#1890ff',
        color: 'black',
        display: 'flex', // Flexbox для вирівнювання
        justifyContent: 'center', // Вирівнюємо по горизонталі
        alignItems: 'center', // Вирівнюємо по вертикалі
        height: '64px', // Встановлюємо висоту header
      }}
    >
      <Title level={3} style={{ color: 'white', margin: 0 }}>
        Музичний Генератор
      </Title>
      
    </Header>
    <Content
      style={{
        padding: '50px',
        background: '#f0f2f5',
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Tabs
        type="card"
        items={Array.from({
          length: 3,
        }).map((_, i) => {
          const id = String(i + 1);
          return {
            label: `Tab ${id}`,
            key: id,
            children: `Content of Tab Pane ${id}`,
          };
        })}
      />
      <div>
        <a target="_blank" rel="noopener noreferrer">
          <img
            src={musicLogo}
            className="logo react"
            alt="Music logo"
            style={{ width: '150px', height: 'auto', marginBottom: '20px' }}
          />
        </a>
      </div>
      <Button type="primary">Згенерувати мелодію</Button>
    </Content>
    <Footer style={{ textAlign: 'center' }}>© 2025 Music Generator</Footer>
  </Layout>
);

export default App;
