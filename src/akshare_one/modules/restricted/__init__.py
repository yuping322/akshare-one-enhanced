"""
Restricted Release (限售解禁) data module for PV.RestrictedRelease.

This module provides interfaces to fetch restricted stock release data including:
- Restricted release data (限售解禁数据) - detailed release information
- Restricted release calendar (解禁日历) - aggregated release schedule
"""

from typing import Any, Dict, Literal, Optional

import pandas as pd

from .factory import RestrictedReleaseFactory


def get_restricted_release(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get restricted stock release data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Standardized restricted release data with columns:
            - symbol: Stock symbol
            - release_date: Release date (YYYY-MM-DD)
            - release_shares: Released shares (股)
            - release_value: Released market value (元)
            - release_type: Release type
            - shareholder_name: Shareholder name

    Example:
        >>> # Get release data for a specific stock
        >>> df = get_restricted_release("600000", start_date="2024-01-01")
        >>> print(df.head())
        >>>
        >>> # Get release data for all stocks
        >>> df = get_restricted_release(start_date="2024-01-01", end_date="2024-12-31")
        >>> print(df.head())
    """
    provider = RestrictedReleaseFactory.get_provider(source=source)
    df = provider.get_restricted_release(symbol, start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_restricted_release_calendar(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get restricted stock release calendar.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Calendar data with columns:
            - date: Release date (YYYY-MM-DD)
            - release_stock_count: Number of stocks with releases
            - total_release_value: Total release market value (元)

    Example:
        >>> # Get release calendar for 2024
        >>> df = get_restricted_release_calendar("2024-01-01", "2024-12-31")
        >>> print(df.head())
    """
    provider = RestrictedReleaseFactory.get_provider(source=source)
    df = provider.get_restricted_release_calendar(start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_restricted_release",
    "get_restricted_release_calendar",
    "RestrictedReleaseFactory",
]
