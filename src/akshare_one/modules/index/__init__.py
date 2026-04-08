"""
Index (指数) data module for PV.Index.

This module provides interfaces to fetch index data including:
- Index historical price data
- Index realtime quotes
- Index listings (CN, HK, US, global)
- Index constituents and weights
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import IndexFactory
from . import eastmoney, sina, lixinger


@api_endpoint(IndexFactory)
def get_index_hist(
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
        symbol: Index symbol (e.g., '000001')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval
    """
    pass


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
    pass


@api_endpoint(IndexFactory)
def get_index_realtime(
    symbol: str | None = None,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get index realtime quotes.

    Args:
        symbol: Index symbol. If None, returns latest for all indices.
    """
    pass


@api_endpoint(IndexFactory)
def get_index_realtime_data(
    symbol: str | None = None,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    pass


@api_endpoint(IndexFactory)
def get_index_list(
    category: Literal["cn", "hk", "us", "global"] = "cn",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get index list.

    Args:
        category: Index category ('cn', 'hk', 'us', 'global')
    """
    pass


@api_endpoint(IndexFactory)
def get_index_constituents(
    symbol: str,
    include_weight: bool = True,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get index constituent stocks.

    Args:
        symbol: Index symbol
        include_weight: Whether to include constituent weights
    """
    pass


__all__ = [
    "get_index_hist",
    "get_index_hist_data",
    "get_index_realtime",
    "get_index_realtime_data",
    "get_index_list",
    "get_index_constituents",
    "IndexFactory",
]
