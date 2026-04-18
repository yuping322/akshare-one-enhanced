"""
Market data modules for akshare-one.

Refactored architecture:
- core/: Infrastructure (base classes, factories, cache, exceptions, field mapping)
- providers/: Data providers (API wrappers with lightweight transformation)
- calculators/: Computation engines (technical indicators, factors, signals, risk, backtest)
"""

# Core infrastructure only - providers and calculators are imported on demand
# to avoid circular imports and reduce startup time
from .core.base import BaseProvider
from .core.factory import BaseFactory
from .core.router import MultiSourceRouter
from .core.cache import cache as cache_data, clear_cache, smart_cache
from .core.exceptions import (
    DataSourceUnavailableError,
    DataValidationError,
    InvalidParameterError,
    MarketDataError,
    NoDataError,
    RateLimitError,
    UpstreamChangedError,
    handle_upstream_error,
    map_to_standard_exception,
    raise_mapped_exception,
)
from .core.calendar import (
    get_all_trade_days,
    transform_date,
    get_trade_dates_between,
    is_trade_date,
)

__all__ = [
    # Core
    "BaseProvider",
    "BaseFactory",
    "MultiSourceRouter",
    "cache_data",
    "clear_cache",
    "smart_cache",
    "MarketDataError",
    "InvalidParameterError",
    "DataSourceUnavailableError",
    "NoDataError",
    "UpstreamChangedError",
    "RateLimitError",
    "DataValidationError",
    "handle_upstream_error",
    "map_to_standard_exception",
    "raise_mapped_exception",
    "get_all_trade_days",
    "transform_date",
    "get_trade_dates_between",
    "is_trade_date",
]
