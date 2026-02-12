"""
Northbound capital (HSGT) data module for PV.NorthboundHSGT.

This module provides interfaces to fetch northbound capital data including:
- Northbound capital flow (Shanghai/Shenzhen Connect)
- Northbound holdings details
- Northbound capital rankings
"""

from typing import Literal
import pandas as pd

from .factory import NorthboundFactory


def get_northbound_flow(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    market: Literal["sh", "sz", "all"] = "all",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get northbound capital flow data.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        market: Market type ('sh' for Shanghai, 'sz' for Shenzhen, 'all' for both)
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized northbound flow data with columns:
            - date: Date (YYYY-MM-DD)
            - market: Market ('sh', 'sz', or 'all')
            - net_buy: Net buy amount (亿元)
            - buy_amount: Buy amount (亿元)
            - sell_amount: Sell amount (亿元)
            - balance: Balance (亿元)
    
    Example:
        >>> df = get_northbound_flow(start_date="2024-01-01", market="all")
        >>> print(df.head())
    """
    provider = NorthboundFactory.get_provider(source=source)
    return provider.get_northbound_flow(start_date, end_date, market)


def get_northbound_holdings(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get northbound holdings details.
    
    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized northbound holdings data with columns:
            - date: Date (YYYY-MM-DD)
            - symbol: Stock symbol
            - holdings_shares: Holdings in shares
            - holdings_value: Holdings value (元)
            - holdings_ratio: Holdings ratio (%)
            - holdings_change: Holdings change in shares
    
    Example:
        >>> df = get_northbound_holdings("600000", start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = NorthboundFactory.get_provider(source=source)
    return provider.get_northbound_holdings(symbol, start_date, end_date)


def get_northbound_top_stocks(
    date: str,
    market: Literal["sh", "sz", "all"] = "all",
    top_n: int = 100,
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get northbound capital top stocks ranking.
    
    Args:
        date: Date in YYYY-MM-DD format
        market: Market type ('sh', 'sz', or 'all')
        top_n: Number of top stocks to return
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Ranked northbound holdings data with columns:
            - rank: Ranking position
            - symbol: Stock symbol
            - name: Stock name
            - net_buy: Net buy amount (元)
            - holdings_shares: Holdings in shares
            - holdings_ratio: Holdings ratio (%)
    
    Example:
        >>> df = get_northbound_top_stocks("2024-01-01", market="all", top_n=50)
        >>> print(df.head())
    """
    provider = NorthboundFactory.get_provider(source=source)
    return provider.get_northbound_top_stocks(date, market, top_n)


__all__ = [
    'get_northbound_flow',
    'get_northbound_holdings',
    'get_northbound_top_stocks',
    'NorthboundFactory',
]
