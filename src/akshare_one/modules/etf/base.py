"""
Base provider class for ETF data.

This module defines the abstract interface for ETF data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class ETFProvider(BaseProvider):
    """
    Abstract base class for ETF data providers.

    Defines the interface for fetching various types of ETF data:
    - ETF historical data
    - ETF realtime quotes
    - ETF list and basic info
    - Fund manager information
    - Fund ratings
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "etf"

    def get_update_frequency(self) -> str:
        """ETF data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """ETF data has 1 day delay for some fields."""
        return 0

    @abstractmethod
    def get_etf_hist(
        self, symbol: str, start_date: str, end_date: str, interval: str = "daily"
    ) -> pd.DataFrame:
        """
        Get ETF historical data.

        Args:
            symbol: ETF symbol (6-digit code)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('daily', 'weekly', 'monthly')

        Returns:
            pd.DataFrame: Standardized historical data with columns:
                - date: Date
                - symbol: ETF symbol
                - open: Opening price
                - high: Highest price
                - low: Lowest price
                - close: Closing price
                - volume: Trading volume
                - amount: Trading amount
        """
        pass

    @abstractmethod
    def get_etf_spot(self) -> pd.DataFrame:
        """
        Get all ETF realtime quotes.

        Returns:
            pd.DataFrame: Realtime ETF data with columns:
                - symbol: ETF symbol
                - name: ETF name
                - price: Current price
                - pct_change: Price change percentage
                - volume: Trading volume
                - amount: Trading amount
                - prev_close: Previous close price
        """
        pass

    @abstractmethod
    def get_etf_list(self, category: str = "all") -> pd.DataFrame:
        """
        Get ETF list.

        Args:
            category: ETF category ('all', 'stock', 'bond', 'cross', 'money')

        Returns:
            pd.DataFrame: ETF list with columns:
                - symbol: ETF symbol
                - name: ETF name
                - type: ETF type
                - list_date: Listing date
        """
        pass

    @abstractmethod
    def get_fund_manager(self) -> pd.DataFrame:
        """
        Get fund manager information.

        Returns:
            pd.DataFrame: Fund manager data with columns:
                - manager_name: Manager name
                - fund_count: Number of funds managed
                - fund_names: Fund names
                - tenure_days: Tenure in days
        """
        pass

    @abstractmethod
    def get_fund_rating(self) -> pd.DataFrame:
        """
        Get fund ratings.

        Returns:
            pd.DataFrame: Fund rating data with columns:
                - symbol: Fund symbol
                - name: Fund name
                - rating: Rating (1-5 stars)
                - rating_date: Rating date
        """
        pass
