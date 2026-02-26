"""
Eastmoney ETF data provider.

This module implements the ETF data provider using Eastmoney (东方财富) as the data source.
"""

import pandas as pd

from .base import ETFProvider


class EastmoneyETFProvider(ETFProvider):
    """
    ETF data provider using Eastmoney as the data source.

    Eastmoney provides comprehensive ETF data including:
    - Realtime quotes
    - Historical data
    - Fund manager information
    - Fund ratings
    """

    def __init__(self):
        """Initialize the Eastmoney ETF provider."""
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

    def get_etf_hist(self, symbol: str, start_date: str, end_date: str, interval: str = "daily") -> pd.DataFrame:
        """
        Get ETF historical data from Eastmoney.

        Args:
            symbol: ETF symbol (6-digit code)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('daily', 'weekly', 'monthly')

        Returns:
            pd.DataFrame: Standardized historical data
        """
        import akshare as ak

        period_map = {"daily": "daily", "weekly": "weekly", "monthly": "monthly"}

        period = period_map.get(interval, "daily")

        df = ak.fund_etf_hist_em(symbol=symbol, period=period, adjust="")

        if df.empty:
            return pd.DataFrame()

        df = self._standardize_hist_data(df, symbol)

        df = self._filter_by_date(df, start_date, end_date)

        return df

    def get_etf_spot(self) -> pd.DataFrame:
        """
        Get all ETF realtime quotes from Eastmoney.

        Returns:
            pd.DataFrame: Realtime ETF data
        """
        import akshare as ak

        df = ak.fund_etf_spot_em()

        if df.empty:
            return pd.DataFrame()

        return self._standardize_spot_data(df)

    def get_etf_list(self, category: str = "all") -> pd.DataFrame:
        """
        Get ETF list from Eastmoney.

        Args:
            category: ETF category ('all', 'stock', 'bond', 'cross', 'money')

        Returns:
            pd.DataFrame: ETF list
        """
        import akshare as ak

        df = ak.fund_etf_spot_em()

        if df.empty:
            return pd.DataFrame()

        df = df[["代码", "名称"]].copy()
        df.columns = ["symbol", "name"]

        df["type"] = "etf"

        return df

    def get_fund_manager(self) -> pd.DataFrame:
        """
        Get fund manager information from Eastmoney.

        Returns:
            pd.DataFrame: Fund manager data
        """
        import akshare as ak

        df = ak.fund_manager_em()

        if df.empty:
            return pd.DataFrame()

        df = df.rename(
            columns={
                "姓名": "manager_name",
                "所属公司": "company",
                "现任基金代码": "fund_symbol",
                "现任基金": "fund_name",
                "累计从业时间": "tenure_days",
                "现任基金资产总规模": "aum_billion",
                "现任基金最佳回报": "best_return_pct",
            }
        )

        df = df[
            [
                "manager_name",
                "company",
                "fund_symbol",
                "fund_name",
                "tenure_days",
                "aum_billion",
                "best_return_pct",
            ]
        ]

        return df

    def get_fund_rating(self) -> pd.DataFrame:
        """
        Get fund ratings from Eastmoney.

        Returns:
            pd.DataFrame: Fund rating data
        """
        import akshare as ak

        df = ak.fund_rating_all()

        if df.empty:
            return pd.DataFrame()

        df = df.rename(
            columns={
                "代码": "symbol",
                "简称": "name",
                "基金经理": "manager",
                "基金公司": "company",
                "5星评级家数": "star_count",
                "上海证券": "sh_securities_rating",
                "招商证券": "cm_securities_rating",
                "济安金信": "jian_rating",
                "晨星评级": "morningstar_rating",
                "手续费": "fee",
                "类型": "fund_type",
            }
        )

        return df

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
