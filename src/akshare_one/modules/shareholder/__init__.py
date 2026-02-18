"""
Shareholder data module.

This module provides interfaces to fetch shareholder data including:
- Shareholder changes (增减持)
- Top shareholders
- Institution holdings
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import ShareholderFactory


def get_shareholder_changes(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney", "sse"] = "sse",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get shareholder changes (增减持) data.

    Args:
        symbol: Stock symbol (optional, if None returns all)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('sse' recommended for changes)
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sort_by": "change_date"}

    Returns:
        pd.DataFrame: Shareholder changes with columns:
            - symbol: Stock symbol
            - name: Stock name
            - holder_name: Holder name
            - position: Position
            - change_shares: Change in shares
            - reason: Change reason
            - change_date: Change date

    Example:
        >>> df = get_shareholder_changes("600000", start_date="2024-01-01")
        >>> print(df.head())
    """
    from akshare_one.client import apply_data_filter

    provider = ShareholderFactory.get_provider(source=source)
    df = provider.get_shareholder_changes(symbol, start_date, end_date)
    return apply_data_filter(df, columns, row_filter)


def get_top_shareholders(
    symbol: str,
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get top shareholders of a stock.

    Args:
        symbol: Stock symbol
        source: Data source ('eastmoney' recommended)
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sort_by": "holding_pct"}

    Returns:
        pd.DataFrame: Top shareholders with columns:
            - symbol: Stock symbol
            - name: Stock name
            - institution_count: Number of institutions
            - holding_pct: Holding percentage

    Example:
        >>> df = get_top_shareholders("600000")
        >>> print(df.head())
    """
    from akshare_one.client import apply_data_filter

    provider = ShareholderFactory.get_provider(source=source)
    df = provider.get_top_shareholders(symbol)
    return apply_data_filter(df, columns, row_filter)


def get_institution_holdings(
    symbol: str,
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get institution holdings of a stock.

    Args:
        symbol: Stock symbol
        source: Data source ('eastmoney' recommended)
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}

    Returns:
        pd.DataFrame: Institution holdings with columns:
            - symbol: Stock symbol
            - name: Stock name
            - institution_count: Number of institutions
            - holding_pct: Holding percentage
            - float_holding_pct: Percentage of float shares

    Example:
        >>> df = get_institution_holdings("600000")
        >>> print(df.head())
    """
    from akshare_one.client import apply_data_filter

    provider = ShareholderFactory.get_provider(source=source)
    df = provider.get_institution_holdings(symbol)
    return apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_shareholder_changes",
    "get_top_shareholders",
    "get_institution_holdings",
    "ShareholderFactory",
]
