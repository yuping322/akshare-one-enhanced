"""
ETF (Exchange-Traded Fund) data module.

This module provides interfaces to fetch ETF data including:
- ETF historical data
- ETF realtime quotes
- ETF list and basic info
- Fund manager information
- Fund ratings
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import ETFFactory
from . import eastmoney, sina  # 触发 Provider 注册


@api_endpoint(ETFFactory)
def get_etf_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    interval: Literal["daily", "weekly", "monthly"] = "daily",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ETF historical data.

    Args:
        symbol: ETF symbol (e.g., '159915' for 创业板ETF)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval ('daily', 'weekly', 'monthly')
    """
    pass


@api_endpoint(ETFFactory)
def get_etf_realtime_data(
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get all ETF realtime quotes.
    """
    pass


@api_endpoint(ETFFactory)
def get_etf_list(
    category: str = "all",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get ETF list.

    Args:
        category: ETF category
    """
    pass


__all__ = [
    "get_etf_hist_data",
    "get_etf_realtime_data",
    "get_etf_list",
    "ETFFactory",
]
