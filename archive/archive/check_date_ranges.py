#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日期范围合理性检查脚本

检查所有示例文件中的日期范围是否在最近1-6个月内。
"""

import re
from pathlib import Path
from datetime import datetime, timedelta


def check_file(filepath):
    """检查单个文件的日期范围"""
    print(f"\n检查文件: {filepath.name}")
    print("="*80)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有日期
    # 匹配 YYYY-MM-DD 格式的日期
    date_pattern = r'["\'](\d{4}-\d{2}-\d{2})["\']'
    matches = re.finditer(date_pattern, content)
    
    issues = []
    dates_found = []
    
    now = datetime.now()
    six_months_ago = now - timedelta(days=180)
    one_month_ago = now - timedelta(days=30)
    
    for match in matches:
        date_str = match.group(1)
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            dates_found.append(date_str)
            
            # 检查日期是否在合理范围内（过去6个月到未来1个月）
            if date_obj < six_months_ago:
                issues.append(f"  日期 {date_str} 过早（超过6个月前）")
            elif date_obj > now + timedelta(days=30):
                issues.append(f"  日期 {date_str} 过晚（超过未来1个月）")
        except ValueError:
            issues.append(f"  无效日期格式: {date_str}")
    
    print(f"找到 {len(dates_found)} 个日期")
    if dates_found:
        unique_dates = sorted(set(dates_found))
        print(f"日期范围: {unique_dates[0]} 到 {unique_dates[-1]}")
    
    if issues:
        print("\n发现问题:")
        for issue in issues:
            print(issue)
        return False
    else:
        if dates_found:
            print("✓ 所有日期都在合理范围内（最近6个月）")
        else:
            print("✓ 未找到固定日期（使用动态日期）")
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
    print(f"当前日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"合理日期范围: {(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')} 到 {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}")
    print("="*80)
    
    all_pass = True
    for filepath in sorted(example_files):
        if not check_file(filepath):
            all_pass = False
    
    print("\n" + "="*80)
    if all_pass:
        print("✓ 所有文件的日期范围都合理")
    else:
        print("✗ 部分文件的日期范围不合理")
    print("="*80)


if __name__ == '__main__':
    main()
