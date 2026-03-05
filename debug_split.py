import re

# 所有可能的动作关键词
ei_actions = ["创建", "添加", "新增", "录入", "输入", "提交", "导入", "上传", "注册", "保存", "维护"]
eo_actions = ["生成", "导出", "统计", "打印", "发送", "通知", "展示", "显示", "计算"]
eq_actions = ["查询", "搜索", "查看", "浏览", "检索", "获取", "查找", "筛选"]
all_actions = ei_actions + eo_actions + eq_actions

def split_sentences(text):
    """将文本分割成句子，同时拆分包含多个功能的句子。"""
    # 第一步：按标点分句
    raw_sentences = [s.strip() for s in re.split(r'[.!?。！？；;]+', text) if s.strip()]
    
    sentences = []
    for sent in raw_sentences:
        # 第二步：如果句子包含"并"、"和"连接多个动作，尝试拆分
        if '并' in sent or '以及' in sent or '和' in sent:
            sub_sentences = split_by_actions(sent, all_actions)
            sentences.extend(sub_sentences)
        else:
            sentences.append(sent)
    
    return sentences

def split_by_actions(sentence, all_actions):
    """按动作拆分包含多个功能的句子。"""
    # 查找句子中所有的动作位置
    action_positions = []
    for action in all_actions:
        idx = sentence.find(action)
        if idx >= 0:
            action_positions.append((idx, action))
    
    # 按位置排序
    action_positions.sort(key=lambda x: x[0])
    print(f"  找到的动作: {action_positions}")
    
    # 如果找到多个动作，按动作拆分
    if len(action_positions) > 1:
        result = []
        for i, (pos, action) in enumerate(action_positions):
            if i < len(action_positions) - 1:
                next_pos = action_positions[i + 1][0]
                sub_sent = sentence[pos:next_pos].strip()
                sub_sent = re.sub(r'[并,和,以及,、]+$', '', sub_sent).strip()
                if sub_sent:
                    result.append(sub_sent)
            else:
                sub_sent = sentence[pos:].strip()
                if sub_sent:
                    result.append(sub_sent)
        return result
    
    return [sentence]

# 测试
text = "系统应允许用户创建客户记录。用户可以搜索客户并生成月度报表。"
print(f"输入: {text}")
print(f"分句结果:")
sentences = split_sentences(text)
for i, s in enumerate(sentences, 1):
    print(f"  {i}. {s}")
