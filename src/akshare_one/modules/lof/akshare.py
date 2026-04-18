"""
AkShare provider for LOF (Listed Open-Ended Fund) data.

This module implements LOF data provider using AkShare as the data source.
"""

import pandas as pd

from ..base import BaseProvider
from .base import LOFFactory, LOFProvider


@LOFFactory.register("akshare")
class AkShareLOFProvider(LOFProvider):
    """
    LOF data provider using AkShare as the data source.

    AkShare provides comprehensive LOF data including:
    - LOF fund list
    - Historical data
    - Realtime quotes
    - NAV history
    """

    _API_MAP = {
        "get_lof_list": {
            "ak_func": "fund_etf_spot_em",
        },
        "get_lof_hist": {
            "ak_func": "fund_etf_hist_em",
            "params": {"symbol": "symbol", "period": "period", "start_date": "start_date", "end_date": "end_date"},
        },
        "get_lof_spot": {
            "ak_func": "fund_etf_spot_em",
        },
        "get_lof_nav": {
            "ak_func": "fund_open_fund_info_em",
            "params": {"symbol": "symbol", "indicator": "indicator"},
        },
    }

    def __init__(self, **kwargs):
        """Initialize the AkShare LOF provider."""
        super().__init__(**kwargs)

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "akshare"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from AkShare.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def get_lof_list(self) -> pd.DataFrame:
        """
        Get LOF list from AkShare.

        Returns:
            pd.DataFrame: LOF fund list
        """
        df = self.akshare_adapter.call("fund_etf_spot_em")

        if df.empty:
            return pd.DataFrame()

        df = df[["代码", "名称"]].copy()
        df.columns = ["symbol", "name"]

        return df

    def get_lof_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get LOF historical data from AkShare.

        Args:
            symbol: LOF symbol (6-digit code)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized historical data
        """
        df = self.akshare_adapter.call(
            "fund_etf_hist_em", symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq"
        )

        if df.empty:
            return pd.DataFrame()

        df = self._standardize_hist_data(df, symbol)

        df = self._filter_by_date(df, start_date, end_date)

        return df

    def get_lof_spot(self) -> pd.DataFrame:
        """
        Get LOF realtime quotes from AkShare.

        Returns:
            pd.DataFrame: Realtime LOF data
        """
        df = self.akshare_adapter.call("fund_etf_spot_em")

        if df.empty:
            return pd.DataFrame()

        return self._standardize_spot_data(df)

    def get_lof_nav(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """
        Get LOF NAV (Net Asset Value) history.

        Args:
            symbol: LOF symbol (6-digit code)
            start_date: Start date (optional)
            end_date: End date (optional)

        Returns:
            pd.DataFrame: NAV history data
        """
        try:
            df = self.akshare_adapter.call("fund_open_fund_info_em", symbol=symbol, indicator="单位净值走势")

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "净值日期": "date",
                    "单位净值": "nav",
                    "累计净值": "accumulated_nav",
                    "日增长率": "daily_growth",
                }
            )

            df["symbol"] = symbol

            cols = ["date", "symbol", "nav", "accumulated_nav", "daily_growth"]
            df = df[[c for c in cols if c in df.columns]]

            if start_date and end_date and "date" in df.columns:
                df = self._filter_by_date(df, start_date, end_date)

            return df
        except Exception:
            return pd.DataFrame()

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

    def _standardize_spot_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize spot data columns."""
        df = df.rename(
            columns={
                "代码": "symbol",
                "名称": "name",
                "最新价": "price",
                "涨跌幅": "pct_change",
                "涨跌额": "change",
                "成交量": "volume",
                "成交额": "amount",
                "开盘价": "open",
                "最高价": "high",
                "最低价": "low",
                "昨收": "prev_close",
                "换手率": "turnover",
            }
        )

        cols = [
            "symbol",
            "name",
            "price",
            "pct_change",
            "change",
            "volume",
            "amount",
            "open",
            "high",
            "low",
            "prev_close",
            "turnover",
        ]

        df = df[[c for c in cols if c in df.columns]]

        return df

    def _filter_by_date(self, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter dataframe by date range."""
        if "date" not in df.columns:
            return df

        df["date"] = pd.to_datetime(df["date"])
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        return df[(df["date"] >= start) & (df["date"] <= end)]
