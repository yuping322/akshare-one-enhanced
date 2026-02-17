"""
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
                # 读取CSV时保持代码为字符串格式
                df = pd.read_csv(csv_path, encoding='utf-8-sig', dtype={'code': str})

                # 处理数值转为字符串的情况（如股票代码）
                processed_mapping = {}
                for code, name in zip(df['code'], df['name']):
                    # 确保股票代码是6位数字格式
                    str_code = str(code).strip()
                    if str_code.isdigit() and len(str_code) < 6:
                        # 补齐到6位
                        str_code = str_code.zfill(6)
                    processed_mapping[str_code] = name

                self._mappings[table_name] = processed_mapping
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
