"""
AkShare provider for FOF (Fund of Funds) data.

This module implements FOF data provider using AkShare as the data source.
"""

import pandas as pd

from .base import FOFFactory, FOFProvider


@FOFFactory.register("akshare")
class AkShareFOFProvider(FOFProvider):
    """
    FOF data provider using AkShare as the data source.

    AkShare provides comprehensive FOF data including:
    - FOF fund list
    - NAV history
    - Fund information
    """

    _API_MAP = {
        "get_fof_list": {
            "ak_func": "fund_open_fund_rank_em",
        },
        "get_fof_nav": {
            "ak_func": "fund_open_fund_info_em",
            "params": {"symbol": "symbol", "indicator": "indicator"},
        },
        "get_fof_info": {
            "ak_func": "fund_open_fund_info_em",
            "params": {"symbol": "symbol", "indicator": "indicator"},
        },
    }

    def __init__(self, **kwargs):
        """Initialize the AkShare FOF provider."""
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

    def get_fof_list(self) -> pd.DataFrame:
        """
        Get FOF list from AkShare.

        Returns:
            pd.DataFrame: FOF fund list
        """
        df = self.akshare_adapter.call("fund_open_fund_rank_em")

        if df.empty:
            return pd.DataFrame()

        return df

    def get_fof_nav(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """
        Get FOF NAV (Net Asset Value) history.

        Args:
            symbol: FOF symbol (6-digit code)
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

    def get_fof_info(self, symbol: str) -> pd.DataFrame:
        """
        Get FOF fund information.

        Args:
            symbol: FOF symbol (6-digit code)

        Returns:
            pd.DataFrame: Fund information
        """
        try:
            df = self.akshare_adapter.call("fund_open_fund_info_em", symbol=symbol, indicator="基金基本信息")

            if df.empty:
                return pd.DataFrame()

            return df
        except Exception:
            return pd.DataFrame()

    def _filter_by_date(self, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter dataframe by date range."""
        if "date" not in df.columns:
            return df

        df["date"] = pd.to_datetime(df["date"])
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        return df[(df["date"] >= start) & (df["date"] <= end)]
