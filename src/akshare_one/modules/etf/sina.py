"""
Sina ETF data provider.

This module implements the ETF data provider using Sina Finance (新浪财经) as the data source.
"""

import pandas as pd

from .base import ETFProvider


class SinaETFProvider(ETFProvider):
    """
    ETF data provider using Sina Finance as the data source.

    Sina provides ETF data including:
    - ETF categories
    - Fund scale data
    - Dividend information
    """

    def __init__(self):
        """Initialize the Sina ETF provider."""
        super().__init__()

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

    def get_etf_hist(
        self, symbol: str, start_date: str, end_date: str, interval: str = "daily"
    ) -> pd.DataFrame:
        """
        Get ETF historical data from Sina.

        Note: Sina's historical data interface may be limited.
        Falls back to category-based approach.

        Args:
            symbol: ETF symbol (6-digit code)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('daily', 'weekly', 'monthly')

        Returns:
            pd.DataFrame: Standardized historical data
        """
        import akshare as ak

        try:
            df = ak.fund_etf_hist_sina(symbol=symbol)
            if df.empty:
                return pd.DataFrame()

            df = self._standardize_hist_data(df, symbol)
            df = self._filter_by_date(df, start_date, end_date)

            return df
        except Exception:
            return pd.DataFrame()

    def get_etf_spot(self) -> pd.DataFrame:
        """
        Get ETF categories from Sina.

        Note: Sina doesn't provide direct realtime quotes.
        Returns ETF category information instead.

        Returns:
            pd.DataFrame: ETF category data
        """
        import akshare as ak

        try:
            df = ak.fund_etf_category_sina()

            if df.empty:
                return pd.DataFrame()

            return self._standardize_category_data(df)
        except Exception:
            return pd.DataFrame()

    def get_etf_list(self, category: str = "all") -> pd.DataFrame:
        """
        Get ETF list from Sina.

        Args:
            category: ETF category ('all', 'stock', 'bond', 'cross', 'money')

        Returns:
            pd.DataFrame: ETF list
        """
        import akshare as ak

        try:
            df = ak.fund_etf_category_sina()

            if df.empty:
                return pd.DataFrame()

            df = df.rename(columns={"代码": "symbol", "名称": "name", "类型": "type"})

            df = df[["symbol", "name", "type"]]

            return df
        except Exception:
            return pd.DataFrame()

    def get_fund_manager(self) -> pd.DataFrame:
        """
        Get fund manager information.

        Note: Sina doesn't provide dedicated fund manager data.
        Returns empty DataFrame.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame(
            columns=[
                "manager_name",
                "company",
                "fund_symbol",
                "fund_name",
                "tenure_days",
                "aum_billion",
                "best_return_pct",
            ]
        )

    def get_fund_rating(self) -> pd.DataFrame:
        """
        Get fund ratings.

        Note: Sina doesn't provide dedicated fund rating data.
        Returns empty DataFrame.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame(
            columns=[
                "symbol",
                "name",
                "manager",
                "company",
                "star_count",
                "sh_securities_rating",
                "cm_securities_rating",
                "jian_rating",
                "morningstar_rating",
                "fee",
                "fund_type",
            ]
        )

    def _standardize_hist_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Standardize historical data columns."""
        if df.empty:
            return df

        column_map = {
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
        }

        df = df.rename(columns=column_map)

        df["symbol"] = symbol

        return df

    def _standardize_category_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize category data columns."""
        if df.empty:
            return df

        df = df.rename(columns={"代码": "symbol", "名称": "name", "类型": "type"})

        return df

    def _filter_by_date(self, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter dataframe by date range."""
        if df.empty or "date" not in df.columns:
            return df

        df["date"] = pd.to_datetime(df["date"])
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        return df[(df["date"] >= start) & (df["date"] <= end)]
