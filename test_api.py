import requests

try:
    response = requests.post('http://localhost:8000/analyze', json={
        'text': '系统应允许用户创建客户记录。用户可以搜索客户并生成月度报表。',
        'project_name': '测试项目'
    })
    data = response.json()
    print('功能点数:', len(data.get('function_points', [])))
    print('功能清单:')
    for i, fp in enumerate(data.get('function_points', []), 1):
        name = fp['name'][:40] if len(fp['name']) > 40 else fp['name']
        print(f"  {i}. [{fp['type']}] {name} - {fp['count']} FP")
except Exception as e:
    print('Error:', e)
