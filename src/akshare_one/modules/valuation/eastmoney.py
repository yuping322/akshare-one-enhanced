"""
Eastmoney valuation data provider.

This module implements the valuation data provider using Eastmoney (东方财富) as the data source.
"""

import pandas as pd

from .base import ValuationProvider


class EastmoneyValuationProvider(ValuationProvider):
    """
    Valuation data provider using Eastmoney as the data source.

    Eastmoney provides comprehensive valuation data including:
    - Stock PE, PB, PS, PEG
    - Market cap data
    """

    def __init__(self):
        """Initialize the Eastmoney valuation provider."""
        super().__init__()

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data. Not used directly."""
        return pd.DataFrame()

    def get_stock_valuation(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get stock valuation data from Eastmoney.

        Args:
            symbol: Stock symbol (e.g., '600000')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Valuation data
        """
        import akshare as ak

        try:
            df = ak.stock_value_em()

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "数据日期": "date",
                    "当日收盘价": "close",
                    "当日涨跌幅": "pct_change",
                    "总市值": "market_cap",
                    "流通市值": "float_market_cap",
                    "总股本": "total_shares",
                    "流通股本": "float_shares",
                    "PE(TTM)": "pe_ttm",
                    "PE(静)": "pe_static",
                    "市净率": "pb",
                    "PEG值": "peg",
                    "市现率": "pcf",
                    "市销率": "ps",
                }
            )

            df["symbol"] = symbol

            df["date"] = pd.to_datetime(df["date"])
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)

            df = df[(df["date"] >= start) & (df["date"] <= end)]

            cols = [
                "date",
                "symbol",
                "close",
                "pct_change",
                "pe_ttm",
                "pe_static",
                "pb",
                "ps",
                "pcf",
                "peg",
                "market_cap",
                "float_market_cap",
                "total_shares",
                "float_shares",
            ]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_market_valuation(self) -> pd.DataFrame:
        """
        Get market-wide valuation data from Eastmoney.

        Note: Uses A-share index data as proxy.

        Returns:
            pd.DataFrame: Market valuation data
        """
        import akshare as ak

        try:
            df = ak.stock_a_pe_and_pb_em(symbol="上证指数")

            if df.empty:
                return pd.DataFrame()

            df = df.rename(columns={"date": "date", "pe": "pe", "pb": "pb"})

            df["index_name"] = "上证指数"

            cols = ["date", "index_name", "pe", "pb"]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
