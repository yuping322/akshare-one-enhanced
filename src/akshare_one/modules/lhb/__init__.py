"""
Dragon Tiger List (龙虎榜) data module for PV.DragonTigerLHB.

This module provides interfaces to fetch dragon tiger list data including:
- Dragon tiger list data (daily trading anomaly data)
- Dragon tiger list summary statistics
- Broker statistics from dragon tiger list
"""

from typing import Literal
import pandas as pd

from .factory import DragonTigerFactory


def get_dragon_tiger_list(
    date: str,
    symbol: str | None = None,
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get dragon tiger list data.
    
    Args:
        date: Date in YYYY-MM-DD format
        symbol: Stock symbol (optional, if None returns all stocks)
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized dragon tiger list data with columns:
            - date: Date (YYYY-MM-DD)
            - symbol: Stock symbol
            - name: Stock name
            - close_price: Closing price
            - pct_change: Price change percentage
            - reason: Reason for being on the list
            - buy_amount: Dragon tiger list buy amount
            - sell_amount: Dragon tiger list sell amount
            - net_amount: Dragon tiger list net amount
            - total_amount: Dragon tiger list total transaction amount
            - turnover_rate: Turnover rate
    
    Example:
        >>> df = get_dragon_tiger_list("2024-01-01")
        >>> print(df.head())
    """
    provider = DragonTigerFactory.get_provider(source=source)
    return provider.get_dragon_tiger_list(date, symbol)


def get_dragon_tiger_summary(
    start_date: str,
    end_date: str,
    group_by: Literal["stock", "broker", "reason"] = "stock",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get dragon tiger list summary statistics.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        group_by: Grouping dimension ('stock', 'broker', or 'reason')
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Summary statistics grouped by specified dimension
    
    Example:
        >>> df = get_dragon_tiger_summary("2024-01-01", "2024-01-31", group_by="stock")
        >>> print(df.head())
    """
    provider = DragonTigerFactory.get_provider(source=source)
    return provider.get_dragon_tiger_summary(start_date, end_date, group_by)


def get_dragon_tiger_broker_stats(
    start_date: str,
    end_date: str,
    top_n: int = 50,
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get broker statistics from dragon tiger list.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        top_n: Number of top brokers to return
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Broker statistics with columns:
            - rank: Ranking position
            - broker_name: Broker name
            - list_count: Number of times on the list
            - buy_amount: Total buy amount
            - buy_count: Number of buy transactions
            - sell_amount: Total sell amount
            - sell_count: Number of sell transactions
            - net_amount: Net amount (buy - sell)
            - total_amount: Total transaction amount
    
    Example:
        >>> df = get_dragon_tiger_broker_stats("2024-01-01", "2024-01-31", top_n=20)
        >>> print(df.head())
    """
    provider = DragonTigerFactory.get_provider(source=source)
    return provider.get_dragon_tiger_broker_stats(start_date, end_date, top_n)


__all__ = [
    'get_dragon_tiger_list',
    'get_dragon_tiger_summary',
    'get_dragon_tiger_broker_stats',
    'DragonTigerFactory',
]
