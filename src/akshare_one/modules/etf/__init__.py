"""
ETF (Exchange-Traded Fund) data module.

This module provides interfaces to fetch ETF data including:
- ETF historical data
- ETF realtime quotes
- ETF list and basic info
- Fund manager information
- Fund ratings
"""

from typing import Any, Dict, Literal

import pandas as pd

from .factory import ETFFactory


def get_etf_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    interval: Literal["daily", "weekly", "monthly"] = "daily",
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get ETF historical data.

    Args:
        symbol: ETF symbol (e.g., '159915' for 创业板ETF)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval ('daily', 'weekly', 'monthly')
        source: Data source ('eastmoney' or 'sina')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Standardized historical data with columns:
            - date: Date
            - symbol: ETF symbol
            - open: Opening price
            - high: Highest price
            - low: Lowest price
            - close: Closing price
            - volume: Trading volume
            - amount: Trading amount
            - pct_change: Price change percentage (if available)
            - turnover: Turnover rate (if available)

    Example:
        >>> df = get_etf_hist_data("159915", start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = ETFFactory.get_provider(source=source)
    df = provider.get_etf_hist(symbol, start_date, end_date, interval)
    return provider.apply_data_filter(df, columns, row_filter)


def get_etf_realtime_data(
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get all ETF realtime quotes.

    Args:
        source: Data source ('eastmoney' recommended)
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Realtime ETF data with columns:
            - symbol: ETF symbol
            - name: ETF name
            - price: Current price
            - pct_change: Price change percentage
            - change: Price change amount
            - volume: Trading volume
            - amount: Trading amount
            - open: Opening price
            - high: Highest price
            - low: Lowest price
            - prev_close: Previous close price
            - turnover: Turnover rate

    Example:
        >>> df = get_etf_realtime_data()
        >>> print(df.head())
    """
    provider = ETFFactory.get_provider(source=source)
    df = provider.get_etf_spot()
    return provider.apply_data_filter(df, columns, row_filter)


def get_etf_list(
    category: str = "all",
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get ETF list.

    Args:
        category: ETF category ('all', 'stock', 'bond', 'cross', 'money')
        source: Data source ('eastmoney' or 'sina')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: ETF list with columns:
            - symbol: ETF symbol
            - name: ETF name
            - type: ETF type

    Example:
        >>> df = get_etf_list()
        >>> print(df.head())
    """
    provider = ETFFactory.get_provider(source=source)
    df = provider.get_etf_list(category)
    return provider.apply_data_filter(df, columns, row_filter)


def get_fund_manager_info(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get fund manager information.

    Args:
        source: Data source ('eastmoney' recommended)
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Fund manager data with columns:
            - manager_name: Manager name
            - company: Fund company
            - fund_symbol: Fund symbol
            - fund_name: Fund name
            - tenure_days: Tenure in days
            - aum_billion: Assets under management (billion)
            - best_return_pct: Best return percentage

    Example:
        >>> df = get_fund_manager_info()
        >>> print(df.head())
    """
    provider = ETFFactory.get_provider(source=source)
    df = provider.get_fund_manager()
    return provider.apply_data_filter(df, columns, row_filter)


def get_fund_rating_data(
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get fund ratings.

    Args:
        source: Data source ('eastmoney' recommended)
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Fund rating data with columns:
            - symbol: Fund symbol
            - name: Fund name
            - manager: Fund manager
            - company: Fund company
            - star_count: Number of 5-star ratings
            - sh_securities_rating: Shanghai Securities rating
            - cm_securities_rating: China Merchants Securities rating
            - jian_rating: Jianan rating
            - morningstar_rating: Morningstar rating
            - fee: Fee rate
            - fund_type: Fund type

    Example:
        >>> df = get_fund_rating_data()
        >>> print(df.head())
    """
    provider = ETFFactory.get_provider(source=source)
    df = provider.get_fund_rating()
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_etf_hist_data",
    "get_etf_realtime_data",
    "get_etf_list",
    "get_fund_manager_info",
    "get_fund_rating_data",
    "ETFFactory",
]
