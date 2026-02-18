import os
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from cachetools import TTLCache, cached
from ..metrics import get_stats_collector

F = TypeVar("F", bound=Callable[..., Any])

# 缓存配置
CACHE_CONFIG: dict[str, TTLCache[Any, Any]] = {
    # 实时数据 - 短缓存
    "realtime_cache": TTLCache(maxsize=500, ttl=60),  # 实时数据缓存1分钟
    "futures_realtime_cache": TTLCache(maxsize=500, ttl=60),  # 期货实时数据缓存1分钟
    "options_realtime_cache": TTLCache(maxsize=500, ttl=60),  # 期权实时数据缓存1分钟
    # 小时级缓存 - 频繁变化的数据
    "hist_data_cache": TTLCache(maxsize=1000, ttl=3600),  # 历史数据缓存1小时
    "news_cache": TTLCache(maxsize=500, ttl=3600),  # 新闻数据缓存1小时
    "futures_hist_cache": TTLCache(maxsize=1000, ttl=3600),  # 期货历史数据缓存1小时
    "options_chain_cache": TTLCache(maxsize=1000, ttl=3600),  # 期权链数据缓存1小时
    # 天级缓存 - 日终数据（收盘后不再变化）
    "hist_daily_cache": TTLCache(maxsize=2000, ttl=86400),  # 日线历史数据缓存24小时
    "financial_cache": TTLCache(maxsize=500, ttl=86400),  # 财务数据缓存24小时
    "info_cache": TTLCache(maxsize=500, ttl=86400),  # 信息数据缓存24小时
    "insider_cache": TTLCache(maxsize=500, ttl=86400),  # 内部交易数据缓存24小时
    # 长期缓存 - 不常变化的数据
    "stock_list_cache": TTLCache(maxsize=100, ttl=604800),  # 股票列表缓存7天
}


def cache(cache_key: str, key: Callable[..., Any] | None = None) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_enabled = os.getenv("AKSHARE_ONE_CACHE_ENABLED", "true").lower() in (
                "1",
                "true",
                "yes",
                "on",
            )

            if cache_enabled:
                if cache_key not in CACHE_CONFIG:
                    raise KeyError(
                        f"Cache configuration '{cache_key}' not found. Available keys: {list(CACHE_CONFIG.keys())}"
                    )

                # 获取统计收集器
                stats_collector = get_stats_collector()

                try:
                    if key is not None:
                        result = cached(CACHE_CONFIG[cache_key], key=key)(func)(*args, **kwargs)
                        stats_collector.record_cache_hit(cache_key)
                        return result
                    else:
                        result = cached(CACHE_CONFIG[cache_key])(func)(*args, **kwargs)
                        stats_collector.record_cache_hit(cache_key)
                        return result
                except KeyError:
                    # 缓存未命中
                    stats_collector.record_cache_miss(cache_key)
                    return func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def smart_cache(
    realtime_key: str,
    daily_key: str,
    interval_attr: str = "interval",
    key: Callable[..., Any] | None = None,
) -> Callable[[F], F]:
    """Smart cache decorator that chooses cache based on data interval.

    For day/week/month/year intervals, uses daily cache (24h TTL).
    For minute/hour intervals, uses realtime cache (1h TTL).

    Args:
        realtime_key: Cache key for high-frequency data (minute/hour)
        daily_key: Cache key for daily+ data (day/week/month/year)
        interval_attr: Attribute name to check for interval type
        key: Optional custom cache key function
    """

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

            # Determine which cache to use based on interval
            # Check args[0] (self) for interval attribute
            use_daily_cache = True
            if args and hasattr(args[0], interval_attr):
                interval = getattr(args[0], interval_attr, "day").lower()
                if interval in ("minute", "hour"):
                    use_daily_cache = False

            cache_key = daily_key if use_daily_cache else realtime_key

            if cache_key not in CACHE_CONFIG:
                raise KeyError(
                    f"Cache configuration '{cache_key}' not found. Available keys: {list(CACHE_CONFIG.keys())}"
                )

            if key is not None:
                return cached(CACHE_CONFIG[cache_key], key=key)(func)(*args, **kwargs)
            else:
                return cached(CACHE_CONFIG[cache_key])(func)(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
