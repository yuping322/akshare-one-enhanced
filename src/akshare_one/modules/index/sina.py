"""
Sina index data provider.

This module implements the index data provider using Sina Finance (新浪财经) as the data source.
"""

import pandas as pd

from .base import IndexProvider, IndexFactory


@IndexFactory.register("sina")
class SinaIndexProvider(IndexProvider):
    """
    Index data provider using Sina Finance as the data source.

    Sina provides index data including:
    - A-share indices
    - Global indices
    """

    def __init__(self, **kwargs):
        """Initialize the Sina index provider."""
        super().__init__()
        # Accept **kwargs for compatibility (ignore symbol parameter)

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "sina"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Sina.

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
        Get index historical data from Sina.

        Args:
            symbol: Index symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('daily', 'weekly', 'monthly')
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Standardized historical data
        """
        import akshare as ak

        try:
            period_map = {"daily": "daily", "weekly": "weekly", "monthly": "monthly"}
            period = period_map.get(interval, "daily")

            start_date_fmt = start_date.replace("-", "")
            end_date_fmt = end_date.replace("-", "")

            df = ak.index_zh_a_hist(symbol=symbol, period=period, start_date=start_date_fmt, end_date=end_date_fmt)
            df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)

            if not df.empty:
                df["symbol"] = symbol
            return df
        except Exception as e:
            self.logger.warning(f"Failed to fetch index historical data for {symbol}: {e}")
            return pd.DataFrame()

    def get_index_realtime(
        self,
        symbol: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get index realtime quotes from Sina.

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
        except Exception as e:
            self.logger.warning(f"Failed to fetch index realtime data: {e}")
            return pd.DataFrame()

    def get_index_list(
        self,
        category: str = "cn",
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get index list from Sina.

        Args:
            category: Index category ('cn' or 'global')
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
            elif category == "global":
                df = ak.index_global_name_table()
                df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)
                if not df.empty:
                    df["type"] = "global_index"
                return df
            else:
                return pd.DataFrame(columns=["symbol", "name", "type"])
        except Exception as e:
            self.logger.warning(f"Failed to fetch index list (category={category}): {e}")
            return pd.DataFrame(columns=["symbol", "name", "type"])

    def get_index_constituents(
        self,
        symbol: str,
        include_weight: bool = True,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get index constituent stocks from Sina.

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
        except Exception as e:
            self.logger.warning(f"Failed to fetch index constituents for {symbol}: {e}")
            return pd.DataFrame(columns=["symbol", "name", "weight"])
