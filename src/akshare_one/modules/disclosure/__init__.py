"""
Disclosure news data module for PV.DisclosureNews.

This module provides interfaces to fetch disclosure and announcement data including:
- General disclosure news
- Dividend data
- Repurchase data
- ST/Delist risk data
"""

from typing import Literal
import pandas as pd

from .factory import DisclosureFactory


def get_disclosure_news(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    category: Literal["all", "dividend", "repurchase", "st", "major_event"] = "all",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get disclosure news data.
    
    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        category: News category ('all', 'dividend', 'repurchase', 'st', 'major_event')
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized disclosure news data with columns:
            - date: Announcement date (YYYY-MM-DD)
            - symbol: Stock symbol
            - title: Announcement title
            - category: Announcement category
            - content: Announcement summary
            - url: Announcement URL
    
    Example:
        >>> df = get_disclosure_news("600000", start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = DisclosureFactory.get_provider(source=source)
    return provider.get_disclosure_news(symbol, start_date, end_date, category)


def get_dividend_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get dividend data.
    
    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized dividend data with columns:
            - symbol: Stock symbol
            - fiscal_year: Dividend fiscal year
            - dividend_per_share: Dividend per share
            - record_date: Record date (YYYY-MM-DD)
            - ex_dividend_date: Ex-dividend date (YYYY-MM-DD)
            - payment_date: Payment date (YYYY-MM-DD)
            - dividend_ratio: Dividend ratio
    
    Example:
        >>> df = get_dividend_data("600000", start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = DisclosureFactory.get_provider(source=source)
    return provider.get_dividend_data(symbol, start_date, end_date)


def get_repurchase_data(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get stock repurchase data.
    
    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized repurchase data with columns:
            - symbol: Stock symbol
            - announcement_date: Announcement date (YYYY-MM-DD)
            - progress: Repurchase progress
            - amount: Repurchase amount
            - quantity: Repurchase quantity
            - price_range: Repurchase price range
    
    Example:
        >>> df = get_repurchase_data("600000", start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = DisclosureFactory.get_provider(source=source)
    return provider.get_repurchase_data(symbol, start_date, end_date)


def get_st_delist_data(
    symbol: str | None = None,
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get ST/delist risk data.
    
    Args:
        symbol: Stock symbol (e.g., '600000'), None for all stocks
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized ST/delist risk data with columns:
            - symbol: Stock symbol
            - name: Stock name
            - st_type: ST type
            - risk_level: Risk level
            - announcement_date: Announcement date (YYYY-MM-DD)
    
    Example:
        >>> df = get_st_delist_data("600000")
        >>> print(df.head())
    """
    provider = DisclosureFactory.get_provider(source=source)
    return provider.get_st_delist_data(symbol)


__all__ = [
    'get_disclosure_news',
    'get_dividend_data',
    'get_repurchase_data',
    'get_st_delist_data',
    'DisclosureFactory',
]
