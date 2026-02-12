"""
ESG (ESG 评级) data module for PV.ESG.

This module provides interfaces to fetch ESG rating data including:
- ESG rating (ESG 评分) - comprehensive ESG scores
- ESG rating rank (ESG 评级排名) - industry rankings
"""

from typing import Literal, Optional
import pandas as pd

from .factory import ESGFactory


def get_esg_rating(
    symbol: Optional[str] = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get ESG rating data.
    
    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Standardized ESG rating data with columns:
            - symbol: Stock symbol
            - rating_date: Rating date (YYYY-MM-DD)
            - esg_score: Overall ESG score
            - e_score: Environmental score
            - s_score: Social score
            - g_score: Governance score
            - rating_agency: Rating agency name
    
    Example:
        >>> # Get ESG rating for a specific stock
        >>> df = get_esg_rating("600000", start_date="2024-01-01")
        >>> print(df.head())
        >>> 
        >>> # Get ESG rating for all stocks
        >>> df = get_esg_rating(start_date="2024-01-01", end_date="2024-12-31")
        >>> print(df.head())
    """
    provider = ESGFactory.get_provider(source=source)
    return provider.get_esg_rating(symbol, start_date, end_date)


def get_esg_rating_rank(
    date: str,
    industry: Optional[str] = None,
    top_n: int = 100,
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get ESG rating rankings.
    
    Args:
        date: Query date in YYYY-MM-DD format
        industry: Industry filter (optional). If None, returns all industries.
        top_n: Number of top stocks to return (default: 100)
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: ESG rating rankings with columns:
            - rank: Overall rank
            - symbol: Stock symbol
            - name: Stock name
            - esg_score: Overall ESG score
            - industry: Industry name
            - industry_rank: Rank within industry
    
    Example:
        >>> # Get top 100 ESG ratings
        >>> df = get_esg_rating_rank("2024-12-31")
        >>> print(df.head())
        >>> 
        >>> # Get top ESG ratings for banking industry
        >>> df = get_esg_rating_rank("2024-12-31", industry="银行")
        >>> print(df.head())
    """
    provider = ESGFactory.get_provider(source=source)
    return provider.get_esg_rating_rank(date, industry, top_n)


__all__ = [
    'get_esg_rating',
    'get_esg_rating_rank',
    'ESGFactory',
]
