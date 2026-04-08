"""
Dragon Tiger List (龙虎榜) data module for PV.DragonTiger.

This module provides interfaces to fetch dragon tiger list data including:
- Daily dragon tiger list transaction details
- Dragon tiger list summary statistics
- Broker (营业部) statistics and rankings
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from .base import DragonTigerFactory
from . import eastmoney
from . import sina


@api_endpoint(DragonTigerFactory)
def get_dragon_tiger_list(
    date: str | None = None,
    symbol: str | None = None,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get dragon tiger list transaction details.

    Args:
        date: Query date in YYYY-MM-DD format. If None, returns latest.
        symbol: Stock symbol. If None, returns all stocks for the date.
    """
    pass


@api_endpoint(DragonTigerFactory)
def get_dragon_tiger_summary(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    group_by: Literal["date", "stock", "broker"] = "date",
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get dragon tiger list summary statistics.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        group_by: Grouping dimension
    """
    pass


@api_endpoint(DragonTigerFactory)
def get_dragon_tiger_broker_stats(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    top_n: int = 100,
    source: SourceType = "eastmoney",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get broker statistics from dragon tiger list.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        top_n: Number of top brokers to return
    """
    pass


__all__ = [
    "get_dragon_tiger_list",
    "get_dragon_tiger_summary",
    "get_dragon_tiger_broker_stats",
    "DragonTigerFactory",
]
