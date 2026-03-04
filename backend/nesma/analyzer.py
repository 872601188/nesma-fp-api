import re
from typing import List, Dict, Any

class NESMAAnalyzer:
    KEYWORDS = {
        'ILF': ['表', '数据库', '数据', '信息', '记录', '档案', '台账', '用户', '订单', '商品', '产品', '客户', '会员', '账户', '库存', '仓库', '物料', '资产', '配置', '参数', '设置'],
        'EIF': ['接口', '对接', '同步', '第三方', '外部系统', '支付', '支付宝', '微信', '短信', '邮件', '推送', '地图', '定位', '认证', 'ERP', 'CRM', 'OA'],
        'EI': ['新增', '添加', '创建', '录入', '导入', '修改', '编辑', '更新', '变更', '删除', '移除', '提交', '保存', '确认', '审核', '上传'],
        'EO': ['导出', '下载', '报表', '统计', '分析', '图表', '打印', '输出', '生成', '计算', '汇总', '排名', '对比', 'PDF', 'Excel'],
        'EQ': ['查询', '查看', '列表', '详情', '搜索', '筛选', '检索', '查找', '浏览', '展示', '显示', '分页', '排序']
    }
    
    def __init__(self):
        self.results = []
    
    def analyze(self, requirement_text: str) -> Dict[str, Any]:
        self.results = []
        sentences = re.split(r'[。；;\n]', requirement_text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            self._identify_data_functions(sentence)
            self._identify_transactional_functions(sentence)
        
        self._deduplicate()
        return {'functions': self.results, 'summary': self._generate_summary()}
    
    def _identify_data_functions(self, sentence: str):
        for keyword in self.KEYWORDS['EIF']:
            if keyword in sentence:
                self._add_function(sentence, keyword, 'EIF')
                return
        for keyword in self.KEYWORDS['ILF']:
            if keyword in sentence:
                self._add_function(sentence, keyword, 'ILF')
                return
    
    def _identify_transactional_functions(self, sentence: str):
        for keyword in self.KEYWORDS['EI']:
            if keyword in sentence:
                self._add_function(sentence, keyword, 'EI')
                return
        for keyword in self.KEYWORDS['EO']:
            if keyword in sentence:
                self._add_function(sentence, keyword, 'EO')
                return
        for keyword in self.KEYWORDS['EQ']:
            if keyword in sentence:
                self._add_function(sentence, keyword, 'EQ')
                return
    
    def _add_function(self, sentence: str, keyword: str, func_type: str):
        if not any(f['type'] == func_type and keyword in f['description'] for f in self.results):
            self.results.append({
                'module': '通用模块',
                'description': sentence[:50] + '...' if len(sentence) > 50 else sentence,
                'type': func_type,
                'complexity': '中',
                'source_sentence': sentence
            })
    
    def _deduplicate(self):
        seen = set()
        unique = []
        for f in self.results:
            key = (f['description'], f['type'])
            if key not in seen:
                seen.add(key)
                unique.append(f)
        self.results = unique
    
    def _generate_summary(self) -> Dict[str, int]:
        summary = {'ILF': 0, 'EIF': 0, 'EI': 0, 'EO': 0, 'EQ': 0, 'total': 0}
        for f in self.results:
            summary[f['type']] = summary.get(f['type'], 0) + 1
            summary['total'] += 1
        return summary
