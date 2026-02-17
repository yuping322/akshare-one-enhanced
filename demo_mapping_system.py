#!/usr/bin/env python3
"""
映射表系统使用示例
展示如何使用全面的映射表系统
"""

from mappings.mapping_utils import (
    get_stock_name,
    get_index_name,
    get_etf_name,
    get_industry_name,
    search_by_name,
    get_option_underlying_patterns,
    preload_mappings
)


def main():
    # 预加载映射表以提高性能
    preload_mappings()

    print("=== 全面映射表系统演示 ===\n")

    # 1. 股票代码查询
    print("1. 股票代码查询:")
    stock_codes = ["000001", "600000", "000002"]
    for code in stock_codes:
        name = get_stock_name(code)
        print(f"   {code} -> {name}")

    print()

    # 2. 指数代码查询
    print("2. 指数代码查询:")
    index_codes = ["000300", "000016", "000905"]
    for code in index_codes:
        name = get_index_name(code)
        print(f"   {code} -> {name}")

    print()

    # 3. ETF基金查询
    print("3. ETF基金查询:")
    etf_codes = ["510300", "510050", "510500"]
    for code in etf_codes:
        name = get_etf_name(code)
        print(f"   {code} -> {name}")

    print()

    # 4. 行业板块查询
    print("4. 行业板块查询:")
    industry_codes = ["BK0473", "BK0474"]
    for code in industry_codes:
        name = get_industry_name(code)
        print(f"   {code} -> {name}")

    print()

    # 5. 模糊搜索
    print("5. 模糊搜索功能:")
    banks = search_by_name("stock_code_to_name", "银行")
    print(f"   包含'银行'的股票 ({len(banks)}个): {[name for name in list(banks.values())[:5]]}")

    tech_stocks = search_by_name("stock_code_to_name", "科技")
    print(f"   包含'科技'的股票 ({len(tech_stocks)}个): {[name for name in list(tech_stocks.values())[:5]]}")

    print()

    # 6. 期权底层资产模式
    print("6. 期权底层资产匹配模式:")
    underlying_codes = ["510300", "510050"]
    for code in underlying_codes:
        patterns = get_option_underlying_patterns(code)
        print(f"   {code} -> {patterns}")

    print()

    # 7. 映射表统计
    print("7. 映射表统计:")
    import pandas as pd
    import os

    mappings_dir = "mappings"
    for filename in os.listdir(mappings_dir):
        if filename.endswith(".csv") and filename != "full_combined_mapping.csv":
            df = pd.read_csv(os.path.join(mappings_dir, filename), encoding='utf-8-sig')
            table_name = filename.replace('.csv', '')
            print(f"   {table_name}: {len(df)} 条记录")


if __name__ == "__main__":
    main()