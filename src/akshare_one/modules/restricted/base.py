"""
Base provider class for restricted stock release data.

This module defines the abstract interface for restricted stock release data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class RestrictedReleaseProvider(BaseProvider):
    """
    Abstract base class for restricted stock release data providers.

    Defines the interface for fetching various types of restricted release data:
    - Restricted release data (detailed release information)
    - Restricted release calendar (aggregated release schedule)
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "restricted"

    def get_update_frequency(self) -> str:
        """Restricted release data is updated irregularly."""
        return "irregular"

    def get_delay_minutes(self) -> int:
        """Restricted release data is updated irregularly, no fixed delay."""
        return 0

    @abstractmethod
    def get_restricted_release(self, symbol: str | None, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get restricted stock release data.

        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized restricted release data
        """
        pass

    @abstractmethod
    def get_restricted_release_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get restricted stock release calendar.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Calendar data
        """
        pass
