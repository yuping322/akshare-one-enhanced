"""
Block deal data module for PV.BlockDeal.

This module provides interfaces to fetch block deal (大宗交易) data including:
- Block deal details (individual stock and market-wide)
- Block deal summary statistics
"""

from typing import Literal
import pandas as pd

from .factory import BlockDealFactory


def get_block_deal(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get block deal transaction details.
    
    Args:
        symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Block deal data with columns:
            - date: Transaction date (YYYY-MM-DD)
            - symbol: Stock symbol
            - name: Stock name
            - price: Transaction price
            - volume: Transaction volume (shares)
            - amount: Transaction amount (yuan)
            - buyer_branch: Buyer branch name
            - seller_branch: Seller branch name
            - premium_rate: Premium/discount rate (%)
    
    Example:
        >>> df = get_block_deal("600000", start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = BlockDealFactory.get_provider(source=source)
    return provider.get_block_deal(symbol, start_date, end_date)


def get_block_deal_summary(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    group_by: Literal["stock", "date", "broker"] = "stock",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get block deal summary statistics.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        group_by: Grouping dimension ('stock', 'date', or 'broker')
        source: Data source ('eastmoney')
    
    Returns:
        pd.DataFrame: Summary statistics with columns varying by group_by:
            - For 'stock': symbol, name, deal_count, total_amount, avg_premium_rate
            - For 'date': date, deal_count, total_amount, avg_premium_rate
            - For 'broker': broker_name, deal_count, total_amount, avg_premium_rate
    
    Example:
        >>> df = get_block_deal_summary(start_date="2024-01-01", group_by="stock")
        >>> print(df.head())
    """
    provider = BlockDealFactory.get_provider(source=source)
    return provider.get_block_deal_summary(start_date, end_date, group_by)


__all__ = [
    'get_block_deal',
    'get_block_deal_summary',
    'BlockDealFactory',
]
