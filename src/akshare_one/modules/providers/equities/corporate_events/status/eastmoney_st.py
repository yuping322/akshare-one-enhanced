"""
Eastmoney ST stocks data provider.
"""

import pandas as pd

from .st import STFactory, STProvider


@STFactory.register("eastmoney")
class EastmoneySTProvider(STProvider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_st_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get spot quotes for ST and *ST stocks.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Special treatment stocks with quotes.
        """
        import akshare as ak

        try:
            df = ak.stock_zh_a_st_em()
            return self.standardize_and_filter(df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch ST stocks: {e}")
            return pd.DataFrame()
