WEIGHTS = {
    'ILF': {'低': 7, '中': 10, '高': 15},
    'EIF': {'低': 5, '中': 7, '高': 10},
    'EI': {'低': 3, '中': 4, '高': 6},
    'EO': {'低': 4, '中': 5, '高': 7},
    'EQ': {'低': 3, '中': 4, '高': 6}
}

def calculate_fp(function_list, method='detailed'):
    total = 0
    details = []
    
    for func in function_list:
        fp_type = func.get('type', 'EQ')
        complexity = func.get('complexity', '中')
        fp = WEIGHTS.get(fp_type, {}).get(complexity, 4)
        total += fp
        details.append({
            'module': func.get('module', ''),
            'description': func.get('description', ''),
            'type': fp_type,
            'complexity': complexity,
            'fp': fp
        })
    
    return {'total': total, 'details': details, 'method': method}
