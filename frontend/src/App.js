import React, { useState } from 'react';
import { Layout, Input, Button, Table, Card, Typography, Space, message, Spin, Tag } from 'antd';
import { DownloadOutlined, SearchOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Header, Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const columns = [
  { title: '模块', dataIndex: 'module', key: 'module' },
  { title: '功能描述', dataIndex: 'description', key: 'description' },
  { 
    title: '类型', 
    dataIndex: 'type', 
    key: 'type',
    render: (type) => (
      <Tag color={{
        'ILF': 'blue',
        'EIF': 'cyan',
        'EI': 'green',
        'EO': 'orange',
        'EQ': 'purple'
      }[type]}>
        {type}
      </Tag>
    )
  },
  { 
    title: '复杂度', 
    dataIndex: 'complexity', 
    key: 'complexity',
    render: (c) => <Tag color={c === '高' ? 'red' : c === '中' ? 'gold' : 'green'}>{c}</Tag>
  },
];

function App() {
  const [requirement, setRequirement] = useState('');
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!requirement.trim()) {
      message.warning('请输入需求描述');
      return;
    }
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/analyze`, {
        requirement,
        project_name: projectName || '软件项目'
      });
      setResult(res.data);
      message.success('分析完成');
    } catch (err) {
      message.error('分析失败: ' + err.message);
    }
    setLoading(false);
  };

  const handleDownload = async () => {
    try {
      const res = await axios.post(`${API_BASE}/api/export/excel`, {
        requirement,
        project_name: projectName || '软件项目'
      }, { responseType: 'blob' });
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${projectName || '软件项目'}_FP.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('下载成功');
    } catch (err) {
      message.error('下载失败: ' + err.message);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#1890ff', padding: '0 24px' }}>
        <Title level={3} style={{ color: 'white', margin: '16px 0' }}>
          NESMA 功能点估算工具
        </Title>
      </Header>
      
      <Content style={{ padding: '24px', maxWidth: 1200, margin: '0 auto' }}>
        <Card title="需求输入" style={{ marginBottom: 24 }}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Input 
              placeholder="项目名称（可选）"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
            />
            <TextArea
              rows={8}
              placeholder="请输入需求描述，例如：需要一个电商系统，包括商品管理、订单管理、用户管理..."
              value={requirement}
              onChange={(e) => setRequirement(e.target.value)}
            />
            
            <Button 
              type="primary" 
              icon={<SearchOutlined />}
              onClick={handleAnalyze}
              loading={loading}
              size="large"
            >
              分析功能点
            </Button>
          </Space>
        </Card>

        {loading && (
          <Card style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" />
            <p>正在分析需求...请稍候</p>
          </Card>
        )}

        {result && !loading && (
          <Card 
            title="分析结果" 
            extra={
              <Button icon={<DownloadOutlined />} onClick={handleDownload}>
                导出 Excel
              </Button>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Space size="large">
                <Text>ILF: <strong>{result.summary?.ILF || 0}</strong></Text>
                <Text>EIF: <strong>{result.summary?.EIF || 0}</strong></Text>
                <Text>EI: <strong>{result.summary?.EI || 0}</strong></Text>
                <Text>EO: <strong>{result.summary?.EO || 0}</strong></Text>
                <Text>EQ: <strong>{result.summary?.EQ || 0}</strong></Text>
                <Text type="danger">总计: <strong>{result.summary?.total || 0}</strong></Text>
              </Space>
              
              <Table 
                dataSource={result.functions} 
                columns={columns} 
                rowKey={(r, i) => i}
                pagination={{ pageSize: 10 }}
              />
            </Space>
          </Card>
        )}
      </Content>
    </Layout>
  );
}

export default App;