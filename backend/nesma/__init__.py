"""
NESMA Function Point Analysis Package

包含以下模块：
- analyzer: 需求分析器
- calculator: 功能点计算器
- excel_generator: Excel报告生成器
- text_splitter: 文本分割器
- batch_analyzer: 批量分析器
"""

from .analyzer import RequirementAnalyzer, Component
from .calculator import FunctionPointCalculator
from .excel_generator import ExcelGenerator
from .text_splitter import TextSplitter, TextSegment, split_text
from .batch_analyzer import BatchAnalyzer, BatchAnalysisResult, SegmentAnalysisResult

__all__ = [
    'RequirementAnalyzer',
    'Component',
    'FunctionPointCalculator',
    'ExcelGenerator',
    'TextSplitter',
    'TextSegment',
    'split_text',
    'BatchAnalyzer',
    'BatchAnalysisResult',
    'SegmentAnalysisResult',
]
