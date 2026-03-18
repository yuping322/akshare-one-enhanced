"""
Eastmoney board data provider.
"""

import pandas as pd

from .base import BoardProvider


class EastmoneyBoardProvider(BoardProvider):
    def __init__(self):
        super().__init__()

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_kcb_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get Kechuang Board (Star Market) spot stock quotes.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: KCB stocks with price and change data.
        """
        import akshare as ak

        try:
            df = ak.stock_kcb_spot_em()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch KCB stocks: {e}")
            return pd.DataFrame()

    def get_cyb_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get ChiNext (Growth Enterprise Market) spot stock quotes.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: CYB stocks with price and change data.
        """
        import akshare as ak

        try:
            df = ak.stock_cyb_spot_em()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch CYB stocks: {e}")
            return pd.DataFrame()
