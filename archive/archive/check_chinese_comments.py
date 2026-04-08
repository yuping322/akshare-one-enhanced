#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文注释完整性检查脚本

检查所有示例文件是否包含足够的中文注释。
"""

import re
from pathlib import Path


def has_chinese(text):
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def check_file(filepath):
    """检查单个文件的中文注释"""
    print(f"\n检查文件: {filepath.name}")
    print("="*80)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    in_function = False
    function_name = ""
    has_function_comment = False
    
    for i, line in enumerate(lines, 1):
        # 检查函数定义
        if line.strip().startswith('def '):
            if in_function and not has_function_comment:
                issues.append(f"  行 {i-1}: 函数 {function_name} 缺少中文注释")
            
            in_function = True
            function_name = line.strip().split('(')[0].replace('def ', '')
            has_function_comment = False
        
        # 检查是否有中文注释
        if in_function and has_chinese(line):
            has_function_comment = True
    
    # 检查最后一个函数
    if in_function and not has_function_comment:
        issues.append(f"  函数 {function_name} 缺少中文注释")
    
    # 统计中文注释行数
    comment_lines = [line for line in lines if '#' in line and has_chinese(line)]
    docstring_lines = [line for line in lines if '"""' in line or "'''" in line]
    
    total_lines = len(lines)
    code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
    chinese_comment_lines = len(comment_lines)
    
    print(f"总行数: {total_lines}")
    print(f"代码行数: {code_lines}")
    print(f"中文注释行数: {chinese_comment_lines}")
    print(f"注释比例: {chinese_comment_lines/code_lines*100:.1f}%")
    
    if issues:
        print("\n发现问题:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✓ 中文注释完整")
        return True


def main():
    """主函数"""
    examples_dir = Path(__file__).parent.parent / 'examples'
    
    # 获取所有示例文件（排除 validate_data_sources.py 和 exception_usage_example.py）
    example_files = [
        f for f in examples_dir.glob('*_example.py')
        if f.name not in ['validate_data_sources.py', 'exception_usage_example.py']
    ]
    
    print(f"找到 {len(example_files)} 个示例文件")
    print("="*80)
    
    all_pass = True
    for filepath in sorted(example_files):
        if not check_file(filepath):
            all_pass = False
    
    print("\n" + "="*80)
    if all_pass:
        print("✓ 所有文件的中文注释都完整")
    else:
        print("✗ 部分文件的中文注释不完整")
    print("="*80)


if __name__ == '__main__':
    main()
