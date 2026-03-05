"""
NESMA 需求分析器
分析软件需求文本以识别功能点组件。
"""

import re
import spacy
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Component:
    type: str  # ILF, EIF, EI, EO, EQ
    name: str
    description: str
    complexity_hints: List[str]

class RequirementAnalyzer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
        
        # 功能点识别模式（中文）
        self.patterns = {
            "EI": {
                "keywords": ["创建", "添加", "新增", "录入", "输入", "提交", "导入", "上传", "注册", "保存", "插入"],
                "action_extract": ["创建", "添加", "新增", "录入", "输入", "提交", "导入", "上传", "注册", "保存", "维护"]
            },
            "EO": {
                "keywords": ["生成", "导出", "报表", "统计", "打印", "发送", "通知", "展示", "显示", "计算"],
                "action_extract": ["生成", "导出", "统计", "打印", "发送", "通知", "展示", "显示", "计算"]
            },
            "EQ": {
                "keywords": ["查询", "搜索", "查看", "浏览", "检索", "获取", "查找", "筛选", "列表", "详情"],
                "action_extract": ["查询", "搜索", "查看", "浏览", "检索", "获取", "查找", "筛选"]
            },
            "ILF": {
                "keywords": ["数据", "表", "文件", "记录", "信息", "档案", "库"],
                "action_extract": ["数据", "信息", "档案"]
            },
            "EIF": {
                "keywords": ["外部", "接口", "导入", "第三方", "系统对接"],
                "action_extract": ["外部", "接口", "第三方"]
            }
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        分析需求文本并识别功能点组件。
        按句子拆分，每个句子识别一个主要功能点。
        """
        sentences = self._split_sentences(text)
        components = {
            "ILF": [],
            "EIF": [],
            "EI": [],
            "EO": [],
            "EQ": []
        }
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 识别该句子中的主要功能点
            comp = self._identify_main_component(sentence)
            if comp:
                comp_type = comp["type"]
                if comp_type in components:
                    components[comp_type].append(comp)
        
        return components
    
    def _split_sentences(self, text: str) -> List[str]:
        """将文本分割成句子，同时拆分包含多个功能的句子。"""
        # 第一步：按标点分句
        raw_sentences = [s.strip() for s in re.split(r'[.!?。！？；;]+', text) if s.strip()]
        
        sentences = []
        for sent in raw_sentences:
            # 第二步：如果句子包含"并"、"和"连接多个动作，尝试拆分
            # 例如："用户可以搜索客户并生成月度报表"
            if '并' in sent or '以及' in sent or '和' in sent:
                sub_sentences = self._split_by_actions(sent)
                sentences.extend(sub_sentences)
            else:
                sentences.append(sent)
        
        return sentences
    
    def _split_by_actions(self, sentence: str) -> List[str]:
        """按动作拆分包含多个功能的句子。"""
        # 所有可能的动作关键词
        all_actions = (
            self.patterns["EI"]["action_extract"] +
            self.patterns["EO"]["action_extract"] +
            self.patterns["EQ"]["action_extract"]
        )
        
        # 查找句子中所有的动作位置
        action_positions = []
        for action in all_actions:
            idx = sentence.find(action)
            if idx >= 0:
                action_positions.append((idx, action))
        
        # 按位置排序
        action_positions.sort(key=lambda x: x[0])
        
        # 如果找到多个动作，按动作拆分
        if len(action_positions) > 1:
            result = []
            for i, (pos, action) in enumerate(action_positions):
                if i < len(action_positions) - 1:
                    # 提取从当前动作到下一个动作之前的内容
                    next_pos = action_positions[i + 1][0]
                    sub_sent = sentence[pos:next_pos].strip()
                    # 去除结尾的连接词
                    sub_sent = re.sub(r'[并,和,以及,、]+$', '', sub_sent).strip()
                    if sub_sent:
                        result.append(sub_sent)
                else:
                    # 最后一个动作到句子结束
                    sub_sent = sentence[pos:].strip()
                    if sub_sent:
                        result.append(sub_sent)
            return result
        
        return [sentence]
    
    def _identify_main_component(self, sentence: str) -> Dict:
        """从单个句子中识别主要功能点（一个句子只识别一个）。"""
        
        # 优先级：ILF > EIF > EI > EO > EQ
        
        # 1. 检查是否是ILF（数据存储相关）
        if self._is_ilm(sentence):
            name = self._extract_function_name(sentence, "ILF")
            return {
                "type": "ILF",
                "name": name,
                "description": sentence,
                "complexity_hints": self._determine_complexity_hints(sentence)
            }
        
        # 2. 检查是否是EIF（外部接口）
        if self._is_eif(sentence):
            name = self._extract_function_name(sentence, "EIF")
            return {
                "type": "EIF",
                "name": name,
                "description": sentence,
                "complexity_hints": self._determine_complexity_hints(sentence)
            }
        
        # 3. 检查EI（输入类）- 最高优先级的事务
        ei_action = self._find_main_action(sentence, self.patterns["EI"]["action_extract"])
        if ei_action:
            return {
                "type": "EI",
                "name": ei_action["name"],
                "description": sentence,
                "complexity_hints": self._determine_complexity_hints(sentence)
            }
        
        # 4. 检查EO（输出类）- 带计算的输出
        eo_action = self._find_main_action(sentence, self.patterns["EO"]["action_extract"])
        if eo_action and self._has_calculation(sentence):
            return {
                "type": "EO",
                "name": eo_action["name"],
                "description": sentence,
                "complexity_hints": self._determine_complexity_hints(sentence)
            }
        
        # 5. 检查EQ（查询类）- 最后优先级
        eq_action = self._find_main_action(sentence, self.patterns["EQ"]["action_extract"])
        if eq_action:
            return {
                "type": "EQ",
                "name": eq_action["name"],
                "description": sentence,
                "complexity_hints": self._determine_complexity_hints(sentence)
            }
        
        return None
    
    def _is_ilm(self, sentence: str) -> bool:
        """判断是否是ILF（内部逻辑文件）。"""
        ilf_keywords = ["数据库", "数据表", "信息库", "档案库", "主数据", "业务数据", "基础数据"]
        return any(kw in sentence for kw in ilf_keywords)
    
    def _is_eif(self, sentence: str) -> bool:
        """判断是否是EIF（外部接口文件）。"""
        eif_keywords = ["外部系统", "第三方", "接口数据", "外部数据库", "异构系统"]
        return any(kw in sentence for kw in eif_keywords)
    
    def _find_main_action(self, sentence: str, action_keywords: List[str]) -> Dict:
        """查找句子中的主要操作行为（返回最重要的一个）。"""
        found_actions = []
        
        for keyword in action_keywords:
            if keyword in sentence:
                # 提取功能名称
                name = self._extract_function_name(sentence, None, keyword)
                if name:
                    # 记录位置和关键词长度（优先匹配位置靠前的，关键词更具体的）
                    pos = sentence.find(keyword)
                    found_actions.append({
                        "keyword": keyword,
                        "name": name,
                        "position": pos,
                        "priority": len(keyword)  # 关键词越长越具体
                    })
        
        if not found_actions:
            return None
        
        # 排序：位置靠前优先，关键词长优先
        found_actions.sort(key=lambda x: (x["position"], -x["priority"]))
        return found_actions[0]
    
    def _extract_function_name(self, sentence: str, comp_type: str = None, action: str = None) -> str:
        """从句子中提取功能点名称。"""
        # 中文规则：对象 + 动作
        # 例如："用户可以查询客户信息" -> "客户信息查询"
        # "系统支持下载党内法规" -> "党内法规下载"
        
        # 去除常见前缀词
        prefixes = ['系统应允许', '系统支持', '用户可以', '用户能够', '提供', '实现', '支持']
        clean_sentence = sentence
        for prefix in prefixes:
            if clean_sentence.startswith(prefix):
                clean_sentence = clean_sentence[len(prefix):]
                break
        
        if action:
            # 找到动作的位置
            idx = clean_sentence.find(action)
            if idx >= 0:
                # 提取动作前的内容作为对象（通常是名词）
                before_action = clean_sentence[:idx].strip()
                # 提取动作后的内容
                after_action = clean_sentence[idx + len(action):].strip()
                
                # 去除停用词
                stop_words = ['用户', '系统', '可以', '能够', '进行', '对', '将', '把', '的']
                for sw in stop_words:
                    before_action = before_action.replace(sw, '')
                    after_action = after_action.replace(sw, '')
                
                before_action = before_action.strip()
                after_action = after_action.strip()
                
                # 组合成功能名称
                if after_action:
                    # 动作 + 对象（如：创建客户记录）
                    obj = after_action[:10] if len(after_action) > 10 else after_action
                    return action + obj
                elif before_action:
                    # 对象 + 动作（如：客户记录创建）
                    obj = before_action[-10:] if len(before_action) > 10 else before_action
                    return obj + action
        
        # 默认返回整句简化版
        clean_sentence = clean_sentence.strip()
        if len(clean_sentence) > 20:
            return clean_sentence[:20]
        return clean_sentence
    
    def _has_calculation(self, sentence: str) -> bool:
        """判断是否包含计算逻辑。"""
        calc_keywords = ["计算", "统计", "汇总", "求和", "平均值", "百分比", "公式", "合计"]
        return any(kw in sentence for kw in calc_keywords)
    
    def _deduplicate(self, components: List[Dict]) -> List[Dict]:
        """去重功能点。"""
        seen = set()
        result = []
        for comp in components:
            key = f"{comp['type']}:{comp['name']}"
            if key not in seen:
                seen.add(key)
                result.append(comp)
        return result
    
    def _determine_complexity_hints(self, sentence: str) -> List[str]:
        """根据句子内容确定复杂度提示。"""
        hints = []
        
        # 复杂度指示词（中文）
        if any(kw in sentence for kw in ["多个", "各种", "不同", "多种", "批量"]):
            hints.append("multiple_data_elements")
        
        if any(kw in sentence for kw in ["复杂", "繁琐", "高级", "多步骤"]):
            hints.append("complex_processing")
        
        if any(kw in sentence for kw in ["简单", "基础", "标准", "单一"]):
            hints.append("simple_processing")
        
        if any(kw in sentence for kw in ["大量", "很多", "许多", "海量"]):
            hints.append("high_volume")
        
        if any(kw in sentence for kw in ["验证", "校验", "检查", "审核"]):
            hints.append("validation_required")
        
        if any(kw in sentence for kw in ["计算", "公式", "运算", "统计", "汇总"]):
            hints.append("calculation_required")
        
        return hints
