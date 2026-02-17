#!/usr/bin/env python3
"""
动态生成映射表的脚本
此脚本用于定期更新底层资产映射表
"""

import json
import pandas as pd
from datetime import datetime
import akshare as ak


def generate_underlying_symbol_mapping():
    """
    生成底层资产符号映射表
    包括指数、ETF基金等期权的标的资产映射
    """
    print("Generating underlying symbol mapping...")

    mapping = {}

    # 1. 获取指数信息
    try:
        index_info = ak.index_stock_info()
        print(f"Found {len(index_info)} indices")

        # 添加主要指数映射
        major_indices = {
            "000300": ["沪深300", "HS300", "300ETF", "沪深300ETF"],
            "000016": ["上证50", "SZ50", "50ETF", "上证50ETF"],
            "000905": ["中证500", "ZZ500", "500ETF", "中证500ETF"],
            "000852": ["中证1000", "ZZ1000", "1000ETF", "中证1000ETF"],
            "000688": ["科创50", "KC50", "880688", "科创板"],
        }

        for code, patterns in major_indices.items():
            mapping[code] = patterns

        # 2. 获取ETF基金信息
        try:
            # 获取ETF基金列表
            etf_fund = ak.fund_etf_fund_info_em()  # 获取ETF基金信息
            if not etf_fund.empty:
                # 筛选主要的ETF基金
                major_etfs = etf_fund[
                    etf_fund['基金简称'].str.contains(
                        '300|50|500|1000|创业板|科创|消费|医药|科技|金融|红利|价值|成长',
                        na=False, regex=True
                    )
                ]

                for _, row in major_etfs.iterrows():
                    fund_code = row.get('基金代码', '')
                    fund_name = row.get('基金简称', '')
                    if fund_code and fund_name:
                        # 添加基金代码到名称的映射
                        if fund_code not in mapping:
                            mapping[fund_code] = []
                        mapping[fund_code].extend([
                            fund_name,
                            fund_name.replace('ETF', '').strip(),
                            fund_name.replace('联接', '').strip(),
                        ])
        except Exception as e:
            print(f"ETF fund info not available: {e}")

        # 3. 获取股票信息（用于个股期权）
        try:
            sz_info = ak.stock_info_sz_name_code()
            sh_info = ak.stock_info_sh_name_code()
            # 只保留主板和中小板的重要股票
            all_stocks = pd.concat([sz_info, sh_info], ignore_index=True)

            # 筛选重要股票（大市值公司）
            # 这里可以根据需要添加筛选条件

        except Exception as e:
            print(f"Stock info not available: {e}")

    except Exception as e:
        print(f"Index info not available: {e}")
        # 使用默认映射作为后备
        mapping.update({
            "510300": ["300ETF", "沪深300ETF", "沪深300"],
            "510050": ["50ETF", "上证50ETF", "上证50"],
            "510500": ["500ETF", "中证500ETF", "中证500"],
            "159919": ["300ETF", "沪深300ETF", "沪深300"],
            "159901": ["深100ETF", "深证100", "深证100ETF"],
        })

    return mapping


def generate_option_symbol_mapping():
    """
    生成期权符号映射表
    包括期权代码到相关信息的映射
    """
    print("Generating option symbol mapping...")

    mapping = {}

    try:
        # 获取期权品种信息
        option_symbols = ak.option_comm_symbol()
        if not option_symbols.empty:
            for _, row in option_symbols.iterrows():
                mapping[row['品种代码']] = {
                    'name': row['品种名称'],
                    'type': 'commodity'  # 商品期权
                }
    except Exception as e:
        print(f"Option symbol info not available: {e}")

    return mapping


def generate_industry_mapping():
    """
    生成行业分类映射表
    """
    print("Generating industry mapping...")

    mapping = {}

    try:
        # 获取行业板块信息
        industry_names = ak.stock_board_industry_name_em()
        if not industry_names.empty:
            for _, row in industry_names.iterrows():
                industry_code = row.get('板块代码', '')
                industry_name = row.get('板块名称', '')
                if industry_code and industry_name:
                    mapping[industry_code] = industry_name
    except Exception as e:
        print(f"Industry mapping not available: {e}")

    return mapping


