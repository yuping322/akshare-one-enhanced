"""
Index data module.

This module provides interfaces to fetch index data including:
- Index historical data
- Index realtime quotes
- Index constituents
- Index list
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import IndexFactory


def get_index_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    interval: Literal["daily", "weekly", "monthly"] = "daily",
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get index historical data.

    Args:
        symbol: Index symbol (e.g., '000001' for SSE Composite, '399001' for SZSE Component)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval ('daily', 'weekly', 'monthly')
        source: Data source ('eastmoney' or 'sina')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Standardized historical data with columns:
            - date: Date
            - symbol: Index symbol
            - open: Opening value
            - high: Highest value
            - low: Lowest value
            - close: Closing value
            - volume: Trading volume
            - amount: Trading amount
            - pct_change: Change percentage (if available)
            - turnover: Turnover rate (if available)

    Example:
        >>> df = get_index_hist_data("000001", start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = IndexFactory.get_provider(source=source)
    df = provider.get_index_hist(symbol, start_date, end_date, interval)
    return provider.apply_data_filter(df, columns, row_filter)


def get_index_realtime_data(
    symbol: str | None = None,
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get index realtime quotes.

    Args:
        symbol: Index symbol (optional, if None returns all)
        source: Data source ('eastmoney' or 'sina')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Realtime index data with columns:
            - symbol: Index symbol
            - name: Index name
            - value: Current value
            - pct_change: Change percentage
            - change: Change amount
            - volume: Trading volume (if available)
            - amount: Trading amount (if available)

    Example:
        >>> df = get_index_realtime_data()
        >>> print(df.head())
    """
    provider = IndexFactory.get_provider(source=source)
    df = provider.get_index_realtime(symbol)
    return provider.apply_data_filter(df, columns, row_filter)


def get_index_list(
    category: Literal["cn", "global"] = "cn",
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get index list.

    Args:
        category: Index category ('cn' for Chinese indices, 'global' for global indices)
        source: Data source ('eastmoney' or 'sina')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Index list with columns:
            - symbol: Index symbol
            - name: Index name
            - type: Index type

    Example:
        >>> df = get_index_list(category="cn")
        >>> print(df.head())
    """
    provider = IndexFactory.get_provider(source=source)
    df = provider.get_index_list(category)
    return provider.apply_data_filter(df, columns, row_filter)


def get_index_constituents(
    symbol: str,
    include_weight: bool = True,
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get index constituent stocks.

    Args:
        symbol: Index symbol (e.g., '000300' for CSI 300)
        include_weight: Whether to include weight information
        source: Data source ('eastmoney' or 'sina')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Constituent stocks with columns:
            - symbol: Stock symbol
            - name: Stock name
            - weight: Weight in index (if include_weight=True)

    Example:
        >>> df = get_index_constituents("000300")
        >>> print(df.head())
    """
    provider = IndexFactory.get_provider(source=source)
    df = provider.get_index_constituents(symbol, include_weight)
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_index_hist_data",
    "get_index_realtime_data",
    "get_index_list",
    "get_index_constituents",
    "IndexFactory",
]
