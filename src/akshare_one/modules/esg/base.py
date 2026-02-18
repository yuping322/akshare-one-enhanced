"""
Base provider class for ESG rating data.

This module defines the abstract interface for ESG rating data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class ESGProvider(BaseProvider):
    """
    Abstract base class for ESG rating data providers.

    Defines the interface for fetching various types of ESG rating data:
    - ESG rating (comprehensive scores)
    - ESG rating rankings (with industry filtering)
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "esg"

    def get_update_frequency(self) -> str:
        """ESG data is updated irregularly."""
        return "irregular"

    def get_delay_minutes(self) -> int:
        """ESG data is updated irregularly, typically with a delay."""
        return 43200  # 30 days in minutes

    @abstractmethod
    def get_esg_rating(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        page: int = 1,
        page_size: int | None = 1,
    ) -> pd.DataFrame:
        """
        Get ESG rating data.

        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        page: Page number to return (default: 1)
        page_size: Number of items per page (default: 1, returns only first page)
            If None, returns all matching data.
            If specified, returns only the requested page of data.

        Returns:
            pd.DataFrame: Standardized ESG rating data
        """
        pass

    @abstractmethod
    def get_esg_rating_rank(self, date: str, industry: str | None, top_n: int) -> pd.DataFrame:
        """
        Get ESG rating rankings.

        Args:
            date: Query date (YYYY-MM-DD)
            industry: Industry filter (optional)
            top_n: Number of top stocks to return

        Returns:
            pd.DataFrame: ESG rating rankings
        """
        pass
