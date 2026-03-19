"""
Index data module.

This module provides interfaces to fetch index data including:
- Index historical data
- Index realtime quotes
- Index constituents
- Index list
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import IndexFactory
from . import eastmoney, sina  # 触发 Provider 注册


@api_endpoint(IndexFactory)
def get_index_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    interval: Literal["daily", "weekly", "monthly"] = "daily",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get index historical data.

    Args:
        symbol: Index symbol (e.g., '000001' for SSE Composite)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval ('daily', 'weekly', 'monthly')
    """
    pass


@api_endpoint(IndexFactory)
def get_index_realtime_data(
    symbol: str | None = None,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get index realtime quotes.

    Args:
        symbol: Index symbol (optional, if None returns all)
    """
    pass


@api_endpoint(IndexFactory)
def get_index_list(
    category: Literal["cn", "global"] = "cn",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get index list.

    Args:
        category: Index category ('cn' or 'global')
    """
    pass


__all__ = [
    "get_index_hist_data",
    "get_index_realtime_data",
    "get_index_list",
    "IndexFactory",
]
