"""
批量分析器 - 支持分批分析文本片段并汇总结果
"""

import asyncio
from typing import List, Dict, Any, AsyncGenerator, Optional
from dataclasses import dataclass, field
from .text_splitter import TextSplitter, TextSegment
from .analyzer import RequirementAnalyzer
from .calculator import FunctionPointCalculator


@dataclass
class SegmentAnalysisResult:
    """单个片段的分析结果"""
    segment: TextSegment           # 原始片段
    components: Dict[str, List]    # 识别的组件
    status: str                    # 状态: success/error/processing
    error_message: str = ""        # 错误信息


@dataclass
class BatchAnalysisResult:
    """批量分析的最终结果"""
    project_name: str
    split_mode: str                # 分割模式
    total_segments: int            # 总片段数
    processed_segments: int        # 已处理片段数
    all_function_points: List[Dict] = field(default_factory=list)
    segment_results: List[SegmentAnalysisResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    # 计算结果
    total_unadjusted_fp: float = 0
    adjusted_fp: float = 0
    vaf: float = 1.0
    
    # 统计
    component_counts: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.component_counts:
            self.component_counts = {"ILF": 0, "EIF": 0, "EI": 0, "EO": 0, "EQ": 0}


class BatchAnalyzer:
    """批量分析器"""
    
    def __init__(self):
        self.splitter = TextSplitter()
        self.analyzer = RequirementAnalyzer()
        self.calculator = FunctionPointCalculator()
    
    async def analyze_stream(
        self,
        text: str,
        project_name: str,
        split_mode: str = "sentence",
        progress_callback: Optional[callable] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式分析 - 逐个片段分析并返回进度
        
        Yields:
            {
                "type": "progress" | "segment_result" | "complete",
                "data": {...}
            }
        """
        # 1. 分割文本
        segments = self.splitter.split(text, split_mode)
        summary = self.splitter.get_segment_summary(segments)
        
        total_segments = len(segments)
        
        # 发送分割完成消息
        yield {
            "type": "split_complete",
            "data": {
                "mode": split_mode,
                "total_segments": total_segments,
                "summary": summary
            }
        }
        
        # 2. 逐个分析片段
        batch_result = BatchAnalysisResult(
            project_name=project_name,
            split_mode=split_mode,
            total_segments=total_segments,
            processed_segments=0
        )
        
        all_components = {
            "ILF": [], "EIF": [], "EI": [], "EO": [], "EQ": []
        }
        
        for i, segment in enumerate(segments):
            try:
                # 分析当前片段
                components = self.analyzer.analyze(segment.content)
                
                # 记录结果
                segment_result = SegmentAnalysisResult(
                    segment=segment,
                    components=components,
                    status="success"
                )
                batch_result.segment_results.append(segment_result)
                
                # 合并组件
                for comp_type, items in components.items():
                    # 添加来源信息
                    for item in items:
                        item["source_segment_index"] = segment.index
                        item["source_segment_type"] = segment.segment_type
                        item["source_segment_preview"] = segment.content[:50] + "..." if len(segment.content) > 50 else segment.content
                    all_components[comp_type].extend(items)
                
                # 发送片段分析完成消息
                yield {
                    "type": "segment_complete",
                    "data": {
                        "index": i + 1,
                        "total": total_segments,
                        "segment": {
                            "index": segment.index,
                            "type": segment.segment_type,
                            "content_preview": segment.content[:100] + "..." if len(segment.content) > 100 else segment.content,
                            "metadata": segment.metadata
                        },
                        "found_components": {
                            k: len(v) for k, v in components.items() if v
                        }
                    }
                }
                
            except Exception as e:
                # 记录错误
                segment_result = SegmentAnalysisResult(
                    segment=segment,
                    components={},
                    status="error",
                    error_message=str(e)
                )
                batch_result.segment_results.append(segment_result)
                
                yield {
                    "type": "segment_error",
                    "data": {
                        "index": i + 1,
                        "total": total_segments,
                        "error": str(e)
                    }
                }
            
            batch_result.processed_segments = i + 1
            
            # 模拟处理延迟，便于前端展示进度
            await asyncio.sleep(0.1)
        
        # 3. 计算总功能点
        calc_result = self.calculator.calculate(all_components)
        
        # 去重处理 - 基于类型和名称
        unique_fp = self._deduplicate_function_points(calc_result["function_points"])
        
        # 更新最终结果
        batch_result.all_function_points = unique_fp
        batch_result.total_unadjusted_fp = sum(fp["count"] for fp in unique_fp)
        batch_result.adjusted_fp = round(batch_result.total_unadjusted_fp * calc_result["vaf"], 2)
        batch_result.vaf = calc_result["vaf"]
        batch_result.component_counts = calc_result["details"]["component_counts"]
        
        # 统计各片段的贡献
        segment_contributions = self._calculate_segment_contributions(
            batch_result.segment_results, unique_fp
        )
        
        # 发送完成消息
        yield {
            "type": "complete",
            "data": {
                "project_name": project_name,
                "split_mode": split_mode,
                "total_segments": total_segments,
                "processed_segments": batch_result.processed_segments,
                "function_points": unique_fp,
                "total_unadjusted_fp": batch_result.total_unadjusted_fp,
                "adjusted_fp": batch_result.adjusted_fp,
                "vaf": batch_result.vaf,
                "component_counts": batch_result.component_counts,
                "segment_contributions": segment_contributions,
                "complexity_distribution": calc_result["details"]["complexity_distribution"]
            }
        }
    
    def analyze_sync(
        self,
        text: str,
        project_name: str,
        split_mode: str = "sentence"
    ) -> BatchAnalysisResult:
        """
        同步批量分析（非流式）
        """
        # 1. 分割文本
        segments = self.splitter.split(text, split_mode)
        
        # 2. 逐个分析
        batch_result = BatchAnalysisResult(
            project_name=project_name,
            split_mode=split_mode,
            total_segments=len(segments),
            processed_segments=0
        )
        
        all_components = {
            "ILF": [], "EIF": [], "EI": [], "EO": [], "EQ": []
        }
        
        for segment in segments:
            try:
                components = self.analyzer.analyze(segment.content)
                
                segment_result = SegmentAnalysisResult(
                    segment=segment,
                    components=components,
                    status="success"
                )
                batch_result.segment_results.append(segment_result)
                
                # 合并组件，添加来源信息
                for comp_type, items in components.items():
                    for item in items:
                        item["source_segment_index"] = segment.index
                        item["source_segment_type"] = segment.segment_type
                    all_components[comp_type].extend(items)
                    
            except Exception as e:
                batch_result.segment_results.append(SegmentAnalysisResult(
                    segment=segment,
                    components={},
                    status="error",
                    error_message=str(e)
                ))
        
        batch_result.processed_segments = len(segments)
        
        # 3. 计算总功能点
        calc_result = self.calculator.calculate(all_components)
        unique_fp = self._deduplicate_function_points(calc_result["function_points"])
        
        batch_result.all_function_points = unique_fp
        batch_result.total_unadjusted_fp = sum(fp["count"] for fp in unique_fp)
        batch_result.adjusted_fp = round(batch_result.total_unadjusted_fp * calc_result["vaf"], 2)
        batch_result.vaf = calc_result["vaf"]
        batch_result.component_counts = calc_result["details"]["component_counts"]
        
        return batch_result
    
    def _deduplicate_function_points(self, function_points: List[Dict]) -> List[Dict]:
        """去重功能点 - 基于类型和名称的相似度"""
        seen = {}
        unique = []
        
        for fp in function_points:
            # 创建唯一键
            key = f"{fp['type']}:{fp['name']}"
            
            # 如果已存在，合并来源信息
            if key in seen:
                existing = seen[key]
                # 保留最高复杂度
                if fp.get("complexity") == "High" and existing.get("complexity") != "High":
                    existing["complexity"] = "High"
                    existing["count"] = fp["count"]
                # 合并来源片段信息
                if "sources" not in existing:
                    existing["sources"] = [{
                        "segment_index": existing.get("source_segment_index", 0),
                        "segment_type": existing.get("source_segment_type", "unknown"),
                        "preview": existing.get("source_segment_preview", "")
                    }]
                existing["sources"].append({
                    "segment_index": fp.get("source_segment_index", 0),
                    "segment_type": fp.get("source_segment_type", "unknown"),
                    "preview": fp.get("source_segment_preview", "")
                })
            else:
                fp_copy = fp.copy()
                fp_copy["sources"] = [{
                    "segment_index": fp.get("source_segment_index", 0),
                    "segment_type": fp.get("source_segment_type", "unknown"),
                    "preview": fp.get("source_segment_preview", "")
                }]
                seen[key] = fp_copy
                unique.append(fp_copy)
        
        return unique
    
    def _calculate_segment_contributions(
        self,
        segment_results: List[SegmentAnalysisResult],
        function_points: List[Dict]
    ) -> List[Dict]:
        """计算每个片段的贡献统计"""
        contributions = []
        
        for sr in segment_results:
            # 统计该片段识别的功能点数量
            found_count = sum(len(items) for items in sr.components.values())
            
            contributions.append({
                "index": sr.segment.index,
                "type": sr.segment.segment_type,
                "content_preview": sr.segment.content[:80] + "..." if len(sr.segment.content) > 80 else sr.segment.content,
                "status": sr.status,
                "found_components": found_count
            })
        
        return contributions
    
    def get_split_preview(self, text: str, mode: str) -> Dict[str, Any]:
        """获取分割预览"""
        segments = self.splitter.split(text, mode)
        summary = self.splitter.get_segment_summary(segments)
        
        return {
            "mode": mode,
            "summary": summary,
            "segments": [
                {
                    "index": s.index,
                    "content_preview": s.content[:200] + "..." if len(s.content) > 200 else s.content,
                    "length": len(s.content),
                    "metadata": s.metadata
                }
                for s in segments[:10]  # 只返回前10个预览
            ],
            "has_more": len(segments) > 10
        }
