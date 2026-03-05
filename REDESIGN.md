# NESMA 功能点分析 - 识别流程重设计

## 概述

本次重构重新设计了需求识别流程，支持用户选择按**句子**、**段落**、**篇章**三种模式进行分批识别，并提供实时进度反馈和汇总展示。

## 新功能特性

### 1. 三种分割模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **按句子** | 将文本按句子分割，逐句识别功能点 | 需求描述详细，每句话对应一个独立功能 |
| **按段落** | 将文本按段落分割，逐段识别功能点 | 需求按段落组织，每段描述一个功能模块 |
| **按篇章** | 将文本按章节分割，逐章识别功能点 | 大型需求文档，按章节组织不同功能域 |

### 2. 两种分析模式

- **传统分析**：一次性分析全部文本（保留原有功能）
- **批量分析**：按选择的分割模式分批分析，实时显示进度

### 3. 流式进度反馈

批量分析时，前端通过 SSE (Server-Sent Events) 接收实时进度：
- 文本分割完成通知
- 每个片段分析完成通知
- 最终结果汇总

### 4. 智能去重

批量分析时，系统会自动合并不同片段中识别到的相同功能点，并记录其来源信息。

## API 变更

### 新增端点

#### 1. 批量分析（非流式）
```http
POST /analyze/batch
Content-Type: application/json

{
  "text": "需求文本...",
  "project_name": "项目名称",
  "split_mode": "sentence" | "paragraph" | "chapter"
}
```

响应：
```json
{
  "project_name": "项目名称",
  "split_mode": "sentence",
  "total_segments": 5,
  "processed_segments": 5,
  "function_points": [...],
  "total_unadjusted_fp": 25,
  "adjusted_fp": 25.75,
  "vaf": 1.03,
  "component_counts": {...},
  "segment_results": [...]
}
```

#### 2. 批量分析（流式）
```http
POST /analyze/batch/stream
Content-Type: application/json

{
  "text": "需求文本...",
  "project_name": "项目名称",
  "split_mode": "sentence"
}
```

SSE 事件类型：
- `split_complete` - 文本分割完成
- `segment_complete` - 单个片段分析完成
- `segment_error` - 单个片段分析出错
- `complete` - 全部完成
- `error` - 错误

#### 3. 分割预览
```http
POST /analyze/preview
Content-Type: application/json

{
  "text": "需求文本...",
  "mode": "sentence"
}
```

#### 4. 获取分割模式列表
```http
GET /split-modes
```

## 前端界面

### 新增功能

1. **分析模式选择器**
   - 传统分析
   - 批量分析

2. **分割模式选择器**
   - 按句子
   - 按段落
   - 按篇章

3. **分割预览区域**
   - 显示分割结果统计
   - 预览前10个片段
   - 显示每个片段的长度和预览内容

4. **实时进度展示**
   - 步骤条显示当前阶段
   - 进度条显示分析进度
   - 已处理/总片段数

5. **片段分析详情**
   - 显示每个片段的分析状态
   - 显示每个片段识别的功能点数量
   - 可展开查看片段详情

6. **结果汇总展示**
   - 显示各片段的贡献统计
   - 显示去重后的功能点列表
   - 显示功能点来源信息

## 代码结构

```
backend/
├── main.py                    # 更新：新增批量分析端点
├── nesma/
│   ├── __init__.py           # 更新：导出新增模块
│   ├── analyzer.py           # 原有：需求分析器
│   ├── calculator.py         # 原有：功能点计算器
│   ├── excel_generator.py    # 原有：Excel生成器
│   ├── text_splitter.py      # 新增：文本分割器
│   └── batch_analyzer.py     # 新增：批量分析器

frontend/
└── src/
    └── App.js                # 更新：新增批量分析界面
```

## 运行方式

### 启动后端
```bash
cd backend
python main.py
```

### 启动前端
```bash
cd frontend
npm start
```

### 测试 API
```bash
python test_batch_api.py
```

## 使用流程

1. 输入需求文本或上传文件
2. 选择分析模式：
   - 选择"批量分析"以使用新功能
3. 选择分割模式：
   - 根据需求特点选择合适的分割粒度
4. 查看分割预览（可选）
5. 点击"开始批量评估"
6. 观察实时进度
7. 查看分析结果和片段详情

## 注意事项

1. 批量分析适用于较长的需求文本（建议超过 500 字符）
2. 流式分析需要浏览器支持 EventSource
3. 去重逻辑基于功能点类型和名称匹配
4. 每个功能点会记录其来源片段信息
