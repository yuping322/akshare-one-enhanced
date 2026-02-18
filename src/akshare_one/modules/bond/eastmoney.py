"""
Eastmoney bond data provider.

This module implements the bond data provider using Eastmoney (东方财富) as the data source.
"""

import pandas as pd

from .base import BondProvider


class EastmoneyBondProvider(BondProvider):
    """
    Bond data provider using Eastmoney as the data source.

    Eastmoney provides comprehensive bond data including:
    - Convertible bond list
    - Historical data
    - Realtime quotes
    """

    def __init__(self):
        """Initialize the Eastmoney bond provider."""
        super().__init__()

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data. Not used directly."""
        return pd.DataFrame()

    def get_bond_list(self) -> pd.DataFrame:
        """
        Get convertible bond list from Eastmoney.

        Returns:
            pd.DataFrame: Bond list
        """
        import akshare as ak

        try:
            df = ak.bond_zh_cov()

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "债券代码": "symbol",
                    "债券简称": "name",
                    "正股代码": "stock_symbol",
                    "正股简称": "stock_name",
                    "正股价": "stock_price",
                    "转股价": "convert_price",
                    "转股价值": "convert_value",
                    "转股溢价率": "premium_rate",
                    "申购日期": "subscribe_date",
                    "上市时间": "list_date",
                    "信用评级": "credit_rating",
                    "发行规模": "issue_size",
                }
            )

            cols = [
                "symbol",
                "name",
                "stock_symbol",
                "stock_name",
                "stock_price",
                "convert_price",
                "convert_value",
                "premium_rate",
                "subscribe_date",
                "list_date",
                "credit_rating",
                "issue_size",
            ]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get bond historical data from Eastmoney.

        Args:
            symbol: Bond symbol (e.g., 'sh113050')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Historical data
        """
        import akshare as ak

        try:
            df = ak.bond_zh_hs_cov_daily(symbol=symbol)

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "date": "date",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "volume": "volume",
                }
            )

            df["symbol"] = symbol

            df["date"] = pd.to_datetime(df["date"])
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)

            df = df[(df["date"] >= start) & (df["date"] <= end)]

            cols = ["date", "symbol", "open", "high", "low", "close", "volume"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_spot(self) -> pd.DataFrame:
        """
        Get bond realtime quotes from Eastmoney.

        Returns:
            pd.DataFrame: Realtime bond data
        """
        import akshare as ak

        try:
            df = ak.bond_zh_cov()

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "债券代码": "symbol",
                    "债券简称": "name",
                    "债现价": "price",
                    "正股代码": "stock_symbol",
                    "正股简称": "stock_name",
                    "正股价": "stock_price",
                    "转股价": "convert_price",
                    "转股价值": "convert_value",
                    "转股溢价率": "premium_rate",
                }
            )

            cols = [
                "symbol",
                "name",
                "price",
                "stock_symbol",
                "stock_name",
                "stock_price",
                "convert_price",
                "convert_value",
                "premium_rate",
            ]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
