"""
Eastmoney IPO data provider.
"""

import pandas as pd

from .base import IPOProvider


class EastmoneyIPOProvider(IPOProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_new_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get newly listed A-share stocks.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: New stocks with listing dates and quotes.
        """
        import akshare as ak

        try:
            df = ak.stock_new_a_spot_em()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch new stocks: {e}")
            return pd.DataFrame()

    def get_ipo_info(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get IPO summary and subscription information.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: IPO schedules and issue prices.
        """
        import akshare as ak

        try:
            df = ak.stock_ipo_summary_cninfo()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch IPO summary: {e}")
            return pd.DataFrame()
