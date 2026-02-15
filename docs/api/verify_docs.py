#!/usr/bin/env python3
"""
API 文档验证脚本

验证内容：
1. 所有文档文件是否存在
2. 文档中的链接是否有效
3. 文档中提到的函数是否在代码中存在
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# 文档根目录
DOCS_DIR = Path(__file__).parent
PROJECT_ROOT = DOCS_DIR.parent.parent

# 预期的文档文件
EXPECTED_DOCS = [
    "README.md",
    "overview.md",
    "basic-info.md",
    "historical.md",
    "realtime.md",
    "financial.md",
    "news.md",
    "futures.md",
    "options.md",
    "insider.md",
    "indicators.md",
    # 扩展模块文档
    "fundflow.md",
    "disclosure.md",
    "northbound.md",
    "macro.md",
    "blockdeal.md",
    "lhb.md",
    "limitup.md",
    "margin.md",
    "pledge.md",
    "restricted.md",
    "goodwill.md",
    "esg.md",
    # 其他文档
    "REFACTORING_SUMMARY.md",
    "CHANGELOG.md",
]

# 核心API函数
CORE_FUNCTIONS = [
    "get_basic_info",
    "get_hist_data",
    "get_realtime_data",
    "get_news_data",
    "get_balance_sheet",
    "get_income_statement",
    "get_cash_flow",
    "get_financial_metrics",
    "get_inner_trade_data",
    "get_futures_hist_data",
    "get_futures_realtime_data",
    "get_futures_main_contracts",
    "get_options_chain",
    "get_options_realtime",
    "get_options_expirations",
    "get_options_hist",
]


def check_files_exist() -> List[str]:
    """检查所有预期的文档文件是否存在"""
    missing = []
    for doc in EXPECTED_DOCS:
        doc_path = DOCS_DIR / doc
        if not doc_path.exists():
            missing.append(doc)
    return missing


def check_markdown_links(doc_path: Path) -> List[Tuple[str, str]]:
    """检查文档中的 Markdown 链接是否有效"""
    broken_links = []
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 Markdown 链接 [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = re.findall(link_pattern, content)
    
    for text, url in links:
        # 跳过外部链接和锚点链接
        if url.startswith('http') or url.startswith('#'):
            continue
        
        # 处理相对路径
        if url.startswith('../'):
            # 相对于 docs/api 的路径
            target_path = (DOCS_DIR / url).resolve()
        else:
            # 同目录下的文件
            target_path = (DOCS_DIR / url).resolve()
        
        if not target_path.exists():
            broken_links.append((text, url))
    
    return broken_links


def check_function_exists(func_name: str) -> bool:
    """检查函数是否在代码中存在"""
    init_file = PROJECT_ROOT / "src" / "akshare_one" / "__init__.py"
    
    if not init_file.exists():
        return False
    
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查函数定义
    pattern = rf'def {func_name}\s*\('
    return bool(re.search(pattern, content))


def main():
    """主验证函数"""
    print("=" * 60)
    print("API 文档验证")
    print("=" * 60)
    
    # 1. 检查文件是否存在
    print("\n1. 检查文档文件...")
    missing_files = check_files_exist()
    if missing_files:
        print(f"   ❌ 缺失文件: {', '.join(missing_files)}")
    else:
        print(f"   ✅ 所有 {len(EXPECTED_DOCS)} 个文档文件都存在")
    
    # 2. 检查链接
    print("\n2. 检查文档链接...")
    total_broken = 0
    for doc in EXPECTED_DOCS:
        doc_path = DOCS_DIR / doc
        if doc_path.exists():
            broken = check_markdown_links(doc_path)
            if broken:
                print(f"   ❌ {doc} 有 {len(broken)} 个失效链接:")
                for text, url in broken:
                    print(f"      - [{text}]({url})")
                total_broken += len(broken)
    
    if total_broken == 0:
        print("   ✅ 所有链接都有效")
    else:
        print(f"   ❌ 总计 {total_broken} 个失效链接")
    
    # 3. 检查核心函数
    print("\n3. 检查核心函数...")
    missing_funcs = []
    for func in CORE_FUNCTIONS:
        if not check_function_exists(func):
            missing_funcs.append(func)
    
    if missing_funcs:
        print(f"   ❌ 缺失函数: {', '.join(missing_funcs)}")
    else:
        print(f"   ✅ 所有 {len(CORE_FUNCTIONS)} 个核心函数都存在")
    
    # 总结
    print("\n" + "=" * 60)
    if not missing_files and total_broken == 0 and not missing_funcs:
        print("✅ 验证通过！所有文档都是最新的。")
    else:
        print("❌ 验证失败！请修复上述问题。")
    print("=" * 60)


if __name__ == "__main__":
    main()
