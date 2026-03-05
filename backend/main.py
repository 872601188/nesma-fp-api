from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Literal
import uvicorn
import json
import asyncio

from nesma.analyzer import RequirementAnalyzer
from nesma.calculator import FunctionPointCalculator
from nesma.excel_generator import ExcelGenerator
from nesma.batch_analyzer import BatchAnalyzer

app = FastAPI(
    title="NESMA 功能点分析 API",
    description="支持分批分析的 NESMA 功能点分析 API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class RequirementInput(BaseModel):
    text: str
    project_name: Optional[str] = "未命名项目"


class BatchAnalysisInput(BaseModel):
    text: str
    project_name: Optional[str] = "未命名项目"
    split_mode: Literal["sentence", "paragraph", "chapter"] = "sentence"


class SplitPreviewInput(BaseModel):
    text: str
    mode: Literal["sentence", "paragraph", "chapter"] = "sentence"


class FunctionPoint(BaseModel):
    type: str  # ILF, EIF, EI, EO, EQ
    name: str
    complexity: str  # Low, Average, High
    count: int


class CalculationResult(BaseModel):
    project_name: str
    original_requirements: str  # 原始需求内容
    function_points: List[FunctionPoint]
    total_unadjusted_fp: float
    adjusted_fp: float
    vaf: float  # Value Adjustment Factor
    details: dict


# Initialize components
analyzer = RequirementAnalyzer()
calculator = FunctionPointCalculator()
excel_gen = ExcelGenerator()
batch_analyzer = BatchAnalyzer()


@app.get("/")
def read_root():
    return {
        "message": "NESMA 功能点分析 API",
        "version": "2.0.0",
        "features": ["单文本分析", "批量分段分析", "流式进度"],
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/analyze", response_model=CalculationResult)
def analyze_requirements(input_data: RequirementInput):
    """传统方式：分析需求文本并计算功能点（不分段）"""
    try:
        # Analyze requirements
        components = analyzer.analyze(input_data.text)
        
        # Calculate function points
        result = calculator.calculate(components)
        
        return CalculationResult(
            project_name=input_data.project_name,
            original_requirements=input_data.text,
            function_points=result["function_points"],
            total_unadjusted_fp=result["total_unadjusted_fp"],
            adjusted_fp=result["adjusted_fp"],
            vaf=result["vaf"],
            details=result["details"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...), project_name: Optional[str] = "未命名项目"):
    """上传并分析需求文件"""
    try:
        content = await file.read()
        text = content.decode("utf-8")
        
        components = analyzer.analyze(text)
        result = calculator.calculate(components)
        
        return CalculationResult(
            project_name=project_name,
            original_requirements=text,
            function_points=result["function_points"],
            total_unadjusted_fp=result["total_unadjusted_fp"],
            adjusted_fp=result["adjusted_fp"],
            vaf=result["vaf"],
            details=result["details"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
def analyze_batch(input_data: BatchAnalysisInput):
    """
    批量分析（非流式）- 按句子/段落/篇章分割后分别识别，最后汇总
    
    - **sentence**: 按句子分割，逐句识别功能点
    - **paragraph**: 按段落分割，逐段识别功能点
    - **chapter**: 按篇章/章节分割，逐章识别功能点
    """
    try:
        result = batch_analyzer.analyze_sync(
            text=input_data.text,
            project_name=input_data.project_name,
            split_mode=input_data.split_mode
        )
        
        return {
            "project_name": result.project_name,
            "split_mode": result.split_mode,
            "total_segments": result.total_segments,
            "processed_segments": result.processed_segments,
            "function_points": result.all_function_points,
            "total_unadjusted_fp": result.total_unadjusted_fp,
            "adjusted_fp": result.adjusted_fp,
            "vaf": result.vaf,
            "component_counts": result.component_counts,
            "segment_results": [
                {
                    "index": sr.segment.index,
                    "type": sr.segment.segment_type,
                    "content_preview": sr.segment.content[:100] + "..." if len(sr.segment.content) > 100 else sr.segment.content,
                    "status": sr.status,
                    "found_components": {k: len(v) for k, v in sr.components.items()}
                }
                for sr in result.segment_results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch/stream")
async def analyze_batch_stream(input_data: BatchAnalysisInput):
    """
    批量分析（流式）- 实时返回每个片段的分析进度和结果
    
    返回 SSE 流，事件类型：
    - `split_complete`: 文本分割完成
    - `segment_complete`: 单个片段分析完成
    - `segment_error`: 单个片段分析出错
    - `complete`: 全部完成，返回最终结果
    """
    async def event_generator():
        try:
            async for event in batch_analyzer.analyze_stream(
                text=input_data.text,
                project_name=input_data.project_name,
                split_mode=input_data.split_mode
            ):
                # 格式化为 SSE 格式
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )


@app.post("/analyze/preview")
def get_split_preview(input_data: SplitPreviewInput):
    """
    获取文本分割预览 - 在实际分析前预览分割结果
    
    帮助用户选择最合适的分割模式
    """
    try:
        preview = batch_analyzer.get_split_preview(input_data.text, input_data.mode)
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export-excel")
def export_excel(result: CalculationResult):
    """将计算结果导出为 Excel 文件"""
    try:
        file_path = excel_gen.generate(result.dict())
        return {
            "message": "Excel 文件生成成功",
            "download_url": f"/download/{file_path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nesma/complexity-table")
def get_complexity_table():
    """获取 NESMA 复杂度权重表"""
    return {
        "ILF": {"低": 7, "中": 10, "高": 15},
        "EIF": {"低": 5, "中": 7, "高": 10},
        "EI": {"低": 3, "中": 4, "高": 6},
        "EO": {"低": 4, "中": 5, "高": 7},
        "EQ": {"低": 3, "中": 4, "高": 6}
    }


@app.get("/nesma/gsc-factors")
def get_gsc_factors():
    """获取通用系统特性 (GSC) 因子"""
    return {
        "factors": [
            {"id": 1, "name": "数据通信", "description": "系统有多少通信设施？"},
            {"id": 2, "name": "分布式数据处理", "description": "分布式数据和处理功能如何处理？"},
            {"id": 3, "name": "性能", "description": "用户是否要求响应时间或吞吐量？"},
            {"id": 4, "name": "高使用配置", "description": "当前硬件平台的使用程度如何？"},
            {"id": 5, "name": "事务率", "description": "事务执行的频率如何？"},
            {"id": 6, "name": "在线数据输入", "description": "有多少百分比的信息是在线输入的？"},
            {"id": 7, "name": "终端用户效率", "description": "应用是否专为终端用户效率而设计？"},
            {"id": 8, "name": "在线更新", "description": "有多少内部逻辑文件由在线事务更新？"},
            {"id": 9, "name": "复杂处理", "description": "应用是否具有复杂处理？"},
            {"id": 10, "name": "可重用性", "description": "应用是否为一个或多个用户需求而开发？"},
            {"id": 11, "name": "安装易用性", "description": "转换和安装有多困难？"},
            {"id": 12, "name": "操作易用性", "description": "启动、备份和恢复的效果如何？"},
            {"id": 13, "name": "多站点", "description": "应用是否设计用于多个站点？"},
            {"id": 14, "name": "促进变更", "description": "应用是否设计为促进变更？"}
        ]
    }


@app.get("/split-modes")
def get_split_modes():
    """获取支持的分割模式说明"""
    return {
        "modes": [
            {
                "id": "sentence",
                "name": "按句子",
                "description": "将文本按句子分割，适合细粒度识别，每个句子单独分析",
                "use_case": "适用于需求描述详细、每句话对应一个独立功能的场景",
                "icon": "📝"
            },
            {
                "id": "paragraph",
                "name": "按段落",
                "description": "将文本按段落分割，适合中等粒度识别",
                "use_case": "适用于需求按段落组织，每段描述一个功能模块的场景",
                "icon": "📄"
            },
            {
                "id": "chapter",
                "name": "按篇章",
                "description": "将文本按章节分割，适合粗粒度识别",
                "use_case": "适用于大型需求文档，按章节组织不同功能域的场景",
                "icon": "📚"
            }
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
