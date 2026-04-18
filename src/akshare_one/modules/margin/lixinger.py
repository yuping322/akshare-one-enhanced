"""
Lixinger provider for margin financing data.

This module implements margin financing data provider using Lixinger OpenAPI.
"""

import time

import pandas as pd

from ...lixinger_client import get_lixinger_client
from ....metrics.stats import get_stats_collector
from .base import MarginFactory, MarginProvider


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
            symbol: Stock symbol (e.g., '600000'). Required — Lixinger API requires stockCode.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Margin data with financingBalance, securitiesBalance, etc.
        """
        if not symbol:
            self.logger.warning(
                "Lixinger margin API requires a stock symbol. "
                "Market-wide query is not supported. Returning empty DataFrame."
            )
            return pd.DataFrame()

        client = get_lixinger_client()
        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}

        start_time = time.time()
        try:
            response = client.query_api("cn/company/margin-trading-and-securities-lending", params)
            duration_ms = (time.time() - start_time) * 1000

            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("lixinger", duration_ms, True)
            except (ImportError, AttributeError):
                pass

            if response.get("code") != 1:
                return pd.DataFrame()

            data = response.get("data", [])
            if not data:
                return pd.DataFrame()

            df = pd.json_normalize(data)

            return self.standardize_and_filter(
                df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("lixinger", duration_ms, False)
            except (ImportError, AttributeError):
                pass
            self.logger.error(f"Failed to fetch margin data from Lixinger: {e}")
            return pd.DataFrame()

    def get_margin_summary(self, start_date: str, end_date: str, market: str, **kwargs) -> pd.DataFrame:
        """
        Get margin financing summary data.

        Note: Lixinger doesn't provide market summary separately.
        This method returns empty DataFrame.
        """
        return pd.DataFrame()
