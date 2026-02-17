#!/usr/bin/env python3
"""
全面的映射表生成器
生成包含所有映射信息的CSV文件
"""

import pandas as pd
import akshare as ak
import os
from datetime import datetime
import json


def generate_full_mapping_tables():
    """生成全面的映射表"""
    print("Generating full mapping tables...")

    mappings = {}

    # 1. 股票代码-名称映射
    print("Fetching stock mappings...")
    try:
        # 深圳证券交易所股票信息
        sz_info = ak.stock_info_sz_name_code()
        sz_mapping = {}
        if not sz_info.empty:
            for _, row in sz_info.iterrows():
                code = row['A股代码']
                name = row['A股简称']
                if pd.notna(code) and pd.notna(name):
                    sz_mapping[str(code)] = name

        # 上海证券交易所股票信息
        sh_info = ak.stock_info_sh_name_code()
        sh_mapping = {}
        if not sh_info.empty:
            for _, row in sh_info.iterrows():
                code = row['证券代码']
                name = row['证券简称']
                if pd.notna(code) and pd.notna(name):
                    sh_mapping[str(code)] = name

        # 北京证券交易所股票信息
        bj_info = ak.stock_info_bj_name_code()
        bj_mapping = {}
        if not bj_info.empty:
            for _, row in bj_info.iterrows():
                code = row['证券代码']
                name = row['证券简称']
                if pd.notna(code) and pd.notna(name):
                    bj_mapping[str(code)] = name

        # 合并所有股票映射
        stock_mapping = {**sz_mapping, **sh_mapping, **bj_mapping}
        mappings['stock_code_to_name'] = stock_mapping

    except Exception as e:
        print(f"Error fetching stock mappings: {e}")
        # 默认股票映射
        mappings['stock_code_to_name'] = {
            "000001": "平安银行",
            "600000": "浦发银行",
            "600036": "招商银行",
            "000002": "万科A",
        }

    # 2. 指数代码-名称映射
    print("Fetching index mappings...")
    try:
        index_info = ak.index_stock_info()
        index_mapping = {}
        if not index_info.empty:
            for _, row in index_info.iterrows():
                code = row['index_code']
                name = row['display_name']
                if pd.notna(code) and pd.notna(name):
                    index_mapping[code] = name
        mappings['index_code_to_name'] = index_mapping
    except Exception as e:
        print(f"Error fetching index mappings: {e}")
        mappings['index_code_to_name'] = {
            "000300": "沪深300",
            "000016": "上证50",
            "000905": "中证500",
            "000001": "上证指数",
        }

    # 3. ETF基金映射
    print("Fetching ETF mappings...")
    try:
        # 获取ETF基金信息
        etf_fund = ak.fund_etf_fund_info_em(explode_factor="1")
        etf_mapping = {}
        if not etf_fund.empty:
            # 筛选主要ETF
            major_etfs = etf_fund[
                etf_fund['基金简称'].str.contains(
                    '300|50|500|1000|创业板|科创|消费|医药|科技|金融|红利|价值|成长|沪深',
                    na=False, regex=True
                )
            ].head(100)  # 限制数量

            for _, row in major_etfs.iterrows():
                code = row.get('基金代码', '')
                name = row.get('基金简称', '')
                if code and name:
                    etf_mapping[code] = name
        mappings['etf_code_to_name'] = etf_mapping
    except Exception as e:
        print(f"Error fetching ETF mappings: {e}")
        mappings['etf_code_to_name'] = {
            "510300": "沪深300ETF",
            "510050": "上证50ETF",
            "510500": "中证500ETF",
            "159919": "沪深300ETF",
            "588080": "科创板50ETF",
        }

    # 4. 行业板块映射
    print("Fetching industry mappings...")
    try:
        industry_names = ak.stock_board_industry_name_em()
        industry_mapping = {}
        if not industry_names.empty:
            for _, row in industry_names.iterrows():
                code = row.get('板块代码', '')
                name = row.get('板块名称', '')
                if code and name:
                    industry_mapping[code] = name
        mappings['industry_code_to_name'] = industry_mapping
    except Exception as e:
        print(f"Error fetching industry mappings: {e}")
        mappings['industry_code_to_name'] = {
            "BK0473": "证券",
            "BK0474": "银行",
            "BK0525": "保险",
            "BK0475": "多元金融",
        }

    # 5. 期权底层资产映射（用于期权模块）
    print("Fetching option underlying mappings...")
    try:
        # 主要期权底层资产
        option_underlyings = {
            "510300": ["沪深300ETF", "沪深300", "300ETF", "HS300ETF"],
            "510050": ["上证50ETF", "上证50", "50ETF", "SZ50ETF"],
            "159919": ["沪深300ETF", "沪深300", "300ETF", "HS300ETF"],
            "159901": ["深100ETF", "深证100", "SZ100ETF"],
            "159915": ["创业板ETF", "创业板", "CYBETF"],
            "588080": ["科创50ETF", "科创50", "KC50ETF"],
            "000300": ["沪深300", "HS300", "300Index"],
            "000016": ["上证50", "SZ50", "50Index"],
        }
        mappings['option_underlying_patterns'] = option_underlyings
    except Exception as e:
        print(f"Error generating option underlying mappings: {e}")
        mappings['option_underlying_patterns'] = {
            "510300": ["沪深300ETF", "沪深300"],
            "510050": ["上证50ETF", "上证50"],
        }

    # 6. 期权品种映射
    try:
        option_symbols = ak.option_comm_symbol()
        option_mapping = {}
        if not option_symbols.empty:
            for _, row in option_symbols.iterrows():
                code = row['品种代码']
                name = row['品种名称']
                if pd.notna(code) and pd.notna(name):
                    option_mapping[code] = name
        mappings['option_symbol_to_name'] = option_mapping
    except Exception as e:
        print(f"Error fetching option symbol mappings: {e}")
        mappings['option_symbol_to_name'] = {
            "au_o": "黄金期权",
            "ag_o": "白银期权",
            "cu_o": "铜期权",
        }

    return mappings


