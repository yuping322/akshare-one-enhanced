"""
Base provider class for bond data.

This module defines the abstract interface for bond data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class BondProvider(BaseProvider):
    """
    Abstract base class for bond data providers.

    Defines the interface for fetching various types of bond data:
    - Convertible bond list and realtime quotes
    - Bond historical data
    - Bond adjustment logs
    - Bond redemption data
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "bond"

    def get_update_frequency(self) -> str:
        """Bond data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Bond data has minimal delay."""
        return 0

    @abstractmethod
    def get_bond_list(self) -> pd.DataFrame:
        """
        Get convertible bond list.

        Returns:
            pd.DataFrame: Bond list with columns:
                - symbol: Bond symbol
                - name: Bond name
                - stock_symbol: Underlying stock symbol
                - stock_name: Underlying stock name
                - convert_price: Conversion price
                - list_date: Listing date
                - credit_rating: Credit rating
        """
        pass

    @abstractmethod
    def get_bond_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get bond historical data.

        Args:
            symbol: Bond symbol (e.g., 'sh113050')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Historical data with columns:
                - date: Date
                - symbol: Bond symbol
                - open: Opening price
                - high: Highest price
                - low: Lowest price
                - close: Closing price
                - volume: Trading volume
        """
        pass

    @abstractmethod
    def get_bond_spot(self) -> pd.DataFrame:
        """
        Get bond realtime quotes.

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
        """
        pass
