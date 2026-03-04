import React, { useState } from 'react';
import {
  Layout,
  Menu,
  Input,
  Button,
  Card,
  Table,
  Statistic,
  Row,
  Col,
  Typography,
  Upload,
  message,
  Tabs,
  Descriptions,
  Progress
} from 'antd';
import {
  UploadOutlined,
  CalculatorOutlined,
  FileExcelOutlined,
  InfoCircleOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph } = Typography;
const { TextArea } = Input;

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [requirementText, setRequirementText] = useState('');
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const analyzeRequirements = async () => {
    if (!requirementText.trim()) {
      message.warning('Please enter requirements text');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        text: requirementText,
        project_name: projectName || 'Untitled Project'
      });
      setResult(response.data);
      message.success('Analysis completed successfully!');
    } catch (error) {
      message.error('Analysis failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_name', projectName || file.name);

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/analyze-file`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
      message.success('File analysis completed!');
    } catch (error) {
      message.error('File analysis failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
    return false;
  };

  const columns = [
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: 'Complexity',
      dataIndex: 'complexity',
      key: 'complexity',
      render: (text) => {
        const colors = { Low: 'green', Average: 'orange', High: 'red' };
        return <span style={{ color: colors[text] }}>{text}</span>;
      }
    },
    {
      title: 'Weight',
      dataIndex: 'count',
      key: 'count'
    }
  ];

  return (
    <Layout className="layout" style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#1890ff' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <CalculatorOutlined style={{ fontSize: '24px', color: 'white', marginRight: '10px' }} />
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            NESMA Function Point Calculator
          </Title>
        </div>
      </Header>

      <Content style={{ padding: '50px 50px', maxWidth: 1200, margin: '0 auto' }}>
        <Card title="Input Requirements" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={24}>
              <Input
                placeholder="Project Name (optional)"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                style={{ marginBottom: 16 }}
              />
            </Col>
          </Row>

          <Tabs defaultActiveKey="1">
            <Tabs.TabPane tab="Text Input" key="1">
              <TextArea
                rows={8}
                placeholder="Enter your software requirements here..."
                value={requirementText}
                onChange={(e) => setRequirementText(e.target.value)}
              />
              <Button
                type="primary"
                icon={<CalculatorOutlined />}
                onClick={analyzeRequirements}
                loading={loading}
                style={{ marginTop: 16 }}
                size="large"
              >
                Analyze Requirements
              </Button>
            </Tabs.TabPane>

            <Tabs.TabPane tab="File Upload" key="2">
              <Upload.Dragger
                beforeUpload={handleFileUpload}
                showUploadList={false}
                accept=".txt,.doc,.docx,.pdf"
              >
                <p className="ant-upload-drag-icon">
                  <UploadOutlined />
                </p>
                <p className="ant-upload-text">Click or drag file to this area to upload</p>
                <p className="ant-upload-hint">
                  Supports text files, Word documents, and PDFs
                </p>
              </Upload.Dragger>
            </Tabs.TabPane>
          </Tabs>
        </Card>

        {result && (
          <Card title="Analysis Results" style={{ marginBottom: 24 }}>
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Card>
                  <Statistic
                    title="Unadjusted FP"
                    value={result.total_unadjusted_fp}
                    precision={0}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card>
                  <Statistic
                    title="VAF"
                    value={result.vaf}
                    precision={2}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card>
                  <Statistic
                    title="Adjusted FP"
                    value={result.adjusted_fp}
                    precision={2}
                    valueStyle={{ color: '#1890ff', fontWeight: 'bold' }}
                  />
                </Card>
              </Col>
            </Row>

            <Descriptions title="Component Summary" bordered style={{ marginBottom: 24 }}>
              <Descriptions.Item label="ILF (Internal Logical Files)">
                {result.details.component_counts.ILF}
              </Descriptions.Item>
              <Descriptions.Item label="EIF (External Interface Files)">
                {result.details.component_counts.EIF}
              </Descriptions.Item>
              <Descriptions.Item label="EI (External Inputs)">
                {result.details.component_counts.EI}
              </Descriptions.Item>
              <Descriptions.Item label="EO (External Outputs)">
                {result.details.component_counts.EO}
              </Descriptions.Item>
              <Descriptions.Item label="EQ (External Inquiries)">
                {result.details.component_counts.EQ}
              </Descriptions.Item>
              <Descriptions.Item label="Total Components">
                {result.function_points.length}
              </Descriptions.Item>
            </Descriptions>

            <Title level={4}>Detailed Components</Title>
            <Table
              dataSource={result.function_points}
              columns={columns}
              rowKey={(record, index) => index}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        )}

        <Card title="About NESMA Function Points">
          <Paragraph>
            The NESMA (Netherlands Software Metrics Association) function point method
            is a standardized technique for measuring the functional size of software.
          </Paragraph>
          <Row gutter={16}>
            <Col span={12}>
              <Card size="small" title="Data Functions">
                <p><strong>ILF</strong> - Internal Logical File (7-15 FP)</p>
                <p><strong>EIF</strong> - External Interface File (5-10 FP)</p>
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="Transactional Functions">
                <p><strong>EI</strong> - External Input (3-6 FP)</p>
                <p><strong>EO</strong> - External Output (4-7 FP)</p>
                <p><strong>EQ</strong> - External Inquiry (3-6 FP)</p>
              </Card>
            </Col>
          </Row>
        </Card>
      </Content>

      <Footer style={{ textAlign: 'center' }}>
        NESMA Function Point Calculator ©2024
      </Footer>
    </Layout>
  );
}

export default App;
