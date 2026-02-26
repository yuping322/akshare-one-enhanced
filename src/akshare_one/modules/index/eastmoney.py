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

    def get_index_hist(self, symbol: str, start_date: str, end_date: str, interval: str = "daily") -> pd.DataFrame:
        """
        Get index historical data from Eastmoney.

        Args:
            symbol: Index symbol (e.g., '000001')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('daily', 'weekly', 'monthly')

        Returns:
            pd.DataFrame: Standardized historical data
        """
        import akshare as ak

        period_map = {"daily": "daily", "weekly": "weekly", "monthly": "monthly"}

        period = period_map.get(interval, "daily")

        start_date_fmt = start_date.replace("-", "")
        end_date_fmt = end_date.replace("-", "")

        df = ak.index_zh_a_hist(symbol=symbol, period=period, start_date=start_date_fmt, end_date=end_date_fmt)

        if df.empty:
            return pd.DataFrame()

        df = self._standardize_hist_data(df, symbol)

        return df

    def get_index_realtime(self, symbol: str | None = None) -> pd.DataFrame:
        """
        Get index realtime quotes from Eastmoney.

        Note: Eastmoney doesn't provide a direct realtime index API.
        This returns the latest data from historical API.

        Args:
            symbol: Index symbol (optional)

        Returns:
            pd.DataFrame: Realtime index data
        """
        import akshare as ak

        try:
            df = ak.stock_zh_index_spot_em()

            if df.empty:
                return pd.DataFrame()

            df = self._standardize_realtime_data(df)

            if symbol:
                df = df[df["symbol"] == symbol]

            return df
        except Exception:
            return pd.DataFrame()

    def get_index_list(self, category: str = "cn") -> pd.DataFrame:
        """
        Get index list from Eastmoney.

        Args:
            category: Index category ('cn' for Chinese indices)

        Returns:
            pd.DataFrame: Index list
        """
        import akshare as ak

        try:
            if category == "cn":
                df = ak.index_stock_info()

                if df.empty:
                    return pd.DataFrame()

                df = df.rename(columns={"index_code": "symbol", "display_name": "name"})

                df["type"] = "cn_index"

                df = df[["symbol", "name", "type"]]

                return df
            else:
                return pd.DataFrame(columns=["symbol", "name", "type"])
        except Exception:
            return pd.DataFrame(columns=["symbol", "name", "type"])

    def get_index_constituents(self, symbol: str, include_weight: bool = True) -> pd.DataFrame:
        """
        Get index constituent stocks from Eastmoney (via CSIndex).

        Args:
            symbol: Index symbol
            include_weight: Whether to include weight

        Returns:
            pd.DataFrame: Constituent stocks
        """
        import akshare as ak

        try:
            df = ak.index_stock_cons_weight_csindex(symbol=symbol)

            if df.empty:
                return pd.DataFrame()

            df = df.rename(columns={"成分券代码": "symbol", "成分券名称": "name", "权重": "weight"})

            df = df[["symbol", "name", "weight"]] if include_weight else df[["symbol", "name"]]

            return df
        except Exception:
            return pd.DataFrame(columns=["symbol", "name", "weight"])

    def _standardize_hist_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Standardize historical data columns."""
        df = df.rename(
            columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "涨跌幅": "pct_change",
                "涨跌额": "change",
                "换手率": "turnover",
            }
        )

        df["symbol"] = symbol

        cols = ["date", "symbol", "open", "high", "low", "close", "volume", "amount"]
        if "pct_change" in df.columns:
            cols.extend(["pct_change", "turnover"])

        df = df[[c for c in cols if c in df.columns]]

        return df

    def _standardize_realtime_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize realtime data columns."""
        df = df.rename(
            columns={
                "代码": "symbol",
                "名称": "name",
                "最新价": "value",
                "涨跌幅": "pct_change",
                "涨跌额": "change",
                "成交量": "volume",
                "成交额": "amount",
            }
        )

        cols = ["symbol", "name", "value", "pct_change", "change", "volume", "amount"]
        df = df[[c for c in cols if c in df.columns]]

        return df
