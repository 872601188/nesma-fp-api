#!/usr/bin/env python3
"""
NESMA 需求分析器
分析需求文本，识别 ILF/EIF/EI/EO/EQ
"""

import re
from typing import List, Dict, Any

class NesmaAnalyzer:
    """NESMA 功能点分析器"""
    
    # 功能类型定义
    FUNCTION_TYPES = {
        'ILF': '内部逻辑文件',
        'EIF': '外部接口文件', 
        'EI': '外部输入',
        'EO': '外部输出',
        'EQ': '外部查询'
    }
    
    # 复杂度关键词
    COMPLEXITY_KEYWORDS = {
        '高': ['复杂', '大量', '多表', '多条件', '计算', '统计', '报表', '分析', '复杂逻辑', '多步骤'],
        '低': ['简单', '少量', '单表', '单条件', '直接', '简单查询', '列表', '基础']
    }
    
    def __init__(self):
        self.patterns = self._init_patterns()
    
    def _init_patterns(self) -> Dict[str, List[re.Pattern]]:
        """初始化识别模式"""
        return {
            'ILF': [
                re.compile(r'(\w+)[表库](?:\s*存储|\s*管理|\s*维护|\s*包含)?', re.IGNORECASE),
                re.compile(r'(\w+)(?:数据|信息)(?:\s*存储|\s*维护)', re.IGNORECASE),
                re.compile(r'维护(\w+)(?:数据|信息|记录)', re.IGNORECASE),
                re.compile(r'(\w+)(?:档案|资料)(?:\s*管理)', re.IGNORECASE),
            ],
            'EIF': [
                re.compile(r'(?:接口|对接|调用|获取|同步)\s*(\w+)(?:数据|信息)?', re.IGNORECASE),
                re.compile(r'(?:从|通过)\s*(\w+)(?:系统|平台|接口)', re.IGNORECASE),
                re.compile(r'外部\s*(\w+)(?:数据|信息|接口)', re.IGNORECASE),
                re.compile(r'(\w+)(?:API|接口|服务)(?:\s*调用)?', re.IGNORECASE),
            ],
            'EI': [
                re.compile(r'(\w+)(?:录入|输入|新增|添加|创建|导入|上传)', re.IGNORECASE),
                re.compile(r'(?:录入|输入|新增|添加|创建|导入|上传)\s*(\w+)', re.IGNORECASE),
                re.compile(r'(\w+)(?:提交|保存|注册|登记)', re.IGNORECASE),
            ],
            'EO': [
                re.compile(r'(?:导出|输出|生成|打印|发送)\s*(\w+)(?:报表|报告|文件|数据)?', re.IGNORECASE),
                re.compile(r'(\w+)(?:报表|报告|统计|分析)(?:\s*生成|\s*导出)?', re.IGNORECASE),
                re.compile(r'(?:生成|导出)\s*(\w+)(?:报表|报告|统计)', re.IGNORECASE),
            ],
            'EQ': [
                re.compile(r'(\w+)(?:查询|检索|查找|搜索|查看|列表|详情)', re.IGNORECASE),
                re.compile(r'(?:查询|检索|查找|搜索|查看)\s*(\w+)', re.IGNORECASE),
                re.compile(r'(\w+)(?:列表|明细|详情页)', re.IGNORECASE),
            ]
        }
    
    def analyze(self, requirement_text: str) -> Dict[str, Any]:
        """
        分析需求文本，识别功能点
        
        Args:
            requirement_text: 需求文本
            
        Returns:
            分析结果，包含识别出的功能点列表
        """
        functions = []
        
        # 按行分析
        lines = requirement_text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            # 识别各类型功能
            for fp_type, patterns in self.patterns.items():
                for pattern in patterns:
                    matches = pattern.finditer(line)
                    for match in matches:
                        func_name = match.group(1) if match.groups() else ''
                        if func_name:
                            func_desc = self._extract_description(line, func_name)
                            complexity = self._determine_complexity(line, fp_type)
                            
                            function = {
                                'id': f"{fp_type}_{len(functions)+1}",
                                'module': self._extract_module(line, lines, line_num),
                                'description': func_desc,
                                'type': fp_type,
                                'type_name': self.FUNCTION_TYPES[fp_type],
                                'complexity': complexity,
                                'line': line_num,
                                'raw_text': line[:100]
                            }
                            
                            # 去重检查
                            if not self._is_duplicate(function, functions):
                                functions.append(function)
        
        # 统计
        stats = self._calculate_stats(functions)
        
        return {
            'functions': functions,
            'stats': stats,
            'total_lines': len(lines),
            'analyzed_lines': len([l for l in lines if l.strip()])
        }
    
    def _extract_description(self, line: str, func_name: str) -> str:
        """提取功能描述"""
        # 尝试提取更完整的描述
        desc = line.strip()
        # 移除常见的列表标记
        desc = re.sub(r'^[-*•・]\s*', '', desc)
        desc = re.sub(r'^\d+[.、]\s*', '', desc)
        return desc[:80]
    
    def _extract_module(self, line: str, lines: List[str], current_line: int) -> str:
        """提取所属模块"""
        # 向上查找模块标题
        for i in range(current_line - 2, max(0, current_line - 10), -1):
            prev_line = lines[i].strip()
            # 模块标题特征
            if re.match(r'^[#【](.+)[#】]$', prev_line):
                match = re.match(r'^[#【](.+)[#】]$', prev_line)
                return match.group(1)
            if re.match(r'^(模块|功能模块|系统模块)[：:]', prev_line):
                return re.sub(r'^(模块|功能模块|系统模块)[：:]\s*', '', prev_line)
            if prev_line.endswith('模块') or prev_line.endswith('管理'):
                if len(prev_line) < 20:
                    return prev_line
        
        # 从当前行提取关键词作为模块
        module_keywords = ['用户', '订单', '商品', '支付', '库存', '报表', '系统', '管理']
        for keyword in module_keywords:
            if keyword in line:
                return keyword + '管理'
        
        return '通用模块'
    
    def _determine_complexity(self, line: str, fp_type: str) -> str:
        """确定复杂度"""
        line_lower = line.lower()
        
        # 检查高复杂度关键词
        for keyword in self.COMPLEXITY_KEYWORDS['高']:
            if keyword in line_lower:
                return '高'
        
        # 检查低复杂度关键词
        for keyword in self.COMPLEXITY_KEYWORDS['低']:
            if keyword in line_lower:
                return '低'
        
        # 默认中等复杂度
        return '中'
    
    def _is_duplicate(self, function: Dict, functions: List[Dict]) -> bool:
        """检查是否重复"""
        for existing in functions:
            if (existing['type'] == function['type'] and 
                existing['description'] == function['description']):
                return True
        return False
    
    def _calculate_stats(self, functions: List[Dict]) -> Dict:
        """计算统计信息"""
        stats = {
            'total': len(functions),
            'by_type': {fp_type: 0 for fp_type in self.FUNCTION_TYPES.keys()},
            'by_complexity': {'低': 0, '中': 0, '高': 0}
        }
        
        for func in functions:
            stats['by_type'][func['type']] += 1
            stats['by_complexity'][func['complexity']] += 1
        
        return stats


# 便捷函数
def analyze_requirements(requirement_text: str) -> Dict[str, Any]:
    """分析需求文本的便捷函数"""
    analyzer = NesmaAnalyzer()
    return analyzer.analyze(requirement_text)


if __name__ == '__main__':
    # 测试示例
    test_requirement = """
# 电商系统需求

## 用户管理模块
1. 用户注册功能，收集用户基本信息
2. 用户登录验证
3. 用户信息维护
4. 用户权限管理

## 商品管理模块  
- 商品表维护，包含商品基本信息、价格、库存
- 商品分类管理
- 商品图片上传
- 商品库存查询

## 订单管理模块
- 订单创建，包含商品选择、地址填写
- 订单查询和列表展示
- 订单状态更新
- 导出订单报表，包含统计信息

## 支付模块
- 调用支付宝接口完成支付
- 调用微信支付接口
- 支付记录查询
"""
    
    result = analyze_requirements(test_requirement)
    print(f"识别到 {result['stats']['total']} 个功能点:")
    for func in result['functions']:
        print(f"  [{func['type']}] {func['description']} - 复杂度:{func['complexity']}")
