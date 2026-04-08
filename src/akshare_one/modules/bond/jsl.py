"""
JiSiLu (集思录) bond data provider.

This module implements the bond data provider using JiSiLu as the data source.
"""

import pandas as pd

from .base import BondFactory, BondProvider


@BondFactory.register("jsl")
class JslBondProvider(BondProvider):
    """
    Bond data provider using JiSiLu (集思录) as the data source.

    JiSiLu provides comprehensive convertible bond data including:
    - Bond list with detailed metrics
    - Premium rate analysis
    - Double low strategy data
    """

    _API_MAP = {
        "get_bond_list": {
            "ak_func": "bond_cb_jsl",
        },
        "get_bond_hist": {
            "ak_func": None,
        },
        "get_bond_realtime": {
            "ak_func": "bond_cb_jsl",
        },
        "get_bond_spot": {
            "ak_func": "bond_cb_jsl",
        },
        "get_bond_premium": {
            "ak_func": "bond_cb_jsl",
        },
    }

    def __init__(self, **kwargs):
        """Initialize the JiSiLu bond provider."""
        super().__init__(**kwargs)

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "jsl"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data. Not used directly."""
        return pd.DataFrame()

    def get_bond_list(self) -> pd.DataFrame:
        """
        Get convertible bond list from JiSiLu.

        Returns:
            pd.DataFrame: Bond list
        """
        import akshare as ak

        try:
            df = ak.bond_cb_jsl()

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "代码": "symbol",
                    "转债名称": "name",
                    "现价": "price",
                    "涨跌幅": "pct_change",
                    "正股代码": "stock_symbol",
                    "正股名称": "stock_name",
                    "正股价": "stock_price",
                    "正股涨跌": "stock_pct_change",
                    "转股价": "convert_price",
                    "转股价值": "convert_value",
                    "转股溢价率": "premium_rate",
                    "债券评级": "credit_rating",
                    "剩余规模": "remaining_size",
                    "到期时间": "maturity_date",
                    "剩余年限": "remaining_years",
                    "到期税前收益": "ytm",
                }
            )

            cols = [
                "symbol",
                "name",
                "price",
                "pct_change",
                "stock_symbol",
                "stock_name",
                "stock_price",
                "convert_price",
                "convert_value",
                "premium_rate",
                "credit_rating",
                "remaining_size",
                "maturity_date",
                "remaining_years",
                "ytm",
            ]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get bond historical data.

        Note: JiSiLu doesn't provide direct historical data API.
        Use Eastmoney provider for historical data.

        Args:
            symbol: Bond symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame(columns=["date", "symbol", "open", "high", "low", "close", "volume"])

    def get_bond_realtime(self) -> pd.DataFrame:
        """Get bond realtime quotes (alias for get_bond_spot)."""
        return self.get_bond_spot()

    def get_bond_spot(self) -> pd.DataFrame:
        """
        Get bond realtime quotes from JiSiLu.

        Returns:
            pd.DataFrame: Realtime bond data
        """
        import akshare as ak

        try:
            df = ak.bond_cb_jsl()

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "代码": "symbol",
                    "转债名称": "name",
                    "现价": "price",
                    "涨跌幅": "pct_change",
                    "正股代码": "stock_symbol",
                    "正股名称": "stock_name",
                    "正股价": "stock_price",
                    "转股价": "convert_price",
                    "转股价值": "convert_value",
                    "转股溢价率": "premium_rate",
                    "成交额": "amount",
                    "换手率": "turnover",
                }
            )

            cols = [
                "symbol",
                "name",
                "price",
                "pct_change",
                "stock_symbol",
                "stock_name",
                "stock_price",
                "convert_price",
                "convert_value",
                "premium_rate",
                "amount",
                "turnover",
            ]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_bond_premium(self, symbol: str) -> pd.DataFrame:
        """
        Get bond premium rate data from JiSiLu.

        Args:
            symbol: Bond symbol (6-digit code)

        Returns:
            pd.DataFrame: Bond premium data
        """
        import akshare as ak

        try:
            df = ak.bond_cb_jsl()

            if df.empty:
                return pd.DataFrame()

            # Filter by symbol if provided
            if symbol:
                df = df[df["代码"] == symbol.zfill(6)]

            df = df.rename(
                columns={
                    "代码": "symbol",
                    "转债名称": "name",
                    "现价": "price",
                    "正股价": "stock_price",
                    "转股价": "convert_price",
                    "转股价值": "convert_value",
                    "转股溢价率": "premium_rate",
                    "剩余年限": "remaining_years",
                    "到期税前收益": "ytm",
                }
            )

            cols = [
                "symbol",
                "name",
                "price",
                "stock_price",
                "convert_price",
                "convert_value",
                "premium_rate",
                "remaining_years",
                "ytm",
            ]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
