#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量自动修复脚本

自动修复以下问题：
1. 删除未使用的导入
2. 删除空白行中的空格
3. 修复 f-string 缺少占位符的问题
4. 删除行尾空格
"""

import os
import re
from pathlib import Path


def fix_file(filepath):
    """修复单个文件的代码质量问题"""
    print(f"修复文件: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    imports_to_remove = set()
    
    # 第一遍：识别未使用的导入
    unused_imports = {
        'sys', 'pandas as pd', 'datetime.datetime', 'datetime.timedelta',
        'akshare_one.modules.exceptions.UpstreamChangedError'
    }
    
    for i, line in enumerate(lines):
        # 删除空白行中的空格和行尾空格
        if line.strip() == '':
            fixed_lines.append('\n')
        else:
            # 删除行尾空格
            line = line.rstrip() + '\n'
            
            # 修复 f-string 缺少占位符的问题
            # 将 f"..." 改为 "..." 如果没有 {} 占位符
            if 'f"' in line or "f'" in line:
                # 检查是否有占位符
                if '{' not in line:
                    line = line.replace('f"', '"').replace("f'", "'")
            
            fixed_lines.append(line)
    
    # 第二遍：删除未使用的导入
    final_lines = []
    for line in fixed_lines:
        # 检查是否是未使用的导入
        skip = False
        if line.startswith('import ') or line.startswith('from '):
            # 检查 sys 导入
            if 'import sys' in line and 'sys' in unused_imports:
                # 检查文件中是否使用了 sys
                content = ''.join(fixed_lines)
                if 'sys.' not in content and 'sys)' not in content:
                    skip = True
            
            # 检查 pandas 导入
            if 'import pandas as pd' in line:
                content = ''.join(fixed_lines)
                if 'pd.' not in content and 'pd)' not in content:
                    skip = True
            
            # 检查 datetime 导入
            if 'from datetime import' in line and ('datetime' in line or 'timedelta' in line):
                content = ''.join(fixed_lines)
                if 'datetime(' not in content and 'timedelta(' not in content:
                    skip = True
            
            # 检查 UpstreamChangedError 导入
            if 'UpstreamChangedError' in line:
                content = ''.join(fixed_lines)
                if 'UpstreamChangedError' not in content.replace(line, ''):
                    skip = True
        
        if not skip:
            final_lines.append(line)
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    
    print(f"  ✓ 修复完成")


def main():
    """主函数"""
    examples_dir = Path(__file__).parent.parent / 'examples'
    
    # 获取所有 Python 文件
    python_files = list(examples_dir.glob('*.py'))
    
    print(f"找到 {len(python_files)} 个 Python 文件")
    print("="*80)
    
    for filepath in python_files:
        if filepath.name != '__init__.py':
            fix_file(filepath)
    
    print("="*80)
    print("所有文件修复完成！")


if __name__ == '__main__':
    main()
