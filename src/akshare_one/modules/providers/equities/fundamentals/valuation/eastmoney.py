"""
Eastmoney valuation data provider.

This module implements the valuation data provider using Eastmoney (东方财富) as the data source.
"""

import pandas as pd

from .base import ValuationFactory, ValuationProvider


@ValuationFactory.register("eastmoney")
class EastmoneyValuationProvider(ValuationProvider):
    """
    Valuation data provider using Eastmoney as the data source.

    Eastmoney provides comprehensive valuation data including:
    - Stock PE, PB, PS, PEG
    - Market cap data
    """

    def __init__(self, **kwargs):
        """Initialize the Eastmoney valuation provider."""
        super().__init__()
        # Accept **kwargs for compatibility (ignore symbol parameter)

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data. Not used directly."""
        return pd.DataFrame()

    def get_stock_valuation(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get stock valuation data from Eastmoney.

        Args:
            symbol: Stock symbol (e.g., '600000')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Valuation data
        """
        import akshare as ak

        try:
            df = ak.stock_value_em()
            df = self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)

            if not df.empty:
                df["symbol"] = symbol
                df["date"] = pd.to_datetime(df["date"])
                start = pd.to_datetime(start_date)
                end = pd.to_datetime(end_date)
                df = df[(df["date"] >= start) & (df["date"] <= end)]

            return df
        except Exception as e:
            self.logger.error(f"Failed to fetch stock valuation: {e}")
            return pd.DataFrame()

    def get_market_valuation(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get market-wide valuation summary.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Market valuation summary
        """
        import akshare as ak

        try:
            df = ak.stock_a_ttm_lyr()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch market valuation: {e}")
            return pd.DataFrame()
        """
        Get market-wide valuation data from Eastmoney.

        Note: Uses A-share index data as proxy.

        Returns:
            pd.DataFrame: Market valuation data
        """
        import akshare as ak

        try:
            df = ak.stock_a_pe_and_pb_em(symbol="上证指数")

            if df.empty:
                return pd.DataFrame()

            df = df.rename(columns={"date": "date", "pe": "pe", "pb": "pb"})

            df["index_name"] = "上证指数"

            cols = ["date", "index_name", "pe", "pb"]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
