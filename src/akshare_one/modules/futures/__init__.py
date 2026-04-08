"""
Futures data module for PV.Futures.

This module provides interfaces to fetch futures data including:
- Historical futures market data
- Realtime futures quotes
- Main contract list
- All futures quotes
"""

from typing import Any, Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import eastmoney, sina
from .base import FuturesDataFactory, FuturesHistoricalFactory, FuturesRealtimeFactory


@api_endpoint(FuturesHistoricalFactory, method_name="get_hist_data")
def get_futures_hist_data(
    symbol: str,
    contract: str = "main",
    interval: Literal["minute", "hour", "day", "week", "month"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get futures historical data.

    Args:
        symbol: Futures symbol (e.g., 'CU', 'AG')
        contract: Contract code or 'main'
        interval: Data interval
        interval_multiplier: Interval multiplier
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(FuturesHistoricalFactory, method_name="get_main_contracts")
def get_futures_main_contracts(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get main futures contracts list.
    """
    pass


@api_endpoint(FuturesRealtimeFactory, method_name="get_current_data")
def get_futures_realtime_data(
    symbol: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get futures realtime quotes.

    Args:
        symbol: Futures symbol (optional)
    """
    pass


@api_endpoint(FuturesRealtimeFactory, method_name="get_all_quotes")
def get_futures_all_quotes(
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get all futures quotes.
    """
    pass


__all__ = [
    "get_futures_hist_data",
    "get_futures_main_contracts",
    "get_futures_realtime_data",
    "get_futures_all_quotes",
    "FuturesHistoricalFactory",
    "FuturesRealtimeFactory",
    "FuturesDataFactory",
]
