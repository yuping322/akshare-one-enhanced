"""
Bond (Convertible Bond) data module.

This module provides interfaces to fetch bond data including:
- Convertible bond list and realtime quotes
- Bond historical data
- Bond adjustment logs
"""

from typing import Literal

import pandas as pd

from .factory import BondFactory


def get_bond_list(
    source: Literal["eastmoney", "jsl"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get convertible bond list.

    Args:
        source: Data source ('eastmoney' or 'jsl')

    Returns:
        pd.DataFrame: Bond list with columns:
            - symbol: Bond symbol
            - name: Bond name
            - stock_symbol: Underlying stock symbol
            - stock_name: Underlying stock name
            - convert_price: Conversion price
            - list_date: Listing date
            - credit_rating: Credit rating

    Example:
        >>> df = get_bond_list()
        >>> print(df.head())
    """
    provider = BondFactory.get_provider(source=source)
    return provider.get_bond_list()


def get_bond_hist_data(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["eastmoney"] = "eastmoney",
) -> pd.DataFrame:
    """
    Get bond historical data.

    Args:
        symbol: Bond symbol (e.g., 'sh113050')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source: Data source ('eastmoney' recommended)

    Returns:
        pd.DataFrame: Historical data with columns:
            - date: Date
            - symbol: Bond symbol
            - open: Opening price
            - high: Highest price
            - low: Lowest price
            - close: Closing price
            - volume: Trading volume

    Example:
        >>> df = get_bond_hist_data("sh113050", start_date="2024-01-01")
        >>> print(df.head())
    """
    provider = BondFactory.get_provider(source=source)
    return provider.get_bond_hist(symbol, start_date, end_date)


def get_bond_realtime_data(
    source: Literal["eastmoney", "jsl"] = "jsl",
) -> pd.DataFrame:
    """
    Get bond realtime quotes.

    Args:
        source: Data source ('jsl' recommended for more details)

    Returns:
        pd.DataFrame: Realtime bond data with columns:
            - symbol: Bond symbol
            - name: Bond name
            - price: Current price
            - pct_change: Price change percentage
            - stock_symbol: Underlying stock symbol
            - stock_price: Underlying stock price
            - convert_price: Conversion price
            - convert_value: Conversion value
            - premium_rate: Conversion premium rate

    Example:
        >>> df = get_bond_realtime_data()
        >>> print(df.head())
    """
    provider = BondFactory.get_provider(source=source)
    return provider.get_bond_spot()


__all__ = [
    "get_bond_list",
    "get_bond_hist_data",
    "get_bond_realtime_data",
    "BondFactory",
]