def save_mappings_as_csv(mappings):
    """将映射表保存为CSV文件"""
    print("Saving mappings to CSV files...")

    os.makedirs("mappings", exist_ok=True)

    for name, mapping in mappings.items():
        if isinstance(mapping, dict):
            # 将字典转换为DataFrame
            df = pd.DataFrame(list(mapping.items()), columns=['code', 'name'])
            csv_path = f"mappings/{name}.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"Saved {name} mapping with {len(mapping)} entries to {csv_path}")

    # 同时保存一个合并的大映射表
    combined_data = []
    for table_name, mapping in mappings.items():
        if isinstance(mapping, dict):
            for code, name in mapping.items():
                combined_data.append({
                    'table': table_name,
                    'code': code,
                    'name': name
                })

    combined_df = pd.DataFrame(combined_data)
    combined_csv_path = "mappings/full_combined_mapping.csv"
    combined_df.to_csv(combined_csv_path, index=False, encoding='utf-8-sig')
    print(f"Saved combined mapping with {len(combined_data)} entries to {combined_csv_path}")


def save_mappings_as_json(mappings):
    """将映射表保存为JSON文件"""
    print("Saving mappings to JSON files...")

    os.makedirs("mappings", exist_ok=True)

    for name, mapping in mappings.items():
        json_path = f"mappings/{name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        print(f"Saved {name} mapping to {json_path}")


def load_mapping_from_csv(table_name):
    """从CSV加载特定映射表"""
    csv_path = f"mappings/{table_name}.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        return dict(zip(df['code'], df['name']))
    return {}


