"""
Eastmoney index data provider.

This module implements the index data provider using Eastmoney (东方财富) as the data source.
"""

import pandas as pd

from .base import IndexProvider


class EastmoneyIndexProvider(IndexProvider):
    """
    Index data provider using Eastmoney as the data source.

    Eastmoney provides comprehensive index data including:
    - A-share indices
    - Global indices
    - Index constituents
    """

    def __init__(self):
        """Initialize the Eastmoney index provider."""
        super().__init__()

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Eastmoney.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def get_index_hist(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "daily",
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get index historical data from Eastmoney.

        Args:
            symbol: Index symbol (e.g., '000001')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('daily', 'weekly', 'monthly')
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Standardized historical data
        """
        import akshare as ak

        period_map = {"daily": "daily", "weekly": "weekly", "monthly": "monthly"}
        period = period_map.get(interval, "daily")

        start_date_fmt = start_date.replace("-", "")
        end_date_fmt = end_date.replace("-", "")

        df = ak.index_zh_a_hist(symbol=symbol, period=period, start_date=start_date_fmt, end_date=end_date_fmt)
        df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)

        if not df.empty:
            df["symbol"] = symbol
        return df

    def get_index_realtime(
        self,
        symbol: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get index realtime quotes from Eastmoney.

        Args:
            symbol: Index symbol (optional)
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Realtime index data
        """
        import akshare as ak

        try:
            df = ak.stock_zh_index_spot_em()
            df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)

            if symbol and not df.empty:
                df = df[df["symbol"] == symbol]
            return df
        except Exception:
            return pd.DataFrame()

    def get_index_list(
        self,
        category: str = "cn",
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get index list from Eastmoney.

        Args:
            category: Index category ('cn' for Chinese indices)
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Index list
        """
        import akshare as ak

        try:
            if category == "cn":
                df = ak.index_stock_info()
                df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)
                if not df.empty:
                    df["type"] = "cn_index"
                return df
            else:
                return pd.DataFrame(columns=["symbol", "name", "type"])
        except Exception:
            return pd.DataFrame(columns=["symbol", "name", "type"])

    def get_index_constituents(
        self,
        symbol: str,
        include_weight: bool = True,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get index constituent stocks from Eastmoney (via CSIndex).

        Args:
            symbol: Index symbol
            include_weight: Whether to include weight
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Constituent stocks
        """
        import akshare as ak

        try:
            df = ak.index_stock_cons_weight_csindex(symbol=symbol)
            df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)
            return df
        except Exception:
            return pd.DataFrame(columns=["symbol", "name", "weight"])

