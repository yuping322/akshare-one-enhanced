"""
Dragon Tiger List (龙虎榜) data module for PV.DragonTigerLHB.

This module provides interfaces to fetch dragon tiger list data including:
- Dragon tiger list data (daily trading anomaly data)
- Dragon tiger list summary statistics
- Broker statistics from dragon tiger list
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import doc_params
from .factory import DragonTigerFactory


@doc_params
def get_dragon_tiger_list(
    date: str,
    symbol: str | None = None,
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get dragon tiger list data.

    Args:
        date: Date in YYYY-MM-DD format
        symbol: Stock symbol (optional, if None returns all stocks)
    """
    return DragonTigerFactory.call_provider_method(
        "get_dragon_tiger_list",
        date,
        symbol,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_dragon_tiger_summary(
    start_date: str,
    end_date: str,
    group_by: Literal["stock", "broker", "reason"] = "stock",
    source: SourceType = None,
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get dragon tiger list summary statistics.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        group_by: Grouping dimension ('stock', 'broker', or 'reason')
    """
    return DragonTigerFactory.call_provider_method(
        "get_dragon_tiger_summary",
        start_date,
        end_date,
        group_by,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


@doc_params
def get_dragon_tiger_broker_stats(
    start_date: str,
    end_date: str,
    top_n: int = 50,
    source: SourceType = None,
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
    return DragonTigerFactory.call_provider_method(
        "get_dragon_tiger_broker_stats",
        start_date,
        end_date,
        top_n,
        source=source,
        columns=columns,
        row_filter=row_filter,
    )


__all__ = [
    "get_dragon_tiger_list",
    "get_dragon_tiger_summary",
    "get_dragon_tiger_broker_stats",
    "DragonTigerFactory",
]
