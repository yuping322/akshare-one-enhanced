"""
Eastmoney suspended stocks data provider.
"""

import pandas as pd

from .base import SuspendedProvider


class EastmoneySuspendedProvider(SuspendedProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_suspended_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get current suspended stocks and their resume schedules.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Suspended stocks with dates and reasons.
        """
        import akshare as ak

        try:
            df = ak.stock_tfp_em()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch suspended stocks: {e}")
            return pd.DataFrame()
