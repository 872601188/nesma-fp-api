#!/usr/bin/env python3
"""
NESMA 功能点计算器
根据功能类型和复杂度计算功能点数
"""

# 复杂度权重矩阵
WEIGHTS = {
    'ILF': {'低': 7, '中': 10, '高': 15},
    'EIF': {'低': 5, '中': 7, '高': 10},
    'EI': {'低': 3, '中': 4, '高': 6},
    'EO': {'低': 4, '中': 5, '高': 7},
    'EQ': {'低': 3, '中': 4, '高': 6}
}

# 快速估算默认值（复杂度默认"中"）
QUICK_WEIGHTS = {
    'ILF': 10,
    'EIF': 7,
    'EI': 4,
    'EO': 5,
    'EQ': 4
}

def calculate_fp(function_list, method='detailed'):
    """
    计算功能点数
    
    Args:
        function_list: 功能列表，每项包含 type, complexity
        method: 计算方法 ('detailed', 'estimated', 'indicative')
    
    Returns:
        总功能点数和详细清单
    """
    total = 0
    details = []
    
    if method == 'indicative':
        # 预估法：只计算 ILF 和 EIF
        ilf_count = sum(1 for f in function_list if f['type'] == 'ILF')
        eif_count = sum(1 for f in function_list if f['type'] == 'EIF')
        total = 35 * ilf_count + 15 * eif_count
        details = [
            {'type': 'ILF', 'count': ilf_count, 'fp': 35 * ilf_count},
            {'type': 'EIF', 'count': eif_count, 'fp': 15 * eif_count}
        ]
    elif method == 'estimated':
        # 估算法：数据功能=低，事务功能=中
        for func in function_list:
            fp_type = func['type']
            if fp_type in ['ILF', 'EIF']:
                complexity = '低'
            else:
                complexity = '中'
            fp = WEIGHTS[fp_type][complexity]
            total += fp
            details.append({
                'module': func.get('module', ''),
                'description': func.get('description', ''),
                'type': fp_type,
                'complexity': complexity,
                'fp': fp
            })
    else:
        # 详细法：根据实际复杂度
        for func in function_list:
            fp_type = func['type']
            complexity = func.get('complexity', '中')
            fp = WEIGHTS[fp_type][complexity]
            total += fp
            details.append({
                'module': func.get('module', ''),
                'description': func.get('description', ''),
                'type': fp_type,
                'complexity': complexity,
                'fp': fp
            })
    
    return {
        'total': total,
        'details': details,
        'method': method
    }

def quick_estimate(ilf_count, eif_count, ei_count, eo_count, eq_count):
    """
    快速估算（使用默认值）
    """
    total = (QUICK_WEIGHTS['ILF'] * ilf_count +
             QUICK_WEIGHTS['EIF'] * eif_count +
             QUICK_WEIGHTS['EI'] * ei_count +
             QUICK_WEIGHTS['EO'] * eo_count +
             QUICK_WEIGHTS['EQ'] * eq_count)
    
    return {
        'ILF': {'count': ilf_count, 'fp': QUICK_WEIGHTS['ILF'] * ilf_count},
        'EIF': {'count': eif_count, 'fp': QUICK_WEIGHTS['EIF'] * eif_count},
        'EI': {'count': ei_count, 'fp': QUICK_WEIGHTS['EI'] * ei_count},
        'EO': {'count': eo_count, 'fp': QUICK_WEIGHTS['EO'] * eo_count},
        'EQ': {'count': eq_count, 'fp': QUICK_WEIGHTS['EQ'] * eq_count},
        'total': total
    }

if __name__ == '__main__':
    # 测试示例
    test_functions = [
        {'module': '用户管理', 'description': '用户表', 'type': 'ILF', 'complexity': '中'},
        {'module': '订单管理', 'description': '订单表', 'type': 'ILF', 'complexity': '中'},
        {'module': '支付', 'description': '支付宝接口', 'type': 'EIF', 'complexity': '低'},
        {'module': '用户管理', 'description': '用户注册', 'type': 'EI', 'complexity': '低'},
        {'module': '订单管理', 'description': '订单查询', 'type': 'EQ', 'complexity': '中'},
    ]
    
    result = calculate_fp(test_functions, 'detailed')
    print(f"总功能点数: {result['total']}")
    for d in result['details']:
        print(f"{d['module']} - {d['description']}: {d['type']}({d['complexity']}) = {d['fp']} FP")
