"""
src/akshare_one/jq_compat/cache.py
JQ-compatible caching and memory management.
"""

import logging
import pandas as pd
import threading
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class CurrentDataCache:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache = {}
                    cls._instance._timestamps = {}
                    cls._instance._ttl_seconds = 60
        return cls._instance

    def get(self, code: str, bt_strategy=None):
        now = datetime.now()
        ts = self._timestamps.get(code)
        if ts and (now - ts).total_seconds() < self._ttl_seconds:
            return self._cache[code]
        from .market import get_detailed_quote
        data = get_detailed_quote(code)
        self._cache[code] = data
        self._timestamps[code] = now
        return data


def get_current_data_cached(code: str, bt_strategy=None):
    """Get current data with cache. JQ-compatible."""
    return CurrentDataCache().get(code, bt_strategy)


def get_current_data_batch(codes: List[str], bt_strategy=None, use_cache: bool = True) -> Dict[str, Any]:
    """Get current data for multiple securities. JQ-compatible."""
    if use_cache:
        return {s: get_current_data_cached(s, bt_strategy) for s in codes}
    from .market import get_detailed_quote
    return {s: get_detailed_quote(s) for s in codes}


class BatchDataLoader:
    def load_stocks(self, symbols, start_date, end_date, fields=None, adjust="qfq"):
        """Load historical data for multiple stocks."""
        from .market import get_price
        return {s: get_price(s, start_date=start_date, end_date=end_date,
                             fields=fields, fq=adjust) for s in symbols}


def preload_data_for_strategy(stock_pool, start_date, end_date):
    """Preload data for strategy. JQ-compatible."""
    return BatchDataLoader().load_stocks(stock_pool, start_date, end_date)


@lru_cache(maxsize=1000)
def cached_get_security_info(code: str):
    """Get security info with LRU cache. JQ-compatible."""
    from .securities import get_security_info
    return get_security_info(code)


@lru_cache(maxsize=200)
def cached_get_index_stocks(index_code: str, date: Optional[str] = None):
    """Get index constituent stocks with cache. JQ-compatible."""
    try:
        import akshare as ak
        code = index_code.split(".")[0]
        df = ak.index_stock_cons(symbol=code)
        if df is None or df.empty:
            return []
        col = next((c for c in ["品种代码", "成分券代码", "code"] if c in df.columns), None)
        if not col:
            return []
        stocks = df[col].astype(str).str.zfill(6).tolist()
        return [f"{s}.XSHG" if s.startswith("6") else f"{s}.XSHE" for s in stocks]
    except Exception as e:
        logger.warning(f"cached_get_index_stocks failed for '{index_code}': {e}")
        return []


def get_memory_usage() -> Dict[str, float]:
    """Get current process memory usage. JQ-compatible."""
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return {
            "rss": process.memory_info().rss / 1024 / 1024,
            "percent": process.memory_percent(),
        }
    except ImportError:
        return {}


def cleanup_memory():
    """Clear caches and run GC. JQ-compatible."""
    CurrentDataCache._instance = None
    cached_get_security_info.cache_clear()
    cached_get_index_stocks.cache_clear()
    import gc
    gc.collect()


def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    """Downcast numeric columns to reduce memory. JQ-compatible."""
    for col in df.columns:
        if df[col].dtype == "float64":
            df[col] = pd.to_numeric(df[col], downcast="float")
        elif df[col].dtype == "int64":
            df[col] = pd.to_numeric(df[col], downcast="integer")
    return df


class DataPreloader:
    """Preload data for strategy execution. JQ-compatible."""

    def preload_market_data(self, symbols, start_date, end_date):
        self.data = preload_data_for_strategy(symbols, start_date, end_date)

    def preload_fundamentals(self, symbols, date=None):
        from .market import get_valuation
        self.fundamentals = get_valuation(symbols, date=date)

    def preload_index_stocks(self, index_codes):
        self.index_stocks = {idx: cached_get_index_stocks(idx) for idx in index_codes}


def warm_up_cache(symbols: List[str], date: Optional[str] = None):
    """Warm up cache by preloading data. JQ-compatible."""
    logger.info(f"Warming up cache for {len(symbols)} symbols")
    for sym in symbols:
        try:
            get_current_data_cached(sym)
        except Exception as e:
            logger.warning(f"warm_up_cache failed for '{sym}': {e}")


def batch_get_fundamentals(query_obj, symbols: List[str], date: Optional[str] = None) -> pd.DataFrame:
    """Batch get fundamentals. JQ-compatible."""
    from .market import get_valuation
    return get_valuation(symbols, date=date)


__all__ = [
    "CurrentDataCache", "get_current_data_cached", "get_current_data_batch",
    "BatchDataLoader", "preload_data_for_strategy", "optimize_dataframe_memory",
    "DataPreloader", "warm_up_cache", "get_memory_usage", "cleanup_memory",
    "cached_get_security_info", "cached_get_index_stocks", "batch_get_fundamentals",
]
