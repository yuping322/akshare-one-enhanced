"""
Lixinger provider for margin financing data.

This module implements margin financing data provider using Lixinger OpenAPI.
"""

import pandas as pd

from .base import MarginProvider, MarginFactory
from ...lixinger_client import get_lixinger_client


@MarginFactory.register("lixinger")
class LixingerMarginProvider(MarginProvider):
    """
    Margin financing data provider using Lixinger OpenAPI.

    Provides margin balance, financing buy, short selling data.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_margin_data(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get margin financing data from Lixinger.

        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Margin data
        """
        client = get_lixinger_client()

        if symbol:
            params = {"stockCodes": [symbol], "startDate": start_date, "endDate": end_date}
        else:
            params = {"startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/margin-trading-and-securities-lending", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_margin_summary(self, start_date: str, end_date: str, market: str, **kwargs) -> pd.DataFrame:
        """
        Get margin financing summary data.

        Note: Lixinger doesn't provide market summary separately.
        This method returns empty DataFrame.
        """
        return pd.DataFrame()