def load_mapping_from_json(table_name):
    """从JSON加载特定映射表"""
    json_path = f"mappings/{table_name}.json"
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def create_mapping_utils():
    """创建映射工具类"""
    util_code = '''"""
映射工具类
提供便捷的映射查询功能
"""

import pandas as pd
import os
from typing import Dict, List, Optional


class MappingUtils:
    """映射工具类"""

    def __init__(self, mappings_dir="mappings"):
        self.mappings_dir = mappings_dir
        self._mappings = {}

    def get_mapping(self, table_name: str) -> Dict[str, str]:
        """获取指定映射表"""
        if table_name not in self._mappings:
            csv_path = os.path.join(self.mappings_dir, f"{table_name}.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                self._mappings[table_name] = dict(zip(df['code'], df['name']))
            else:
                self._mappings[table_name] = {}
        return self._mappings[table_name]

    def get_name_by_code(self, table_name: str, code: str) -> Optional[str]:
        """根据代码获取名称"""
        mapping = self.get_mapping(table_name)
        return mapping.get(code)

    def get_all_codes(self, table_name: str) -> List[str]:
        """获取所有代码"""
        mapping = self.get_mapping(table_name)
        return list(mapping.keys())

    def get_all_names(self, table_name: str) -> List[str]:
        """获取所有名称"""
        mapping = self.get_mapping(table_name)
        return list(mapping.values())

    def search_by_name(self, table_name: str, name_pattern: str) -> Dict[str, str]:
        """根据名称模式搜索"""
        mapping = self.get_mapping(table_name)
        results = {}
        for code, name in mapping.items():
            if name_pattern.lower() in name.lower():
                results[code] = name
        return results


# 全局实例
_mapping_utils = MappingUtils()


def get_name_by_code(table_name: str, code: str) -> Optional[str]:
    """根据代码获取名称的便捷函数"""
    return _mapping_utils.get_name_by_code(table_name, code)


def search_by_name(table_name: str, name_pattern: str) -> Dict[str, str]:
    """根据名称模式搜索的便捷函数"""
    return _mapping_utils.search_by_name(table_name, name_pattern)


def get_all_codes(table_name: str) -> List[str]:
    """获取所有代码的便捷函数"""
    return _mapping_utils.get_all_codes(table_name)


def get_stock_name(stock_code: str) -> Optional[str]:
    """获取股票名称"""
    return get_name_by_code('stock_code_to_name', stock_code)


def get_index_name(index_code: str) -> Optional[str]:
    """获取指数名称"""
    return get_name_by_code('index_code_to_name', index_code)


def get_etf_name(etf_code: str) -> Optional[str]:
    """获取ETF名称"""
    return get_name_by_code('etf_code_to_name', etf_code)


def get_industry_name(industry_code: str) -> Optional[str]:
    """获取行业名称"""
    return get_name_by_code('industry_code_to_name', industry_code)


def get_option_underlying_patterns(underlying_code: str) -> List[str]:
    """获取期权底层资产匹配模式"""
    mapping = _mapping_utils.get_mapping('option_underlying_patterns')
    return mapping.get(underlying_code, [underlying_code])


# 预加载常用映射
def preload_mappings():
    """预加载常用映射表"""
    _mapping_utils.get_mapping('stock_code_to_name')
    _mapping_utils.get_mapping('index_code_to_name')
    _mapping_utils.get_mapping('etf_code_to_name')
    _mapping_utils.get_mapping('industry_code_to_name')
    _mapping_utils.get_mapping('option_underlying_patterns')


if __name__ == "__main__":
    # 测试映射工具
    preload_mappings()

    print("Testing mapping utilities:")
    print(f"Stock 000001: {get_stock_name('000001')}")
    print(f"Index 000300: {get_index_name('000300')}")
    print(f"ETF 510300: {get_etf_name('510300')}")
    print(f"Searching '银行': {search_by_name('stock_code_to_name', '银行')}")
'''

    with open("mappings/mapping_utils.py", "w", encoding="utf-8") as f:
        f.write(util_code)

    print("Created mapping utilities module")


def main():
    """主函数"""
    print("Starting full mapping generation...")

    # 生成映射表
    mappings = generate_full_mapping_tables()

    # 保存为CSV
    save_mappings_as_csv(mappings)

    # 保存为JSON
    save_mappings_as_json(mappings)

    # 创建映射工具类
    create_mapping_utils()

    print("\\nMapping generation completed!")
    print("Files created in 'mappings/' directory:")
    for name in mappings.keys():
        print(f"  - {name}.csv")
        print(f"  - {name}.json")
    print("  - full_combined_mapping.csv")
    print("  - mapping_utils.py")


if __name__ == "__main__":
    main()