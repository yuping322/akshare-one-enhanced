#!/usr/bin/env python3
"""检查 API 文档中的重复内容"""

import os
from pathlib import Path
from collections import defaultdict

def extract_sections(content):
    """提取文档中的主要部分"""
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def find_duplicate_content(docs_dir):
    """查找重复的文档内容"""
    
    # 读取所有 markdown 文件
    md_files = list(Path(docs_dir).glob('*.md'))
    
    # 排除索引和总结文件
    exclude_files = {'README.md', 'overview.md', 'CHANGELOG.md', 
                     'REFACTORING_SUMMARY.md', 'FINAL_REFACTORING_SUMMARY.md'}
    
    md_files = [f for f in md_files if f.name not in exclude_files]
    
    print("=" * 60)
    print("API 文档重复内容检查")
    print("=" * 60)
    print(f"\n检查 {len(md_files)} 个文档文件...\n")
    
    # 1. 检查完全相同的文件
    print("1. 检查完全相同的文件...")
    file_contents = {}
    content_to_files = defaultdict(list)
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            file_contents[file_path.name] = content
            content_to_files[content].append(file_path.name)
    
    duplicates_found = False
    for content, files in content_to_files.items():
        if len(files) > 1:
            print(f"   ❌ 发现完全相同的文件: {', '.join(files)}")
            duplicates_found = True
    
    if not duplicates_found:
        print("   ✅ 没有完全相同的文件")
    
    # 2. 检查重复的章节内容
    print("\n2. 检查重复的章节内容...")
    section_contents = defaultdict(list)
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            sections = extract_sections(content)
            
            for section_name, section_content in sections.items():
                # 忽略太短的内容（少于100字符）
                if len(section_content.strip()) > 100:
                    section_contents[section_content.strip()].append(
                        (file_path.name, section_name)
                    )
    
    duplicates_found = False
    for content, locations in section_contents.items():
        if len(locations) > 1:
            print(f"\n   ❌ 发现重复的章节内容:")
            for filename, section in locations:
                print(f"      - {filename}: {section}")
            print(f"      内容长度: {len(content)} 字符")
            duplicates_found = True
    
    if not duplicates_found:
        print("   ✅ 没有重复的章节内容")
    
    # 3. 检查重复的异常说明
    print("\n3. 检查异常说明的一致性...")
    exception_patterns = defaultdict(list)
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 查找异常部分
            if '#### 异常' in content or '## 异常' in content:
                # 提取异常列表
                lines = content.split('\n')
                in_exception_section = False
                exceptions = []
                
                for line in lines:
                    if '异常' in line and line.startswith('#'):
                        in_exception_section = True
                        continue
                    elif in_exception_section:
                        if line.startswith('#'):
                            break
                        if line.strip().startswith('-'):
                            exceptions.append(line.strip())
                
                if exceptions:
                    exception_key = tuple(sorted(exceptions))
                    exception_patterns[exception_key].append(file_path.name)
    
    print(f"   发现 {len(exception_patterns)} 种不同的异常说明模式")
    
    for pattern, files in exception_patterns.items():
        if len(files) > 1:
            print(f"\n   相同的异常说明出现在 {len(files)} 个文件中:")
            for f in files[:5]:  # 只显示前5个
                print(f"      - {f}")
            if len(files) > 5:
                print(f"      ... 还有 {len(files) - 5} 个文件")
    
    # 4. 检查参数表格的重复
    print("\n4. 检查常见参数的一致性...")
    common_params = ['start_date', 'end_date', 'source', 'symbol']
    param_definitions = defaultdict(lambda: defaultdict(list))
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                for param in common_params:
                    if f'| {param} |' in line or f'| `{param}` |' in line:
                        param_definitions[param][line.strip()].append(file_path.name)
    
    for param, definitions in param_definitions.items():
        if len(definitions) > 1:
            print(f"\n   ⚠️  参数 '{param}' 有 {len(definitions)} 种不同的定义:")
            for definition, files in list(definitions.items())[:3]:
                print(f"      定义: {definition[:80]}...")
                print(f"      出现在: {files[0]}")
    
    # 5. 检查导入方式的格式
    print("\n5. 检查导入方式的格式一致性...")
    import_sections = {}
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if '## 导入方式' in content:
                # 提取导入方式部分
                start = content.find('## 导入方式')
                end = content.find('\n## ', start + 1)
                if end == -1:
                    end = len(content)
                
                import_section = content[start:end].strip()
                import_sections[file_path.name] = import_section
    
    # 检查格式是否一致
    formats = defaultdict(list)
    for filename, section in import_sections.items():
        # 简化格式检查
        has_python_block = '```python' in section
        has_from_import = 'from akshare_one' in section
        format_key = (has_python_block, has_from_import)
        formats[format_key].append(filename)
    
    if len(formats) > 1:
        print("   ⚠️  导入方式格式不一致:")
        for format_key, files in formats.items():
            print(f"      格式 {format_key}: {len(files)} 个文件")
    else:
        print("   ✅ 导入方式格式一致")
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)

if __name__ == '__main__':
    docs_dir = Path(__file__).parent
    find_duplicate_content(docs_dir)
