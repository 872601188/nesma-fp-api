import requests
import json

response = requests.post('http://localhost:8000/analyze', json={
    'text': '系统应允许用户创建客户记录。用户可以搜索客户并生成月度报表。',
    'project_name': '测试项目'
})
data = response.json()

print('功能点数:', len(data.get('function_points', [])))
print('原始需求:', data.get('original_requirements', '')[:50])
print('总UFP:', data.get('total_unadjusted_fp', 0))
print('\n功能点列表:')

for i, fp in enumerate(data.get('function_points', []), 1):
    print("  " + str(i) + ". type=" + fp.get('type') + ", name=" + fp.get('name', '')[:30] + ", count=" + str(fp.get('count')))

print('\n完整数据结构:')
print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
