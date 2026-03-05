import React, { useState, useEffect, useRef } from 'react';
import {
  Layout,
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
  Tag,
  Space,
  Badge,
  Radio,
  Progress,
  Steps,
  Collapse,
  Alert,
  Tooltip,
  Spin,
  Empty,
  Divider
} from 'antd';
import {
  UploadOutlined,
  CalculatorOutlined,
  FileTextOutlined,
  AppstoreOutlined,
  UnorderedListOutlined,
  TableOutlined,
  ProfileOutlined,
  FileSearchOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
  EyeOutlined,
  PartitionOutlined,
  BookOutlined,
  AlignLeftOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Step } = Steps;
const { Panel } = Collapse;

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 分割模式配置
const SPLIT_MODES = {
  sentence: {
    label: '按句子',
    icon: <AlignLeftOutlined />,
    description: '将文本按句子分割，适合细粒度识别',
    color: '#52c41a',
    useCase: '适用于需求描述详细、每句话对应独立功能的场景'
  },
  paragraph: {
    label: '按段落',
    icon: <ProfileOutlined />,
    description: '将文本按段落分割，适合中等粒度识别',
    color: '#1890ff',
    useCase: '适用于需求按段落组织，每段描述一个功能模块'
  },
  chapter: {
    label: '按篇章',
    icon: <BookOutlined />,
    description: '将文本按章节分割，适合粗粒度识别',
    color: '#722ed1',
    useCase: '适用于大型需求文档，按章节组织不同功能域'
  }
};

// 分析模式配置
const ANALYSIS_MODES = {
  traditional: {
    label: '传统分析',
    description: '一次性分析全部文本',
    icon: <FileSearchOutlined />
  },
  batch: {
    label: '批量分析',
    description: '按选择的分割模式分批分析',
    icon: <PartitionOutlined />
  }
};

