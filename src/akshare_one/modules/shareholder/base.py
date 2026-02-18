"""
Base provider class for shareholder data.

This module defines the abstract interface for shareholder data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class ShareholderProvider(BaseProvider):
    """
    Abstract base class for shareholder data providers.

    Defines the interface for fetching various types of shareholder data:
    - Shareholder changes (增减持)
    - Top shareholders
    - Institution holdings
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "shareholder"

    def get_update_frequency(self) -> str:
        """Shareholder data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Shareholder data has 1 day delay."""
        return 0

    @abstractmethod
    def get_shareholder_changes(
        self,
        symbol: str | None = None,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
    ) -> pd.DataFrame:
        """
        Get shareholder changes (增减持) data.

        Args:
            symbol: Stock symbol (optional, if None returns all)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Shareholder changes with columns:
                - symbol: Stock symbol
                - name: Stock name
                - holder_name: Holder name
                - position: Position
                - change_shares: Change in shares
                - change_date: Change date
                - reason: Change reason
        """
        pass

    @abstractmethod
    def get_top_shareholders(self, symbol: str) -> pd.DataFrame:
        """
        Get top shareholders of a stock.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Top shareholders with columns:
                - rank: Ranking
                - holder_name: Holder name
                - shares: Number of shares
                - pct: Percentage of total shares
                - change: Change from last period
        """
        pass

    @abstractmethod
    def get_institution_holdings(self, symbol: str) -> pd.DataFrame:
        """
        Get institution holdings of a stock.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Institution holdings with columns:
                - institution_count: Number of institutions
                - holding_pct: Holding percentage
                - change_pct: Change percentage
        """
        pass
