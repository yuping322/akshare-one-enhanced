"""
Goodwill (商誉) data module for PV.Goodwill.

This module provides interfaces to fetch goodwill data including:
- Goodwill data (商誉数据) - balance and ratios
- Goodwill impairment expectations (商誉减值预期) - risk assessment
- Goodwill by industry (行业商誉统计) - industry aggregation
"""

from typing import Any, Dict, Literal, Optional

import pandas as pd

from .factory import GoodwillFactory


def get_goodwill_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get goodwill data.

    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Standardized goodwill data with columns:
            - symbol: Stock symbol
            - report_date: Report date (YYYY-MM-DD)
            - goodwill_balance: Goodwill balance (元)
            - goodwill_ratio: Goodwill to net assets ratio (%)
            - goodwill_impairment: Goodwill impairment (元)

    Example:
        >>> # Get goodwill data for a specific stock
        >>> df = get_goodwill_data("600000", start_date="2024-01-01")
        >>> print(df.head())
        >>>
        >>> # Get goodwill data for all stocks
        >>> df = get_goodwill_data(start_date="2024-01-01", end_date="2024-12-31")
        >>> print(df.head())
    """
    provider = GoodwillFactory.get_provider(source=source)
    df = provider.get_goodwill_data(symbol, start_date, end_date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_goodwill_impairment(
    date: str,
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get goodwill impairment expectations.

    Args:
        date: Query date in YYYY-MM-DD format
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Goodwill impairment expectations with columns:
            - symbol: Stock symbol
            - name: Stock name
            - goodwill_balance: Goodwill balance (元)
            - expected_impairment: Expected impairment amount (元)
            - risk_level: Risk level (high/medium/low)

    Example:
        >>> # Get goodwill impairment expectations
        >>> df = get_goodwill_impairment("2024-12-31")
        >>> print(df.head())
    """
    provider = GoodwillFactory.get_provider(source=source)
    df = provider.get_goodwill_impairment(date)
    return provider.apply_data_filter(df, columns, row_filter)


def get_goodwill_by_industry(
    date: str,
    source: Literal["eastmoney"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Get goodwill statistics by industry.

    Args:
        date: Query date in YYYY-MM-DD format
        source: Data source ('eastmoney')
        columns: Columns to return (default: all)
        row_filter: Row filter config. Supports: {"top_n": 10}, {"sample": 0.3}, {"query": "..."}

    Returns:
        pd.DataFrame: Industry goodwill statistics with columns:
            - industry: Industry name
            - total_goodwill: Total goodwill amount (元)
            - avg_ratio: Average goodwill to net assets ratio (%)
            - total_impairment: Total impairment amount (元)
            - company_count: Number of companies

    Example:
        >>> # Get goodwill statistics by industry
        >>> df = get_goodwill_by_industry("2024-12-31")
        >>> print(df.head())
    """
    provider = GoodwillFactory.get_provider(source=source)
    df = provider.get_goodwill_by_industry(date)
    return provider.apply_data_filter(df, columns, row_filter)


__all__ = [
    "get_goodwill_data",
    "get_goodwill_impairment",
    "get_goodwill_by_industry",
    "GoodwillFactory",
]
