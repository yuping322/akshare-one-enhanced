"""
Lixinger provider for valuation data.

This module implements valuation data provider using Lixinger OpenAPI.
"""

import time

import pandas as pd

from ...lixinger_client import get_lixinger_client
from ....metrics.stats import get_stats_collector
from .base import ValuationFactory, ValuationProvider


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

        start_time = time.time()
        try:
            response = client.query_api("cn/company/fundamental/non_financial", params)
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
            self.logger.error(f"Failed to fetch valuation data from Lixinger: {e}")
            return pd.DataFrame()

    def get_market_valuation(self, **kwargs) -> pd.DataFrame:
        """
        Get market-wide valuation data.

        Note: Lixinger doesn't provide market-wide summary.
        This returns empty DataFrame.
        """
        return pd.DataFrame()
