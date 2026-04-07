"""
Limit Up/Down (涨跌停) data module for PV.LimitUpDown.

This module provides interfaces to fetch limit up/down data including:
- Daily limit up stock pool
- Daily limit down stock pool
- Limit up/down market statistics
"""

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import LimitUpDownFactory
from . import eastmoney
from . import sina


@api_endpoint(LimitUpDownFactory)
def get_limit_up_pool(
    date: str | None = None,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get limit up pool data.

    Args:
        date: Query date in YYYY-MM-DD format. If None, returns latest.
    """
    pass


@api_endpoint(LimitUpDownFactory)
def get_limit_down_pool(
    date: str | None = None,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get limit down pool data.

    Args:
        date: Query date in YYYY-MM-DD format. If None, returns latest.
    """
    pass


@api_endpoint(LimitUpDownFactory)
def get_limit_up_stats(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get limit up/down statistics.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


__all__ = [
    "get_limit_up_pool",
    "get_limit_down_pool",
    "get_limit_up_stats",
    "LimitUpDownFactory",
]
