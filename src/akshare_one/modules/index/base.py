"""
Base provider class for index data.

This module defines the abstract interface for index data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class IndexProvider(BaseProvider):
    """
    Abstract base class for index data providers.

    Defines the interface for fetching various types of index data:
    - Index historical data
    - Index realtime quotes
    - Index constituents
    - Index list
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "index"

    def get_update_frequency(self) -> str:
        """Index data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Index data has minimal delay."""
        return 0

    @abstractmethod
    def get_index_hist(
        self, symbol: str, start_date: str, end_date: str, interval: str = "daily"
    ) -> pd.DataFrame:
        """
        Get index historical data.

        Args:
            symbol: Index symbol (e.g., '000001' for SSE Composite)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('daily', 'weekly', 'monthly')

        Returns:
            pd.DataFrame: Standardized historical data with columns:
                - date: Date
                - symbol: Index symbol
                - open: Opening value
                - high: Highest value
                - low: Lowest value
                - close: Closing value
                - volume: Trading volume
                - amount: Trading amount
        """
        pass

    @abstractmethod
    def get_index_realtime(self, symbol: str | None = None) -> pd.DataFrame:
        """
        Get index realtime quotes.

        Args:
            symbol: Index symbol (optional, if None returns all)

        Returns:
            pd.DataFrame: Realtime index data with columns:
                - symbol: Index symbol
                - name: Index name
                - value: Current value
                - pct_change: Change percentage
                - change: Change amount
                - volume: Trading volume
                - amount: Trading amount
        """
        pass

    @abstractmethod
    def get_index_list(self, category: str = "cn") -> pd.DataFrame:
        """
        Get index list.

        Args:
            category: Index category ('cn', 'global')

        Returns:
            pd.DataFrame: Index list with columns:
                - symbol: Index symbol
                - name: Index name
                - type: Index type
        """
        pass

    @abstractmethod
    def get_index_constituents(self, symbol: str, include_weight: bool = True) -> pd.DataFrame:
        """
        Get index constituent stocks.

        Args:
            symbol: Index symbol
            include_weight: Whether to include weight information

        Returns:
            pd.DataFrame: Constituent stocks with columns:
                - symbol: Stock symbol
                - name: Stock name
                - weight: Weight in index (if available)
        """
        pass
