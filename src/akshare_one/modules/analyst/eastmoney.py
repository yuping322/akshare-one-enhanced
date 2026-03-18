"""
Eastmoney analyst data provider.
"""

import pandas as pd

from .base import AnalystProvider


class EastmoneyAnalystProvider(AnalystProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_analyst_rank(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get analyst performance rankings from Eastmoney.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Ranked analyst data with performance metrics.
        """
        import akshare as ak

        try:
            df = ak.stock_analyst_rank_em()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch analyst rank: {e}")
            return pd.DataFrame()

    def get_research_report(
        self,
        symbol: str,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get research reports for a specific stock.

        Args:
            symbol: Stock symbol (e.g., '600000').
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: List of research reports with ratings and institutions.
        """
        import akshare as ak

        try:
            df = ak.stock_research_report_em(symbol=symbol)
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch research report for {symbol}: {e}")
            return pd.DataFrame()
