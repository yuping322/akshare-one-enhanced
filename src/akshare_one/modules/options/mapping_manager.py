"""
动态映射表管理器
提供动态加载和更新映射表的功能
"""

import json
import os
from datetime import datetime, timedelta

import akshare as ak


class DynamicMappingManager:
    """动态映射表管理器"""

    def __init__(self, cache_dir: str = "mapping_tables"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
        self._underlying_patterns = None
        self._last_update = None

    def ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def is_cache_expired(self, cache_file: str, days: int = 7) -> bool:
        """检查缓存是否过期"""
        if not os.path.exists(cache_file):
            return True

        file_time = os.path.getmtime(cache_file)
        return datetime.fromtimestamp(file_time) < datetime.now() - timedelta(days=days)

    def generate_underlying_patterns(self) -> dict[str, list[str]]:
        """动态生成底层资产模式映射"""
        mapping = {}

        # 1. 首先尝试从AKShare获取指数信息
        try:
            index_info = ak.index_stock_info()
            if not index_info.empty:
                # 主要指数的映射
                major_indices = {
                    "000300": ["沪深300", "HS300", "300ETF", "沪深300ETF"],
                    "000016": ["上证50", "SZ50", "50ETF", "上证50ETF"],
                    "000905": ["中证500", "ZZ500", "500ETF", "中证500ETF"],
                    "000852": ["中证1000", "ZZ1000", "1000ETF", "中证1000ETF"],
                }

                for code, patterns in major_indices.items():
                    mapping[code] = patterns

                # 尝试从指数成分股中提取更多信息
                for _, row in index_info.head(20).iterrows():  # 只取前20个以避免过多数据
                    idx_code = row["index_code"]
                    display_name = row["display_name"]
                    if idx_code not in mapping:
                        mapping[idx_code] = [display_name]
                    else:
                        mapping[idx_code].append(display_name)

        except Exception as e:
            print(f"Warning: Could not fetch index info: {e}")

        # 2. 尝试获取ETF基金信息
        try:
            # 获取ETF基金列表
            etf_listings = [
                ("510300", "沪深300ETF"),
                ("510050", "上证50ETF"),
                ("510500", "中证500ETF"),
                ("159919", "沪深300ETF"),
                ("159901", "深证100ETF"),
                ("588080", "科创板50ETF"),
                ("159915", "创业板ETF"),
            ]

            for code, name in etf_listings:
                if code not in mapping:
                    mapping[code] = []
                mapping[code].extend([name, name.replace("ETF", ""), name.replace("联接", "")])

        except Exception as e:
            print(f"Warning: Could not fetch ETF info: {e}")

        # 3. 添加常见的股票代码映射
        common_stocks = {
            "000001": ["平安银行", "000001"],
            "600000": ["浦发银行", "600000"],
        }

        for code, patterns in common_stocks.items():
            if code not in mapping:
                mapping[code] = patterns

        return mapping

    def get_underlying_patterns(self) -> dict[str, list[str]]:
        """获取底层资产模式映射，带缓存"""
        cache_file = os.path.join(self.cache_dir, "underlying_patterns.json")

        if self._underlying_patterns is None or self.is_cache_expired(cache_file):
            print("Updating underlying patterns cache...")
            self._underlying_patterns = self.generate_underlying_patterns()

            # 保存到缓存
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(self._underlying_patterns, f, ensure_ascii=False, indent=2)

            self._last_update = datetime.now()

        elif self._underlying_patterns is None:
            # 尝试从缓存加载
            try:
                with open(cache_file, encoding="utf-8") as f:
                    self._underlying_patterns = json.load(f)
            except FileNotFoundError:
                # 如果缓存不存在，生成新的
                self._underlying_patterns = self.generate_underlying_patterns()
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(self._underlying_patterns, f, ensure_ascii=False, indent=2)

        return self._underlying_patterns

    def get_patterns_for_symbol(self, symbol: str) -> list[str]:
        """获取特定符号的匹配模式"""
        patterns = self.get_underlying_patterns()
        return patterns.get(symbol, [symbol])

    def refresh_cache(self):
        """强制刷新缓存"""
        self._underlying_patterns = None
        cache_file = os.path.join(self.cache_dir, "underlying_patterns.json")
        if os.path.exists(cache_file):
            os.remove(cache_file)


# 全局实例
_mapping_manager = DynamicMappingManager()


def get_underlying_patterns() -> dict[str, list[str]]:
    """获取底层资产模式映射"""
    return _mapping_manager.get_underlying_patterns()


def get_patterns_for_symbol(symbol: str) -> list[str]:
    """获取特定符号的匹配模式"""
    return _mapping_manager.get_patterns_for_symbol(symbol)


def refresh_mapping_cache():
    """刷新映射缓存"""
    _mapping_manager.refresh_cache()


if __name__ == "__main__":
    # 测试映射管理器
    manager = DynamicMappingManager()
    patterns = manager.get_underlying_patterns()

    print("Generated underlying patterns:")
    for symbol, pattern_list in list(patterns.items())[:10]:  # 显示前10个
        print(f"  {symbol}: {pattern_list}")

    print(f"\nTotal patterns: {len(patterns)}")
