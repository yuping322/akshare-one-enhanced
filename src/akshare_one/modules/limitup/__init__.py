"""
Limit Up/Down (涨停池) data module for PV.LimitUpDown.

This module provides interfaces to fetch limit up/down data including:
- Limit up pool (涨停池)
- Limit down pool (跌停池)
- Limit up/down statistics
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import LimitUpDownFactory


def get_limit_up_pool(
    date: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get limit up pool data.

    Args:
        date: Date in YYYY-MM-DD format
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Standardized limit up pool data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = LimitUpDownFactory.create_router(sources=source)
        df = router.execute("get_limit_up_pool", date)
    else:
        provider = LimitUpDownFactory.get_provider(source=source)
        df = provider.get_limit_up_pool(date)

    return apply_data_filter(df, columns, row_filter)


def get_limit_down_pool(
    date: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get limit down pool data.

    Args:
        date: Date in YYYY-MM-DD format
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Standardized limit down pool data
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = LimitUpDownFactory.create_router(sources=source)
        df = router.execute("get_limit_down_pool", date)
    else:
        provider = LimitUpDownFactory.get_provider(source=source)
        df = provider.get_limit_down_pool(date)

    return apply_data_filter(df, columns, row_filter)


def get_limit_up_stats(
    start_date: str,
    end_date: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get limit up/down statistics.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source
        columns: Columns to return
        row_filter: Row filter config

    Returns:
        pd.DataFrame: Statistics
    """
    from ...client import apply_data_filter

    if isinstance(source, list) or source is None:
        router = LimitUpDownFactory.create_router(sources=source)
        df = router.execute("get_limit_up_stats", start_date, end_date)
    else:
        provider = LimitUpDownFactory.get_provider(source=source)
        df = provider.get_limit_up_stats(start_date, end_date)

    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_limit_up_pool",
    "get_limit_down_pool",
    "get_limit_up_stats",
    "LimitUpDownFactory",
]
