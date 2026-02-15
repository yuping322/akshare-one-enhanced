#!/usr/bin/env python3
"""
将 interfaces-reference.md 拆分成12个独立的模块文档
"""

import re
from pathlib import Path

# 文档根目录
DOCS_DIR = Path(__file__).parent

# 12个模块的配置
MODULES = [
    {
        "id": 1,
        "name_zh": "资金流",
        "name_en": "FundFlow",
        "filename": "fundflow.md",
        "example": "fundflow_example.py",
        "import_path": "akshare_one.modules.fundflow"
    },
    {
        "id": 2,
        "name_zh": "公告信披",
        "name_en": "Disclosure",
        "filename": "disclosure.md",
        "example": "disclosure_example.py",
        "import_path": "akshare_one.modules.disclosure"
    },
    {
        "id": 3,
        "name_zh": "北向资金",
        "name_en": "Northbound",
        "filename": "northbound.md",
        "example": "northbound_example.py",
        "import_path": "akshare_one.modules.northbound"
    },
    {
        "id": 4,
        "name_zh": "宏观数据",
        "name_en": "Macro",
        "filename": "macro.md",
        "example": "macro_example.py",
        "import_path": "akshare_one.modules.macro"
    },
    {
        "id": 5,
        "name_zh": "大宗交易",
        "name_en": "BlockDeal",
        "filename": "blockdeal.md",
        "example": "blockdeal_example.py",
        "import_path": "akshare_one.modules.blockdeal"
    },
    {
        "id": 6,
        "name_zh": "龙虎榜",
        "name_en": "DragonTigerLHB",
        "filename": "lhb.md",
        "example": "lhb_example.py",
        "import_path": "akshare_one.modules.lhb"
    },
    {
        "id": 7,
        "name_zh": "涨停池",
        "name_en": "LimitUpDown",
        "filename": "limitup.md",
        "example": "limitup_example.py",
        "import_path": "akshare_one.modules.limitup"
    },
    {
        "id": 8,
        "name_zh": "融资融券",
        "name_en": "MarginFinancing",
        "filename": "margin.md",
        "example": "margin_example.py",
        "import_path": "akshare_one.modules.margin"
    },
    {
        "id": 9,
        "name_zh": "股权质押",
        "name_en": "EquityPledge",
        "filename": "pledge.md",
        "example": "pledge_example.py",
        "import_path": "akshare_one.modules.pledge"
    },
    {
        "id": 10,
        "name_zh": "限售解禁",
        "name_en": "RestrictedRelease",
        "filename": "restricted.md",
        "example": "restricted_example.py",
        "import_path": "akshare_one.modules.restricted"
    },
    {
        "id": 11,
        "name_zh": "商誉",
        "name_en": "Goodwill",
        "filename": "goodwill.md",
        "example": "goodwill_example.py",
        "import_path": "akshare_one.modules.goodwill"
    },
    {
        "id": 12,
        "name_zh": "ESG评级",
        "name_en": "ESG",
        "filename": "esg.md",
        "example": "esg_example.py",
        "import_path": "akshare_one.modules.esg"
    }
]


def read_interfaces_reference():
    """读取 interfaces-reference.md 文件"""
    ref_file = DOCS_DIR / "interfaces-reference.md"
    with open(ref_file, 'r', encoding='utf-8') as f:
        return f.read()


def extract_module_content(content, module_id):
    """提取指定模块的内容"""
    # 匹配模块标题和内容
    pattern = rf'## {module_id}\. .+?\n\n(.+?)(?=\n---\n\n## {module_id + 1}\. |\n---\n\n## 附录|$)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return None


def create_module_doc(module, module_content):
    """创建单个模块文档"""
    # 提取数据源和更新频率
    data_source_match = re.search(r'\*\*数据源\*\*：(.+?)\s+', module_content)
    update_freq_match = re.search(r'\*\*更新频率\*\*：(.+?)\s+', module_content)
    
    data_source = data_source_match.group(1) if data_source_match else "东方财富（eastmoney）"
    update_freq = update_freq_match.group(1) if update_freq_match else "实时 / T+1"
    
    # 提取所有函数名
    function_pattern = r'### \d+\.\d+ (get_\w+)'
    functions = re.findall(function_pattern, module_content)
    
    # 构建导入语句
    import_statement = f"from {module['import_path']} import (\n"
    import_statement += ",\n".join(f"    {func}" for func in functions)
    import_statement += "\n)"
    
    # 构建文档头部
    doc = f"""# {module['name_zh']}（{module['name_en']}）

{module['name_zh']}模块提供相关数据接口。

**数据源**：{data_source}  
**更新频率**：{update_freq}  
**示例程序**：[examples/{module['example']}](../../examples/{module['example']})

## 导入方式

```python
{import_statement}
```

## 接口列表

"""
    
    # 移除模块描述部分，只保留接口内容
    # 找到第一个 ### 开始的位置
    first_func_match = re.search(r'### \d+\.\d+ ', module_content)
    if first_func_match:
        interfaces_content = module_content[first_func_match.start():]
        # 移除编号
        interfaces_content = re.sub(r'### \d+\.\d+ ', '### ', interfaces_content)
        doc += interfaces_content
    else:
        doc += module_content
    
    return doc


def main():
    """主函数"""
    print("开始拆分 interfaces-reference.md...")
    
    # 读取原文件
    content = read_interfaces_reference()
    
    # 为每个模块创建文档
    for module in MODULES:
        print(f"处理模块 {module['id']}: {module['name_zh']}...")
        
        # 提取模块内容
        module_content = extract_module_content(content, module['id'])
        
        if module_content:
            # 创建模块文档
            doc = create_module_doc(module, module_content)
            
            # 写入文件
            output_file = DOCS_DIR / module['filename']
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(doc)
            
            print(f"  ✓ 已创建 {module['filename']}")
        else:
            print(f"  ✗ 未找到模块内容")
    
    print("\n拆分完成！")
    print(f"已创建 {len(MODULES)} 个模块文档")


if __name__ == "__main__":
    main()
