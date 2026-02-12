"""
Equity Pledge (股权质押) data module for PV.EquityPledge.

This module provides interfaces to fetch equity pledge data including:
- Equity pledge data (股权质押数据) - shareholder pledge information
- Equity pledge ratio ranking (质押比例排名) - stocks ranked by pledge ratio
"""

from typing import Literal, Optional
import pandas as pd

from .factory import EquityPledgeFactory


def get_equity_pledge(
    symbol: Optional[str] = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get equity pledge data.
    
    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized equity pledge data with columns:
            - symbol: Stock symbol
            - shareholder_name: Shareholder name
            - pledge_shares: Pledged shares (股)
            - pledge_ratio: Pledge ratio (%)
            - pledgee: Pledgee institution
            - pledge_date: Pledge date (YYYY-MM-DD)
    
    Example:
        >>> # Get pledge data for a specific stock
        >>> df = get_equity_pledge("600000", start_date="2024-01-01")
        >>> print(df.head())
        >>> 
        >>> # Get pledge data for all stocks
        >>> df = get_equity_pledge(start_date="2024-01-01", end_date="2024-01-31")
        >>> print(df.head())
    """
    provider = EquityPledgeFactory.get_provider(source=source)
    return provider.get_equity_pledge(symbol, start_date, end_date)


def get_equity_pledge_ratio_rank(
    date: str,
    top_n: int = 100,
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get equity pledge ratio ranking.
    
    Args:
        date: Query date in YYYY-MM-DD format
        top_n: Number of top stocks to return (default: 100)
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Ranking data with columns:
            - rank: Ranking
            - symbol: Stock symbol
            - name: Stock name
            - pledge_ratio: Total pledge ratio (%)
            - pledge_value: Pledged market value (元)
    
    Example:
        >>> # Get top 100 stocks by pledge ratio
        >>> df = get_equity_pledge_ratio_rank("2024-01-31")
        >>> print(df.head())
        >>> 
        >>> # Get top 50 stocks
        >>> df = get_equity_pledge_ratio_rank("2024-01-31", top_n=50)
        >>> print(df.head())
    """
    provider = EquityPledgeFactory.get_provider(source=source)
    return provider.get_equity_pledge_ratio_rank(date, top_n)


__all__ = [
    'get_equity_pledge',
    'get_equity_pledge_ratio_rank',
    'EquityPledgeFactory',
]
