"""
测试批量分析API
"""
import requests
import json

API_URL = "http://localhost:8000"

# 测试文本
test_text = """
系统应允许用户创建客户记录。用户可以搜索客户并生成月度报表。
系统支持客户信息的导入和导出功能。管理员可以查看系统日志。
用户需要能够修改个人资料。系统提供数据备份功能。
"""

def test_traditional():
    """测试传统分析"""
    print("=" * 50)
    print("测试传统分析API")
    print("=" * 50)
    
    response = requests.post(
        f"{API_URL}/analyze",
        json={
            "text": test_text,
            "project_name": "测试项目-传统"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 分析成功")
        print(f"  项目: {result['project_name']}")
        print(f"  功能点: {len(result['function_points'])} 个")
        print(f"  UFP: {result['total_unadjusted_fp']}")
        print(f"  AFP: {result['adjusted_fp']}")
    else:
        print(f"✗ 分析失败: {response.status_code}")
        print(response.text)

def test_batch():
    """测试批量分析"""
    print("\n" + "=" * 50)
    print("测试批量分析API (按句子)")
    print("=" * 50)
    
    response = requests.post(
        f"{API_URL}/analyze/batch",
        json={
            "text": test_text,
            "project_name": "测试项目-批量",
            "split_mode": "sentence"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 批量分析成功")
        print(f"  分割模式: {result['split_mode']}")
        print(f"  总片段数: {result['total_segments']}")
        print(f"  处理片段: {result['processed_segments']}")
        print(f"  功能点: {len(result['function_points'])} 个")
        print(f"  UFP: {result['total_unadjusted_fp']}")
        print(f"  组件统计: {result['component_counts']}")
    else:
        print(f"✗ 分析失败: {response.status_code}")
        print(response.text)

def test_preview():
    """测试分割预览"""
    print("\n" + "=" * 50)
    print("测试分割预览API")
    print("=" * 50)
    
    for mode in ["sentence", "paragraph", "chapter"]:
        response = requests.post(
            f"{API_URL}/analyze/preview",
            json={
                "text": test_text,
                "mode": mode
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ {mode} 模式: {result['summary']['count']} 个片段")
        else:
            print(f"✗ {mode} 模式失败: {response.status_code}")

def test_split_modes():
    """测试获取分割模式列表"""
    print("\n" + "=" * 50)
    print("测试分割模式列表API")
    print("=" * 50)
    
    response = requests.get(f"{API_URL}/split-modes")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 获取成功")
        for mode in result['modes']:
            print(f"  - {mode['name']}: {mode['description']}")
    else:
        print(f"✗ 获取失败: {response.status_code}")

def test_batch_stream():
    """测试批量流式分析"""
    print("\n" + "=" * 50)
    print("测试批量流式分析API")
    print("=" * 50)
    
    try:
        import urllib.request
        
        req = urllib.request.Request(
            f"{API_URL}/analyze/batch/stream",
            data=json.dumps({
                "text": test_text,
                "project_name": "测试项目-流式",
                "split_mode": "sentence"
            }).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        print("✓ 流式响应接收中...")
        event_count = 0
        
        with urllib.request.urlopen(req) as response:
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        event = json.loads(line[6:])
                        event_count += 1
                        if event['type'] == 'split_complete':
                            print(f"  分割完成: {event['data']['total_segments']} 个片段")
                        elif event['type'] == 'segment_complete':
                            print(f"  片段 {event['data']['index']}/{event['data']['total']} 完成")
                        elif event['type'] == 'complete':
                            print(f"  ✓ 全部完成: {len(event['data']['function_points'])} 个功能点")
                    except json.JSONDecodeError:
                        pass
        
        print(f"✓ 共接收 {event_count} 个事件")
        
    except Exception as e:
        print(f"✗ 流式分析失败: {e}")

if __name__ == "__main__":
    print("NESMA 功能点分析 API 测试")
    print("请确保后端服务已启动: python backend/main.py")
    print()
    
    try:
        # 测试健康检查
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✓ 后端服务连接正常\n")
        else:
            print("✗ 后端服务异常")
            exit(1)
    except Exception as e:
        print(f"✗ 无法连接到后端服务: {e}")
        print("请先启动后端服务: cd backend && python main.py")
        exit(1)
    
    # 运行测试
    test_traditional()
    test_batch()
    test_preview()
    test_split_modes()
    test_batch_stream()
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)
