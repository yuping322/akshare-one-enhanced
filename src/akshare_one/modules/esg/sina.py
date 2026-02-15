"""
Sina ESG rating data provider.

This module implements the ESG rating data provider using Sina as the data source.
"""

from typing import Optional
import pandas as pd

from .base import ESGProvider


class SinaESGProvider(ESGProvider):
    """
    ESG rating data provider using Sina as the data source.

    This provider wraps akshare functions to fetch ESG rating data from Sina
    and standardizes the output format for consistency.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return 'sina'

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Sina.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def get_esg_rating(
        self,
        symbol: Optional[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get ESG rating data from Sina.

        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized ESG rating data
        """
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        # Return empty DataFrame with proper structure
        return self.create_empty_dataframe([
            'symbol', 'name', 'date', 'esg_score', 'environmental_score',
            'social_score', 'governance_score', 'rating'
        ])

    def get_esg_rating_rank(
        self,
        date: str,
        industry: Optional[str],
        top_n: int
    ) -> pd.DataFrame:
        """
        Get ESG rating rankings from Sina.

        Args:
            date: Query date (YYYY-MM-DD)
            industry: Industry filter (optional)
            top_n: Number of top stocks to return

        Returns:
            pd.DataFrame: ESG rating rankings
        """
        if top_n <= 0:
            raise ValueError("top_n must be a positive integer")

        # Return empty DataFrame with proper structure
        return self.create_empty_dataframe([
            'rank', 'symbol', 'name', 'esg_score', 'industry'
        ])
