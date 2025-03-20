import React from 'react';
import { Tabs, Layout } from 'antd';
import LSTMGenerator from './LSTMGenerator';
import VAEGenerator from './VAEGenerator';

const { TabPane } = Tabs;
const { Content } = Layout;

const MelodyGenerator = ({uploadedMidiRef}) => {
    return (
        <Layout style={{ minHeight: '100%', minWidth: '100%' }}>
            <Content style={{ textAlign: 'center' }}>
                <Tabs defaultActiveKey="lstm" centered>
                    <TabPane tab="LSTM Generator" key="lstm">
                        <LSTMGenerator />
                    </TabPane>
                    <TabPane tab="VAE Variations" key="vae">
                        <VAEGenerator uploadedMidiRef={uploadedMidiRef}/>
                    </TabPane>
                </Tabs>
            </Content>
        </Layout>
    );
};

export default MelodyGenerator;
