#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票代码有效性检查脚本

检查所有示例文件中的股票代码是否为6位数字格式。
"""

import re
from pathlib import Path


def check_file(filepath):
    """检查单个文件的股票代码"""
    print(f"\n检查文件: {filepath.name}")
    print("="*80)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有可能的股票代码
    # 匹配 symbol = "..." 或 symbol="..." 或 '...'
    patterns = [
        r'symbol\s*=\s*["\'](\d+)["\']',
        r'get_\w+\(["\'](\d+)["\']',
    ]
    
    issues = []
    valid_codes = []
    
    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            code = match.group(1)
            if len(code) == 6 and code.isdigit():
                valid_codes.append(code)
            else:
                issues.append(f"  无效股票代码: {code} (应为6位数字)")
    
    print(f"找到 {len(valid_codes)} 个有效股票代码")
    if valid_codes:
        print(f"有效代码: {', '.join(set(valid_codes))}")
    
    if issues:
        print("\n发现问题:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✓ 所有股票代码都是6位数字格式")
        return True


def main():
    """主函数"""
    examples_dir = Path(__file__).parent.parent / 'examples'
    
    # 获取所有示例文件
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
        print("✓ 所有文件的股票代码都有效")
    else:
        print("✗ 部分文件的股票代码无效")
    print("="*80)


if __name__ == '__main__':
    main()
