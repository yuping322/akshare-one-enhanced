"""
Core infrastructure layer for akshare-one modules.

This package provides the foundational components for all market data providers:
- Base provider class
- Factory pattern implementation
- Multi-source routing
- Caching
- Exception handling
- Trade calendar utilities
- Symbol utilities
- Field mapping and standardization
"""

from .base import BaseProvider, MarketType, apply_data_filter
from .cache import cache, clear_cache, smart_cache
from .calendar import get_all_trade_days, get_trade_dates_between, is_trade_date, transform_date
from .exceptions import (
    DataValidationError,
    DataSourceUnavailableError,
    InvalidParameterError,
    MarketDataError,
    NoDataError,
    RateLimitError,
    UpstreamChangedError,
    handle_upstream_error,
    map_to_standard_exception,
    raise_mapped_exception,
)
from .factory import (
    BaseFactory,
    api_endpoint,
    create_block_deal_router,
    create_dragon_tiger_router,
    create_financial_router,
    create_fundflow_router,
    create_historical_router,
    create_limit_up_down_router,
    create_northbound_router,
    create_realtime_router,
    create_router,
    doc_params,
)
from .router import EmptyDataPolicy, ExecutionResult, MultiSourceRouter
from .symbols import convert_xieqiu_symbol, detect_market, normalize_symbol

__all__ = [
    # Base provider
    "BaseProvider",
    "MarketType",
    "apply_data_filter",
    # Factory
    "BaseFactory",
    "api_endpoint",
    "doc_params",
    "create_router",
    "create_historical_router",
    "create_realtime_router",
    "create_financial_router",
    "create_northbound_router",
    "create_fundflow_router",
    "create_dragon_tiger_router",
    "create_limit_up_down_router",
    "create_block_deal_router",
    # Router
    "MultiSourceRouter",
    "EmptyDataPolicy",
    "ExecutionResult",
    # Cache
    "cache",
    "smart_cache",
    "clear_cache",
    # Exceptions
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
    # Calendar
    "get_all_trade_days",
    "transform_date",
    "get_trade_dates_between",
    "is_trade_date",
    # Symbols
    "convert_xieqiu_symbol",
    "normalize_symbol",
    "detect_market",
]
