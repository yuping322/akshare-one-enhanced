"""
Limit Up/Down (涨停池) data module for PV.LimitUpDown.

This module provides interfaces to fetch limit up/down data including:
- Limit up pool (涨停池)
- Limit down pool (跌停池)
- Limit up/down statistics
"""

from typing import Literal
import pandas as pd

from .factory import LimitUpDownFactory


def get_limit_up_pool(
    date: str,
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get limit up pool data.
    
    Args:
        date: Date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized limit up pool data with columns:
            - date: Date (YYYY-MM-DD)
            - symbol: Stock symbol
            - name: Stock name
            - close_price: Closing price
            - limit_up_time: Time when limit up occurred
            - open_count: Number of times limit up was broken
            - seal_amount: Sealing order amount
            - consecutive_days: Number of consecutive limit up days
            - reason: Reason for limit up
            - turnover_rate: Turnover rate
    
    Example:
        >>> df = get_limit_up_pool("2024-01-01")
        >>> print(df.head())
    """
    provider = LimitUpDownFactory.get_provider(source=source)
    return provider.get_limit_up_pool(date)


def get_limit_down_pool(
    date: str,
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get limit down pool data.
    
    Args:
        date: Date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized limit down pool data with columns:
            - date: Date (YYYY-MM-DD)
            - symbol: Stock symbol
            - name: Stock name
            - close_price: Closing price
            - limit_down_time: Time when limit down occurred
            - open_count: Number of times limit down was broken
            - turnover_rate: Turnover rate
    
    Example:
        >>> df = get_limit_down_pool("2024-01-01")
        >>> print(df.head())
    """
    provider = LimitUpDownFactory.get_provider(source=source)
    return provider.get_limit_down_pool(date)


def get_limit_up_stats(
    start_date: str,
    end_date: str,
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get limit up/down statistics.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Statistics with columns:
            - date: Date (YYYY-MM-DD)
            - limit_up_count: Number of limit up stocks
            - limit_down_count: Number of limit down stocks
            - broken_rate: Rate of broken limit ups (%)
    
    Example:
        >>> df = get_limit_up_stats("2024-01-01", "2024-01-31")
        >>> print(df.head())
    """
    provider = LimitUpDownFactory.get_provider(source=source)
    return provider.get_limit_up_stats(start_date, end_date)


__all__ = [
    'get_limit_up_pool',
    'get_limit_down_pool',
    'get_limit_up_stats',
    'LimitUpDownFactory',
]
