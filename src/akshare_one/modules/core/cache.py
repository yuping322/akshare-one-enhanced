"""Cache decorators - memory + parquet + DuckDB persistent cache.

Replaces the old TTLCache-only implementation with a multi-layer cache:
1. Memory (TTLCache) - hot data, fast
2. Parquet + DuckDB - persistent, cross-process, long-term

Usage:
    @cache("stock_daily")
    def get_hist_data(self, symbol, start_date, end_date):
        ...
"""

import os
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import pandas as pd

F = TypeVar("F", bound=Callable[..., Any])

_TABLE_MAP = {
    "realtime_cache": "realtime",
    "futures_realtime_cache": "futures_realtime",
    "options_realtime_cache": "options_realtime",
    "hist_data_cache": "stock_daily",
    "hist_daily_cache": "stock_daily",
    "news_cache": "news",
    "futures_hist_cache": "futures_daily",
    "options_chain_cache": "options_chain",
    "financial_cache": "financial_metrics",
    "info_cache": "securities",
    "insider_cache": "insider_trade",
    "macro_cache": "macro_data",
    "blockdeal_cache": "block_deal",
    "shareholder_cache": "shareholder_top10",
    "dividend_data_cache": "dividend",
    "adjust_factor_cache": "adjust_factor",
    "northbound_cache": "northbound_flow",
    "margin_cache": "margin_data",
    "index_cache": "index_daily",
    "lhbg_cache": "dragon_tiger",
    "pledge_cache": "equity_pledge",
    "restricted_cache": "restricted_release",
    "stock_list_cache": "securities",
    "trade_dates_cache": "trade_days",
    "etf_cache": "etf_daily",
}


def _get_cache_manager():
    from ...cache import get_cache_manager

    return get_cache_manager()


def _get_symbol_normalizer():
    from ...cache import SymbolNormalizer

    return SymbolNormalizer


def _get_stats_collector():
    from ....metrics.stats import get_stats_collector

    return get_stats_collector()


def cache(cache_key: str, key: Callable | None = None) -> Callable[[F], F]:
    """缓存装饰器

    查询路径: Memory → DuckDB(Parquet) → 调用原函数 → 写回 Parquet + Memory
    """
    table_name = _TABLE_MAP.get(cache_key, cache_key.replace("_cache", ""))

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_enabled = os.getenv("AKSHARE_ONE_CACHE_ENABLED", "true").lower() in (
                "1",
                "true",
                "yes",
                "on",
            )
            if not cache_enabled:
                return func(*args, **kwargs)

            stats = _get_stats_collector()
            mgr = _get_cache_manager()
            Normalizer = _get_symbol_normalizer()

            symbol = _extract_symbol(args, kwargs)
            start = _extract_start_date(args, kwargs)
            end = _extract_end_date(args, kwargs)

            if symbol:
                symbol = Normalizer.normalize(symbol)

            mem_key = _make_mem_key(table_name, symbol, start, end)
            with mgr.memory_lock:
                try:
                    result = mgr.memory[mem_key]
                    stats.record_cache_hit(f"{cache_key}_memory")
                    return result.copy()
                except KeyError:
                    stats.record_cache_miss(cache_key)

            df = mgr.engine.query(table_name, symbol, start, end)
            if not df.empty:
                with mgr.memory_lock:
                    mgr.memory[mem_key] = df
                stats.record_cache_hit(f"{cache_key}_persistence")
                return df.copy()

            result = func(*args, **kwargs)

            if isinstance(result, pd.DataFrame) and not result.empty:
                partition = _extract_partition_value(result, table_name, symbol)
                try:
                    mgr.store.write(table_name, result, partition)
                    with mgr.memory_lock:
                        mgr.memory[mem_key] = result
                except Exception as e:
                    import logging

                    logging.getLogger(__name__).warning(f"Cache write failed: {e}")

            return result.copy() if isinstance(result, pd.DataFrame) else result

        return wrapper  # type: ignore

    return decorator


def smart_cache(
    realtime_key: str,
    daily_key: str,
    interval_attr: str = "interval",
    key: Callable | None = None,
) -> Callable[[F], F]:
    """智能缓存：根据 interval 选择不同 TTL"""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            use_daily = True
            if args and hasattr(args[0], interval_attr):
                interval = getattr(args[0], interval_attr, "day").lower()
                if interval in ("minute", "hour"):
                    use_daily = False

            cache_key = daily_key if use_daily else realtime_key
            return cache(cache_key, key=key)(func)(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def clear_cache(cache_key: str | None = None) -> None:
    """清除缓存"""
    mgr = _get_cache_manager()
    if cache_key:
        table = _TABLE_MAP.get(cache_key, cache_key.replace("_cache", ""))
        mgr.invalidate(table)
    else:
        mgr.invalidate()


def _extract_symbol(args: tuple, kwargs: dict) -> str | None:
    for k in ("symbol", "code", "underlying_symbol"):
        if k in kwargs:
            return str(kwargs[k])
    return None


def _extract_start_date(args: tuple, kwargs: dict) -> str | None:
    for k in ("start_date", "start"):
        if k in kwargs:
            return str(kwargs[k])
    return None


def _extract_end_date(args: tuple, kwargs: dict) -> str | None:
    for k in ("end_date", "end"):
        if k in kwargs:
            return str(kwargs[k])
    return None


def _extract_partition_value(
    df: pd.DataFrame,
    table: str,
    symbol: str | None,
) -> str | None:
    from ...cache.schema import SCHEMA_REGISTRY

    schema = SCHEMA_REGISTRY.get_or_none(table)
    if not schema or not schema.partition_by:
        return None

    col = schema.partition_by
    if col == "date" and "date" in df.columns:
        return str(df["date"].iloc[0])
    if col == "week" and "date" in df.columns:
        date = pd.to_datetime(df["date"].iloc[0])
        return date.strftime("%Y-W%W")
    if col == "symbol" and symbol:
        return symbol

    return None


def _make_mem_key(
    table: str,
    symbol: str | None,
    start: str | None,
    end: str | None,
) -> str:
    parts = [table]
    if symbol:
        parts.append(symbol)
    if start:
        parts.append(start)
    if end:
        parts.append(end)
    return ":".join(parts)