def save_mapping_tables():
    """
    保存所有映射表到JSON文件
    """
    print("Saving mapping tables...")

    # 生成各个映射表
    underlying_mapping = generate_underlying_symbol_mapping()
    option_mapping = generate_option_symbol_mapping()
    industry_mapping = generate_industry_mapping()

    # 保存到文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(f"mapping_tables/underlying_patterns_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(underlying_mapping, f, ensure_ascii=False, indent=2)

    with open(f"mapping_tables/option_symbols_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(option_mapping, f, ensure_ascii=False, indent=2)

    with open(f"mapping_tables/industries_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(industry_mapping, f, ensure_ascii=False, indent=2)

    # 同时保存最新的版本
    with open("mapping_tables/underlying_patterns_latest.json", 'w', encoding='utf-8') as f:
        json.dump(underlying_mapping, f, ensure_ascii=False, indent=2)

    with open("mapping_tables/option_symbols_latest.json", 'w', encoding='utf-8') as f:
        json.dump(option_mapping, f, ensure_ascii=False, indent=2)

    with open("mapping_tables/industries_latest.json", 'w', encoding='utf-8') as f:
        json.dump(industry_mapping, f, ensure_ascii=False, indent=2)

    print(f"Mapping tables saved with timestamp: {timestamp}")
    print(f"Underlying patterns: {len(underlying_mapping)} entries")
    print(f"Option symbols: {len(option_mapping)} entries")
    print(f"Industries: {len(industry_mapping)} entries")


def load_latest_mappings():
    """
    加载最新的映射表
    """
    import os

    mappings_dir = "mapping_tables"
    if not os.path.exists(mappings_dir):
        os.makedirs(mappings_dir)

    try:
        with open(f"{mappings_dir}/underlying_patterns_latest.json", 'r', encoding='utf-8') as f:
            underlying_patterns = json.load(f)
    except FileNotFoundError:
        underlying_patterns = {}

    try:
        with open(f"{mappings_dir}/option_symbols_latest.json", 'r', encoding='utf-8') as f:
            option_symbols = json.load(f)
    except FileNotFoundError:
        option_symbols = {}

    try:
        with open(f"{mappings_dir}/industries_latest.json", 'r', encoding='utf-8') as f:
            industries = json.load(f)
    except FileNotFoundError:
        industries = {}

    return {
        'underlying_patterns': underlying_patterns,
        'option_symbols': option_symbols,
        'industries': industries
    }


def update_if_needed():
    """
    检查是否需要更新映射表（比如每周更新一次）
    """
    import os
    from datetime import timedelta

    mappings_dir = "mapping_tables"
    if not os.path.exists(mappings_dir):
        os.makedirs(mappings_dir)

    latest_file = f"{mappings_dir}/underlying_patterns_latest.json"

    if os.path.exists(latest_file):
        # 检查文件修改时间，如果超过一周则更新
        import time
        file_time = os.path.getmtime(latest_file)
        if datetime.fromtimestamp(file_time) < datetime.now() - timedelta(days=7):
            print("Mappings are older than 7 days, updating...")
            save_mapping_tables()
        else:
            print("Mappings are up to date")
    else:
        print("No existing mappings found, generating...")
        save_mapping_tables()


if __name__ == "__main__":
    # 创建目录
    import os
    if not os.path.exists("mapping_tables"):
        os.makedirs("mapping_tables")

    # 更新映射表
    update_if_needed()

    # 加载并显示结果
    mappings = load_latest_mappings()
    print("\nGenerated mappings:")
    print(f"- Underlying patterns: {len(mappings['underlying_patterns'])} entries")
    print(f"- Option symbols: {len(mappings['option_symbols'])} entries")
    print(f"- Industries: {len(mappings['industries'])} entries")

    # 显示部分示例
    print("\nSample underlying patterns:")
    for code, patterns in list(mappings['underlying_patterns'].items())[:5]:
        print(f"  {code}: {patterns}")