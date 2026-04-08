"""
Lixinger provider for valuation data.

This module implements valuation data provider using Lixinger OpenAPI.
"""

import pandas as pd

from .base import ValuationProvider, ValuationFactory
from ...lixinger_client import get_lixinger_client


@ValuationFactory.register("lixinger")
class LixingerValuationProvider(ValuationProvider):
    """
    Valuation data provider using Lixinger OpenAPI.

    Provides PE, PB, PS, market cap, dividend yield, etc.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data - not directly used.

        Each specific method fetches its own data.
        """
        return pd.DataFrame()

    def get_stock_valuation(
        self, symbol: str, start_date: str, end_date: str, metrics: list[str] | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get stock valuation data from Lixinger.

        Args:
            symbol: Stock symbol (e.g., '600000')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics: List of metrics to fetch
                     Default: ['pe_ttm', 'pb', 'ps_ttm', 'mc', 'cmc', 'dyr']

        Returns:
            pd.DataFrame: Valuation data with columns:
                - date: Date
                - symbol: Stock symbol
                - pe_ttm: PE-TTM
                - pb: PB
                - ps_ttm: PS-TTM
                - market_cap: Market cap (元)
                - circulating_market_cap: Circulating market cap (元)
                - dividend_yield_ratio: Dividend yield ratio
        """
        if metrics is None:
            metrics = ["pe_ttm", "pb", "ps_ttm", "mc", "cmc", "dyr"]

        client = get_lixinger_client()

        params = {"stockCodes": [symbol], "metricsList": metrics, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/fundamental/non_financial", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_market_valuation(self, **kwargs) -> pd.DataFrame:
        """
        Get market-wide valuation data.

        Note: Lixinger doesn't provide market-wide summary.
        This returns empty DataFrame.
        """
        return pd.DataFrame()
