"""
Eastmoney HK/US stock data provider.
"""

import pandas as pd

from .base import HKUSFactory, HKUSProvider


@HKUSFactory.register("eastmoney")
class EastmoneyHKUSProvider(HKUSProvider):
    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_hk_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get spot quotes for Hong Kong listed stocks.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: HK stocks with price and change data.
        """
        import akshare as ak

        try:
            df = ak.stock_hk_spot_em()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch HK stocks: {e}")
            return pd.DataFrame()

    def get_us_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get spot quotes for US listed stocks.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: US stocks with price and change data.
        """
        import akshare as ak

        try:
            df = ak.stock_us_spot_em()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch US stocks: {e}")
            return pd.DataFrame()
