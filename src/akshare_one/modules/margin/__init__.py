"""
Margin Financing (融资融券) data module for PV.MarginFinancing.

This module provides interfaces to fetch margin financing data including:
- Margin financing data (融资融券数据) - individual stocks and market-wide
- Margin financing summary (融资融券汇总) - market aggregation
"""

from typing import Literal, Optional
import pandas as pd

from .factory import MarginFactory


def get_margin_data(
    symbol: Optional[str] = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get margin financing data.
    
    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized margin financing data with columns:
            - date: Date (YYYY-MM-DD)
            - symbol: Stock symbol
            - name: Stock name
            - margin_balance: Margin financing balance (元)
            - margin_buy: Margin financing buy amount (元)
            - short_balance: Short selling balance (元)
            - short_sell_volume: Short selling volume (股)
            - total_balance: Total margin balance (元)
    
    Example:
        >>> # Get margin data for a specific stock
        >>> df = get_margin_data("600000", start_date="2024-01-01")
        >>> print(df.head())
        >>> 
        >>> # Get margin data for all stocks
        >>> df = get_margin_data(start_date="2024-01-01", end_date="2024-01-31")
        >>> print(df.head())
    """
    provider = MarginFactory.get_provider(source=source)
    return provider.get_margin_data(symbol, start_date, end_date)


def get_margin_summary(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    market: Literal["sh", "sz", "all"] = "all",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get margin financing summary data.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        market: Market ('sh' for Shanghai, 'sz' for Shenzhen, 'all' for both)
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Summary data with columns:
            - date: Date (YYYY-MM-DD)
            - market: Market ('sh', 'sz', or 'all')
            - margin_balance: Total margin financing balance (元)
            - short_balance: Total short selling balance (元)
            - total_balance: Total margin balance (元)
    
    Example:
        >>> # Get summary for all markets
        >>> df = get_margin_summary(start_date="2024-01-01", end_date="2024-01-31")
        >>> print(df.head())
        >>> 
        >>> # Get summary for Shanghai market only
        >>> df = get_margin_summary(start_date="2024-01-01", market="sh")
        >>> print(df.head())
    """
    provider = MarginFactory.get_provider(source=source)
    return provider.get_margin_summary(start_date, end_date, market)


__all__ = [
    'get_margin_data',
    'get_margin_summary',
    'MarginFactory',
]
