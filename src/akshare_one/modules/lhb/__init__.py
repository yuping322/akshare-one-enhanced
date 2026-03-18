"""
Dragon Tiger List (龙虎榜) data module for PV.DragonTigerLHB.

This module provides interfaces to fetch dragon tiger list data including:
- Dragon tiger list data (daily trading anomaly data)
- Dragon tiger list summary statistics
- Broker statistics from dragon tiger list
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import DragonTigerFactory


def get_dragon_tiger_list(
    date: str,
    symbol: str | None = None,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get dragon tiger list data.

    Args:
        date: Date in YYYY-MM-DD format
        symbol: Stock symbol (optional, if None returns all stocks)
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Standardized dragon tiger list data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = DragonTigerFactory.create_router(sources=source)
        df = router.execute("get_dragon_tiger_list", date, symbol)
    else:
        provider = DragonTigerFactory.get_provider(source=source)
        df = provider.get_dragon_tiger_list(date, symbol)

    return apply_data_filter(df, columns, row_filter)


def get_dragon_tiger_summary(
    start_date: str,
    end_date: str,
    group_by: Literal["stock", "broker", "reason"] = "stock",
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get dragon tiger list summary statistics.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        group_by: Grouping dimension ('stock', 'broker', or 'reason')
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Summary statistics
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = DragonTigerFactory.create_router(sources=source)
        df = router.execute("get_dragon_tiger_summary", start_date, end_date, group_by)
    else:
        provider = DragonTigerFactory.get_provider(source=source)
        df = provider.get_dragon_tiger_summary(start_date, end_date, group_by)

    return apply_data_filter(df, columns, row_filter)


def get_dragon_tiger_broker_stats(
    start_date: str,
    end_date: str,
    top_n: int = 50,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get broker statistics from dragon tiger list.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        top_n: Number of top brokers to return
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Broker statistics
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = DragonTigerFactory.create_router(sources=source)
        df = router.execute("get_dragon_tiger_broker_stats", start_date, end_date, top_n)
    else:
        provider = DragonTigerFactory.get_provider(source=source)
        df = provider.get_dragon_tiger_broker_stats(start_date, end_date, top_n)

    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_dragon_tiger_list",
    "get_dragon_tiger_summary",
    "get_dragon_tiger_broker_stats",
    "DragonTigerFactory",
]
