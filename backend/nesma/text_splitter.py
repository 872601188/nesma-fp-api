"""
文本分割器 - 支持句子、段落、篇章三种分割模式
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class TextSegment:
    """文本片段"""
    index: int                    # 片段序号
    content: str                  # 片段内容
    segment_type: str             # 片段类型：sentence/paragraph/chapter
    start_pos: int               # 起始位置
    end_pos: int                 # 结束位置
    metadata: Dict[str, Any]     # 元数据（如：段落编号、章节标题等）


class TextSplitter:
    """文本分割器"""
    
    def __init__(self):
        # 中文句子结束符
        self.sentence_endings = r'[。！？；.!?;]+'
        # 段落分隔符
        self.paragraph_endings = r'\n\s*\n|\r\n\s*\r\n'
        # 章节分隔符（常见的章节标题模式）
        self.chapter_patterns = [
            r'(?:^|\n)\s*第[一二三四五六七八九十零百千\d]+章[\s:：]+',  # 第一章、第1章
            r'(?:^|\n)\s*第[一二三四五六七八九十零百千\d]+节[\s:：]+',  # 第一节、第1节
            r'(?:^|\n)\s*[\d]+[.．、]\s*',                           # 1. 1． 1、
            r'(?:^|\n)\s*[（(][\d一二三四五六七八九十]+[)）][\s:：]+',  # （一）(一)
            r'(?:^|\n)\s*\d+\s*[.、]\d+\s*',                        # 1.1、1.1 
        ]
    
    def split(self, text: str, mode: str = "sentence") -> List[TextSegment]:
        """
        根据模式分割文本
        
        Args:
            text: 原始文本
            mode: 分割模式 - sentence(句子)/paragraph(段落)/chapter(篇章)
        
        Returns:
            TextSegment列表
        """
        if mode == "sentence":
            return self._split_by_sentence(text)
        elif mode == "paragraph":
            return self._split_by_paragraph(text)
        elif mode == "chapter":
            return self._split_by_chapter(text)
        else:
            raise ValueError(f"不支持的分割模式: {mode}")
    
    def _split_by_sentence(self, text: str) -> List[TextSegment]:
        """按句子分割"""
        segments = []
        
        # 先按句子结束符分割
        raw_sentences = re.split(f'({self.sentence_endings})', text)
        
        current_pos = 0
        index = 0
        buffer = ""
        
        for part in raw_sentences:
            buffer += part
            # 如果包含结束符，则形成完整句子
            if re.match(self.sentence_endings, part):
                content = buffer.strip()
                if content and len(content) > 3:  # 过滤太短的片段
                    segments.append(TextSegment(
                        index=index,
                        content=content,
                        segment_type="sentence",
                        start_pos=current_pos,
                        end_pos=current_pos + len(buffer),
                        metadata={"length": len(content)}
                    ))
                    index += 1
                current_pos += len(buffer)
                buffer = ""
        
        # 处理剩余内容
        if buffer.strip() and len(buffer.strip()) > 3:
            segments.append(TextSegment(
                index=index,
                content=buffer.strip(),
                segment_type="sentence",
                start_pos=current_pos,
                end_pos=current_pos + len(buffer),
                metadata={"length": len(buffer)}
            ))
        
        return segments
    
    def _split_by_paragraph(self, text: str) -> List[TextSegment]:
        """按段落分割"""
        segments = []
        
        # 按段落分隔符分割
        raw_paragraphs = re.split(self.paragraph_endings, text)
        
        current_pos = 0
        for index, para in enumerate(raw_paragraphs):
            para = para.strip()
            # 过滤空段落和太短的段落
            if para and len(para) > 10:
                # 计算在原文中的位置
                start_pos = text.find(para, current_pos)
                end_pos = start_pos + len(para)
                
                segments.append(TextSegment(
                    index=index,
                    content=para,
                    segment_type="paragraph",
                    start_pos=start_pos,
                    end_pos=end_pos,
                    metadata={
                        "length": len(para),
                        "line_count": para.count('\n') + 1
                    }
                ))
                current_pos = end_pos
        
        return segments
    
    def _split_by_chapter(self, text: str) -> List[TextSegment]:
        """按篇章/章节分割"""
        segments = []
        
        # 合并所有章节模式
        chapter_regex = '|'.join(f'({p})' for p in self.chapter_patterns)
        
        # 查找所有章节标题位置
        matches = list(re.finditer(chapter_regex, text))
        
        if len(matches) <= 1:
            # 如果没有章节标题或只有一个，则整个文本作为一章
            segments.append(TextSegment(
                index=0,
                content=text.strip(),
                segment_type="chapter",
                start_pos=0,
                end_pos=len(text),
                metadata={
                    "title": "全文",
                    "length": len(text),
                    "is_full_text": True
                }
            ))
        else:
            # 按章节分割
            for i, match in enumerate(matches):
                start_pos = match.start()
                title = match.group().strip()
                
                # 确定章节结束位置
                if i < len(matches) - 1:
                    end_pos = matches[i + 1].start()
                else:
                    end_pos = len(text)
                
                content = text[start_pos:end_pos].strip()
                
                # 提取正文内容（去掉标题）
                body_content = text[match.end():end_pos].strip()
                
                if content:
                    segments.append(TextSegment(
                        index=i,
                        content=content,
                        segment_type="chapter",
                        start_pos=start_pos,
                        end_pos=end_pos,
                        metadata={
                            "title": title,
                            "body": body_content,
                            "length": len(content),
                            "is_full_text": False
                        }
                    ))
        
        return segments
    
    def get_segment_summary(self, segments: List[TextSegment]) -> Dict[str, Any]:
        """获取分割结果摘要"""
        if not segments:
            return {"count": 0, "total_length": 0, "type": None}
        
        total_length = sum(s.metadata.get("length", len(s.content)) for s in segments)
        avg_length = total_length / len(segments)
        
        return {
            "count": len(segments),
            "total_length": total_length,
            "average_length": round(avg_length, 1),
            "type": segments[0].segment_type if segments else None,
            "min_length": min(s.metadata.get("length", len(s.content)) for s in segments),
            "max_length": max(s.metadata.get("length", len(s.content)) for s in segments)
        }


# 便捷函数
def split_text(text: str, mode: str = "sentence") -> List[TextSegment]:
    """便捷函数：分割文本"""
    splitter = TextSplitter()
    return splitter.split(text, mode)