function App() {
  // 输入状态
  const [requirementText, setRequirementText] = useState('');
  const [projectName, setProjectName] = useState('');
  
  // 分析设置
  const [analysisMode, setAnalysisMode] = useState('batch'); // 'traditional' | 'batch'
  const [splitMode, setSplitMode] = useState('sentence'); // 'sentence' | 'paragraph' | 'chapter'
  
  // 加载和进度状态
  const [loading, setLoading] = useState(false);
  const [analysisPhase, setAnalysisPhase] = useState('idle'); // 'idle' | 'splitting' | 'analyzing' | 'summarizing' | 'complete'
  const [progress, setProgress] = useState({ current: 0, total: 0, percent: 0 });
  
  // 预览状态
  const [previewData, setPreviewData] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  
  // 结果状态
  const [result, setResult] = useState(null);
  const [segmentResults, setSegmentResults] = useState([]);
  const [activeTab, setActiveTab] = useState('result');
  
  // 流式连接引用
  const eventSourceRef = useRef(null);

  // 清理函数
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // 获取分割预览
  const fetchPreview = async () => {
    if (!requirementText.trim() || requirementText.length < 50) {
      setPreviewData(null);
      return;
    }
    
    setPreviewLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/analyze/preview`, {
        text: requirementText,
        mode: splitMode
      });
      setPreviewData(response.data);
    } catch (error) {
      console.error('Preview error:', error);
    } finally {
      setPreviewLoading(false);
    }
  };

  // 分割模式改变时更新预览
  useEffect(() => {
    const timer = setTimeout(() => {
      if (analysisMode === 'batch') {
        fetchPreview();
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [splitMode, requirementText]);

  // 传统分析
  const analyzeTraditional = async () => {
    if (!requirementText.trim()) {
      message.warning('请输入需求文本');
      return;
    }

    setLoading(true);
    setAnalysisPhase('analyzing');
    setActiveTab('result');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        text: requirementText,
        project_name: projectName || '未命名项目'
      });
      
      setResult(response.data);
      setSegmentResults([]);
      setAnalysisPhase('complete');
      message.success('分析完成！');
    } catch (error) {
      message.error('分析失败：' + (error.response?.data?.detail || error.message));
      setAnalysisPhase('idle');
    } finally {
      setLoading(false);
    }
  };

  // 批量流式分析
  const analyzeBatchStream = async () => {
    if (!requirementText.trim()) {
      message.warning('请输入需求文本');
      return;
    }

    setLoading(true);
    setAnalysisPhase('splitting');
    setProgress({ current: 0, total: 0, percent: 0 });
    setSegmentResults([]);
    setResult(null);
    setActiveTab('progress');

    try {
      // 使用 fetch API 进行 SSE 请求
      const response = await fetch(`${API_BASE_URL}/analyze/batch/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: requirementText,
          project_name: projectName || '未命名项目',
          split_mode: splitMode
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              handleStreamEvent(event);
            } catch (e) {
              console.error('Parse event error:', e);
            }
          }
        }
      }
    } catch (error) {
      message.error('分析失败：' + error.message);
      setAnalysisPhase('idle');
    } finally {
      setLoading(false);
    }
  };

  // 处理流式事件
  const handleStreamEvent = (event) => {
    switch (event.type) {
      case 'split_complete':
        setAnalysisPhase('analyzing');
        setProgress({
          current: 0,
          total: event.data.total_segments,
          percent: 0
        });
        break;

      case 'segment_complete':
        setSegmentResults(prev => [...prev, event.data]);
        setProgress(prev => ({
          ...prev,
          current: event.data.index,
          percent: Math.round((event.data.index / event.data.total) * 100)
        }));
        break;

      case 'segment_error':
        message.warning(`片段 ${event.data.index} 分析失败: ${event.data.error}`);
        break;

      case 'complete':
        setResult(event.data);
        setAnalysisPhase('complete');
        setActiveTab('result');
        message.success('批量分析完成！');
        break;

      case 'error':
        message.error('分析错误：' + event.data.message);
        setAnalysisPhase('idle');
        break;

      default:
        break;
    }
  };

  // 开始分析
  const startAnalysis = () => {
    if (analysisMode === 'traditional') {
      analyzeTraditional();
    } else {
      analyzeBatchStream();
    }
  };

  // 文件上传
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
      setSegmentResults([]);
      setAnalysisMode('traditional');
      setActiveTab('result');
      message.success('文件分析完成！');
    } catch (error) {
      message.error('文件分析失败：' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
    return false;
  };

  // 获取类别标签颜色
  const getTypeColor = (type) => {
    const colors = {
      'ILF': 'blue',
      'EIF': 'cyan',
      'EI': 'green',
      'EO': 'orange',
      'EQ': 'purple'
    };
    return colors[type] || 'default';
  };

  // 获取类别中文名
  const getTypeName = (type) => {
    const names = {
      'ILF': '内部逻辑文件',
      'EIF': '外部接口文件',
      'EI': '外部输入',
      'EO': '外部输出',
      'EQ': '外部查询'
    };
    return names[type] || type;
  };

  // 功能点表格列定义
  const functionPointColumns = [
    {
      title: '序号',
      key: 'index',
      width: 60,
      align: 'center',
      render: (text, record, index) => index + 1
    },
    {
      title: '功能点项描述',
      dataIndex: 'name',
      key: 'description',
      width: 280,
      render: (name, record) => (
        <div>
          <div style={{ 
            whiteSpace: 'normal', 
            wordBreak: 'break-all',
            lineHeight: 1.6,
            color: '#333'
          }}>
            {name}
          </div>
          {record.sources && record.sources.length > 1 && (
            <Tag size="small" color="orange" style={{ marginTop: 4 }}>
              发现 {record.sources.length} 次
            </Tag>
          )}
        </div>
      )
    },
    {
      title: '功能点计数项名称',
      key: 'fp_name',
      width: 180,
      render: (record) => {
        const name = record.name || '';
        const keywords = ['创建', '添加', '新增', '录入', '查询', '搜索', '查看', 
                         '下载', '上传', '导入', '导出', '生成', '统计', '删除', '修改', '更新'];
        let action = '';
        for (const kw of keywords) {
          if (name.includes(kw)) {
            action = kw;
            break;
          }
        }
        let obj = name;
        if (action && name.includes(action)) {
          const parts = name.split(action);
          if (parts.length > 1) {
            obj = parts[1].substring(0, 10);
          }
        }
        const fpName = action && obj ? (obj + action) : name.substring(0, 15);
        return (
          <Text strong style={{ color: '#1890ff', fontSize: 14 }}>
            {fpName}
          </Text>
        );
      }
    },
    {
      title: '类别',
      dataIndex: 'type',
      key: 'type',
      width: 90,
      align: 'center',
      render: (type) => (
        <Tag color={getTypeColor(type)} style={{ fontSize: 13, fontWeight: 'bold' }}>
          {type}
        </Tag>
      )
    },
    {
      title: '复杂度',
      dataIndex: 'complexity',
      key: 'complexity',
      width: 90,
      align: 'center',
      render: (complexity) => {
        const colors = { 'Low': 'green', 'Average': 'blue', 'High': 'red' };
        const names = { 'Low': '低', 'Average': '中', 'High': '高' };
        return <Tag color={colors[complexity] || 'default'}>{names[complexity] || complexity}</Tag>;
      }
    },
    {
      title: 'UFP',
      dataIndex: 'count',
      key: 'count',
      width: 70,
      align: 'center',
      render: (count) => (
        <Text strong style={{ 
          fontSize: 16, 
          color: '#52c41a',
          background: '#f6ffed',
          padding: '2px 8px',
          borderRadius: 4,
          border: '1px solid #b7eb8f'
        }}>
          {count}
        </Text>
      )
    },
    {
      title: '来源片段',
      key: 'source',
      width: 120,
      render: (_, record) => {
        if (!record.sources) return '-';
        const firstSource = record.sources[0];
        return (
          <Tooltip title={firstSource.preview}>
            <Tag color="default" style={{ fontSize: 11 }}>
              片段 #{firstSource.segment_index + 1}
            </Tag>
          </Tooltip>
        );
      }
    }
  ];

  // 片段结果表格列
  const segmentColumns = [
    {
      title: '序号',
      dataIndex: 'index',
      key: 'index',
      width: 70,
      align: 'center',
      render: (index) => <Text strong>#{index + 1}</Text>
    },
    {
      title: '内容预览',
      dataIndex: 'segment',
      key: 'content',
      render: (segment) => (
        <div style={{ 
          maxWidth: 400,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          color: '#666'
        }}>
          {segment.content_preview}
        </div>
      )
    },
    {
      title: '状态',
      key: 'status',
      width: 100,
      align: 'center',
      render: (_, record) => (
        record.status === 'success' ? (
          <Tag icon={<CheckCircleOutlined />} color="success">完成</Tag>
        ) : (
          <Tag icon={<LoadingOutlined />} color="processing">分析中...</Tag>
        )
      )
    },
    {
      title: '识别功能点',
      key: 'found',
      width: 120,
      align: 'center',
      render: (_, record) => {
        const count = Object.values(record.found_components || {}).reduce((a, b) => a + b, 0);
        return count > 0 ? (
          <Badge count={count} style={{ backgroundColor: '#52c41a' }} />
        ) : (
          <Text type="secondary">-</Text>
        );
      }
    }
  ];

  // 准备类别汇总数据
  const getSummaryData = () => {
    if (!result || !result.function_points) return [];
    const typeOrder = ['ILF', 'EIF', 'EI', 'EO', 'EQ'];
    return typeOrder
      .map(type => {
        const items = result.function_points.filter(fp => fp.type === type);
        return {
          type,
          count: items.length,
          fp: items.reduce((sum, item) => sum + (item.count || 0), 0)
        };
      })
      .filter(item => item.count > 0);
  };

  return (
    <Layout className="layout" style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#1890ff' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <CalculatorOutlined style={{ fontSize: '24px', color: 'white', marginRight: '10px' }} />
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            NESMA 功能点计算器
          </Title>
          <Tag color="blue" style={{ marginLeft: 16, background: 'rgba(255,255,255,0.2)', color: 'white', border: 'none' }}>
            v2.0 批量分析
          </Tag>
        </div>
      </Header>

      <Content style={{ padding: '30px 30px', maxWidth: 1400, margin: '0 auto' }}>
        {/* 输入区域 */}
        <Card title="需求输入" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={24}>
              <Input
                placeholder="项目名称（可选）"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                style={{ marginBottom: 16 }}
                prefix={<AppstoreOutlined />}
              />
            </Col>
          </Row>

          {/* 分析设置 */}
          <Row gutter={24} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Card size="small" title="分析模式" bordered={false} style={{ background: '#f6ffed' }}>
                <Radio.Group 
                  value={analysisMode} 
                  onChange={(e) => setAnalysisMode(e.target.value)}
                  buttonStyle="solid"
                >
                  <Radio.Button value="traditional">
                    <Space>
                      <FileSearchOutlined />
                      传统分析
                    </Space>
                  </Radio.Button>
                  <Radio.Button value="batch">
                    <Space>
                      <PartitionOutlined />
                      批量分析
                    </Space>
                  </Radio.Button>
                </Radio.Group>
                <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                  {ANALYSIS_MODES[analysisMode].description}
                </div>
              </Card>
            </Col>
            
            {analysisMode === 'batch' && (
              <Col span={12}>
                <Card size="small" title="分割模式" bordered={false} style={{ background: '#e6f7ff' }}>
                  <Radio.Group 
                    value={splitMode} 
                    onChange={(e) => setSplitMode(e.target.value)}
                  >
                    {Object.entries(SPLIT_MODES).map(([key, config]) => (
                      <Radio.Button key={key} value={key}>
                        <Space>
                          {config.icon}
                          {config.label}
                        </Space>
                      </Radio.Button>
                    ))}
                  </Radio.Group>
                  <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                    {SPLIT_MODES[splitMode].description}
                  </div>
                </Card>
              </Col>
            )}
          </Row>

          {/* 分割预览 */}
          {analysisMode === 'batch' && previewData && (
            <Alert
              message={
                <Space>
                  <EyeOutlined />
                  <span>分割预览</span>
                  <Tag color={SPLIT_MODES[splitMode].color}>{SPLIT_MODES[splitMode].label}</Tag>
                </Space>
              }
              description={
                <div style={{ marginTop: 8 }}>
                  <Row gutter={16}>
                    <Col span={6}>
                      <Statistic title="总片段数" value={previewData.summary.count} suffix="个" />
                    </Col>
                    <Col span={6}>
                      <Statistic title="总字符数" value={previewData.summary.total_length} suffix="字符" />
                    </Col>
                    <Col span={6}>
                      <Statistic title="平均长度" value={previewData.summary.average_length} suffix="字符/片段" />
                    </Col>
                    <Col span={6}>
                      <Text type="secondary">{SPLIT_MODES[splitMode].useCase}</Text>
                    </Col>
                  </Row>
                  {previewData.segments.length > 0 && (
                    <Collapse ghost style={{ marginTop: 8 }}>
                      <Panel header={`查看前 ${previewData.segments.length} 个片段预览`} key="1">
                        {previewData.segments.map((seg, idx) => (
                          <div key={idx} style={{ 
                            padding: '8px 12px', 
                            marginBottom: 8, 
                            background: '#f5f5f5',
                            borderRadius: 4,
                            borderLeft: `3px solid ${SPLIT_MODES[splitMode].color}`
                          }}>
                            <Text strong style={{ color: SPLIT_MODES[splitMode].color }}>#{seg.index + 1}</Text>
                            <Text style={{ marginLeft: 8, fontSize: 12 }}>{seg.content_preview}</Text>
                          </div>
                        ))}
                        {previewData.has_more && (
                          <Text type="secondary" style={{ fontSize: 12 }}>还有更多片段...</Text>
                        )}
                      </Panel>
                    </Collapse>
                  )}
                </div>
              }
              type="info"
              style={{ marginBottom: 16 }}
            />
          )}

          <Tabs 
            defaultActiveKey="1"
            items={[
              {
                key: '1',
                label: '文本输入',
                children: (
                  <>
                    <TextArea
                      rows={10}
                      placeholder="在此输入软件需求文本...&#10;例如：&#10;系统应允许用户创建客户记录。&#10;用户可以搜索客户并生成月度报表。&#10;系统支持下载客户信息。"
                      value={requirementText}
                      onChange={(e) => setRequirementText(e.target.value)}
                    />
                    <Button
                      type="primary"
                      icon={<CalculatorOutlined />}
                      onClick={startAnalysis}
                      loading={loading}
                      style={{ marginTop: 16 }}
                      size="large"
                      block
                    >
                      {analysisMode === 'batch' ? '开始批量评估' : '开始评估'}
                    </Button>
                  </>
                )
              },
              {
                key: '2',
                label: '文件上传',
                children: (
                  <Upload.Dragger
                    beforeUpload={handleFileUpload}
                    showUploadList={false}
                    accept=".txt,.doc,.docx,.pdf"
                  >
                    <p className="ant-upload-drag-icon">
                      <UploadOutlined />
                    </p>
                    <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
                    <p className="ant-upload-hint">
                      支持文本文件、Word 文档和 PDF 文件
                    </p>
                  </Upload.Dragger>
                )
              }
            ]}
          />
        </Card>

        {/* 分析进度 */}
        {analysisPhase !== 'idle' && analysisPhase !== 'complete' && (
          <Card title="分析进度" style={{ marginBottom: 24 }}>
            <Steps current={analysisPhase === 'splitting' ? 0 : analysisPhase === 'analyzing' ? 1 : 2}>
              <Step title="文本分割" icon={analysisPhase === 'splitting' ? <LoadingOutlined /> : <CheckCircleOutlined />} />
              <Step title="分段识别" icon={analysisPhase === 'analyzing' ? <LoadingOutlined /> : <FileSearchOutlined />} />
              <Step title="结果汇总" icon={<TableOutlined />} />
            </Steps>
            
            {analysisPhase === 'analyzing' && (
              <div style={{ marginTop: 24 }}>
                <Row align="middle" gutter={16}>
                  <Col flex="auto">
                    <Progress 
                      percent={progress.percent} 
                      status="active"
                      strokeColor={SPLIT_MODES[splitMode].color}
                    />
                  </Col>
                  <Col>
                    <Text strong>{progress.current} / {progress.total} 片段</Text>
                  </Col>
                </Row>
              </div>
            )}
          </Card>
        )}

        {/* 结果展示 */}
        {(result || segmentResults.length > 0) && (
          <Tabs 
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: 'result',
                label: (
                  <Space>
                    <TableOutlined />
                    评估结果
                    {result?.function_points && (
                      <Badge count={result.function_points.length} style={{ backgroundColor: '#1890ff' }} />
                    )}
                  </Space>
                ),
                children: result && (
                  <>
                    {/* 统计概览 */}
                    <Card title="评估结果概览" style={{ marginBottom: 24 }}>
                      <Row gutter={16}>
                        <Col span={6}>
                          <Card>
                            <Statistic
                              title="未调整功能点 (UFP)"
                              value={result.total_unadjusted_fp || 0}
                              precision={0}
                              valueStyle={{ color: '#1890ff', fontSize: 28 }}
                            />
                          </Card>
                        </Col>
                        <Col span={6}>
                          <Card>
                            <Statistic
                              title="价值调整因子 (VAF)"
                              value={result.vaf || 1}
                              precision={2}
                            />
                          </Card>
                        </Col>
                        <Col span={6}>
                          <Card>
                            <Statistic
                              title="调整后功能点 (AFP)"
                              value={result.adjusted_fp || 0}
                              precision={2}
                              valueStyle={{ color: '#52c41a', fontWeight: 'bold', fontSize: 28 }}
                            />
                          </Card>
                        </Col>
                        <Col span={6}>
                          <Card>
                            <Statistic
                              title="功能项总数"
                              value={result.function_points ? result.function_points.length : 0}
                              suffix="个"
                            />
                          </Card>
                        </Col>
                      </Row>
                      
                      {analysisMode === 'batch' && result.segment_contributions && (
                        <Alert
                          message="批量分析统计"
                          description={
                            <Row gutter={16} style={{ marginTop: 8 }}>
                              <Col span={8}>
                                <Statistic title="分析片段数" value={result.total_segments} suffix="个" />
                              </Col>
                              <Col span={8}>
                                <Statistic 
                                  title="成功识别" 
                                  value={result.segment_contributions.filter(s => s.found_components > 0).length} 
                                  suffix="个片段" 
                                />
                              </Col>
                              <Col span={8}>
                                <Statistic title="去重后功能点" value={result.function_points.length} suffix="个" />
                              </Col>
                            </Row>
                          }
                          type="info"
                          showIcon
                          style={{ marginTop: 16 }}
                        />
                      )}
                    </Card>

                    {/* 功能清单明细表 */}
                    <Card 
                      title={
                        <Space>
                          <TableOutlined />
                          <span>功能清单明细</span>
                          <Badge count={result.function_points ? result.function_points.length : 0} 
                                 style={{ backgroundColor: '#1890ff' }} />
                        </Space>
                      } 
                      style={{ marginBottom: 24 }}
                    >
                      {(!result.function_points || result.function_points.length === 0) ? (
                        <Empty description="未识别到功能点" />
                      ) : (
                        <Table
                          dataSource={result.function_points.map((item, idx) => ({...item, key: idx}))}
                          columns={functionPointColumns}
                          rowKey="key"
                          pagination={result.function_points.length > 10 ? { 
                            pageSize: 10, 
                            showTotal: (total) => `共 ${total} 条记录` 
                          } : false}
                          bordered
                          size="small"
                          scroll={{ x: 1200 }}
                          summary={() => {
                            const totalUS = (result.function_points || []).reduce(
                              (sum, item) => sum + (item.count * 0.33), 0
                            ).toFixed(2);
                            return (
                              <Table.Summary fixed>
                                <Table.Summary.Row style={{ background: '#e6f7ff' }}>
                                  <Table.Summary.Cell index={0} colSpan={5} align="right">
                                    <Text strong style={{ fontSize: 16 }}>合计：</Text>
                                  </Table.Summary.Cell>
                                  <Table.Summary.Cell index={1} align="center">
                                    <Text strong style={{ 
                                      fontSize: 18, 
                                      color: '#52c41a',
                                      background: '#f6ffed',
                                      padding: '2px 10px',
                                      borderRadius: 4,
                                      border: '1px solid #b7eb8f'
                                    }}>
                                      {result.total_unadjusted_fp}
                                    </Text>
                                  </Table.Summary.Cell>
                                  <Table.Summary.Cell index={2} align="center">
                                    <Text strong style={{ fontSize: 14 }}>--</Text>
                                  </Table.Summary.Cell>
                                </Table.Summary.Row>
                              </Table.Summary>
                            );
                          }}
                        />
                      )}
                    </Card>

                    {/* 类别汇总 */}
                    <Card title="类别汇总统计">
                      <Row gutter={24}>
                        <Col span={16}>
                          <Table
                            dataSource={getSummaryData()}
                            columns={[
                              {
                                title: '类别',
                                dataIndex: 'type',
                                key: 'type',
                                render: (type) => (
                                  <Space>
                                    <Tag color={getTypeColor(type)}>{type}</Tag>
                                    <Text type="secondary">{getTypeName(type)}</Text>
                                  </Space>
                                )
                              },
                              {
                                title: '数量',
                                dataIndex: 'count',
                                key: 'count',
                                align: 'center',
                                width: 100
                              },
                              {
                                title: 'UFP合计',
                                dataIndex: 'fp',
                                key: 'fp',
                                align: 'center',
                                width: 120,
                                render: (fp) => (
                                  <Text strong style={{ color: '#52c41a', fontSize: 16 }}>{fp}</Text>
                                )
                              }
                            ]}
                            rowKey="type"
                            pagination={false}
                            bordered
                            size="small"
                          />
                        </Col>
                        <Col span={8}>
                          <Card size="small" title="复杂度分布" style={{ height: '100%' }}>
                            <div style={{ lineHeight: 2 }}>
                              {['ILF', 'EIF', 'EI', 'EO', 'EQ'].map(type => (
                                <div key={type}>
                                  <Tag color={getTypeColor(type)}>{type}</Tag>
                                  <Text>{result.component_counts?.[type] || 0} 个</Text>
                                </div>
                              ))}
                            </div>
                          </Card>
                        </Col>
                      </Row>
                    </Card>
                  </>
                )
              },
              {
                key: 'progress',
                label: (
                  <Space>
                    <UnorderedListOutlined />
                    片段分析详情
                    {segmentResults.length > 0 && (
                      <Badge count={segmentResults.length} style={{ backgroundColor: '#52c41a' }} />
                    )}
                  </Space>
                ),
                children: (
                  <Card title="各片段识别详情">
                    {segmentResults.length === 0 ? (
                      <Empty description="暂无分析数据" />
                    ) : (
                      <>
                        <Table
                          dataSource={segmentResults}
                          columns={segmentColumns}
                          rowKey="index"
                          pagination={false}
                          size="small"
                          bordered
                        />
                        <Divider />
                        <Collapse>
                          {segmentResults.filter(s => Object.keys(s.found_components || {}).length > 0).map((sr, idx) => (
                            <Panel 
                              header={`片段 #${sr.index} - 识别到 ${Object.values(sr.found_components).reduce((a, b) => a + b, 0)} 个功能点`} 
                              key={idx}
                            >
                              <div style={{ padding: 12, background: '#f6ffed', borderRadius: 4, marginBottom: 12 }}>
                                <Text strong>原文：</Text>
                                <Text>{sr.segment.content_preview}</Text>
                              </div>
                              {Object.entries(sr.found_components).map(([type, count]) => (
                                count > 0 && (
                                  <Tag key={type} color={getTypeColor(type)} style={{ margin: 4 }}>
                                    {getTypeName(type)}: {count} 个
                                  </Tag>
                                )
                              ))}
                            </Panel>
                          ))}
                        </Collapse>
                      </>
                    )}
                  </Card>
                )
              }
            ]}
          />
        )}

        {/* 关于 NESMA */}
        <Card title="关于 NESMA 功能点" style={{ marginTop: 24 }}>
          <Paragraph>
            NESMA（荷兰软件度量协会）功能点方法是一种标准化的软件功能规模测量技术。
            它通过识别软件中的数据功能和事务功能来计算功能点。
          </Paragraph>
          <Row gutter={16}>
            <Col span={12}>
              <Card size="small" title="数据功能">
                <p><Tag color="blue">ILF</Tag> 内部逻辑文件 (7-15 FP)</p>
                <p><Tag color="cyan">EIF</Tag> 外部接口文件 (5-10 FP)</p>
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="事务功能">
                <p><Tag color="green">EI</Tag> 外部输入 (3-6 FP)</p>
                <p><Tag color="orange">EO</Tag> 外部输出 (4-7 FP)</p>
                <p><Tag color="purple">EQ</Tag> 外部查询 (3-6 FP)</p>
              </Card>
            </Col>
          </Row>
          
          <Divider />
          
          <Title level={5}>批量分析说明</Title>
          <Row gutter={16}>
            {Object.entries(SPLIT_MODES).map(([key, config]) => (
              <Col span={8} key={key}>
                <Card size="small" title={<Space>{config.icon}{config.label}</Space>}>
                  <Text type="secondary">{config.description}</Text>
                  <div style={{ marginTop: 8 }}>
                    <Text strong>适用场景：</Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>{config.useCase}</Text>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      </Content>

      <Footer style={{ textAlign: 'center' }}>
        NESMA 功能点计算器 ©2024 - 支持批量分段分析
      </Footer>
    </Layout>
  );
}

export default App;
