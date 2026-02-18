"""
Eastmoney shareholder data provider.

This module implements the shareholder data provider using Eastmoney (东方财富) as the data source.
"""

import pandas as pd

from .base import ShareholderProvider


class EastmoneyShareholderProvider(ShareholderProvider):
    """
    Shareholder data provider using Eastmoney as the data source.

    Eastmoney provides comprehensive shareholder data including:
    - Top shareholders
    - Institution holdings
    """

    def __init__(self):
        """Initialize the Eastmoney shareholder provider."""
        super().__init__()

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data. Not used directly."""
        return pd.DataFrame()

    def get_shareholder_changes(
        self,
        symbol: str | None = None,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
    ) -> pd.DataFrame:
        """
        Get shareholder changes from Eastmoney.

        Note: Uses SSE data as fallback.

        Args:
            symbol: Stock symbol (optional)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Shareholder changes
        """
        import akshare as ak

        try:
            df = ak.stock_share_hold_change_sse()

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "公司代码": "symbol",
                    "公司名称": "name",
                    "姓名": "holder_name",
                    "职务": "position",
                    "变动数": "change_shares",
                    "变动原因": "reason",
                    "变动日期": "change_date",
                }
            )

            if symbol:
                df = df[df["symbol"] == symbol]

            df["change_date"] = pd.to_datetime(df["change_date"])
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)

            df = df[(df["change_date"] >= start) & (df["change_date"] <= end)]

            cols = [
                "symbol",
                "name",
                "holder_name",
                "position",
                "change_shares",
                "reason",
                "change_date",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_top_shareholders(self, symbol: str) -> pd.DataFrame:
        """
        Get top shareholders from Eastmoney.

        Note: API may be unstable.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Top shareholders
        """
        import akshare as ak

        try:
            df = ak.stock_institute_hold(symbol=symbol)

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "证券代码": "symbol",
                    "证券简称": "name",
                    "机构数": "institution_count",
                    "机构数变化": "institution_change",
                    "持股比例": "holding_pct",
                    "持股比例增幅": "holding_pct_change",
                }
            )

            cols = [
                "symbol",
                "name",
                "institution_count",
                "institution_change",
                "holding_pct",
                "holding_pct_change",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_institution_holdings(self, symbol: str) -> pd.DataFrame:
        """
        Get institution holdings from Eastmoney.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Institution holdings
        """
        import akshare as ak

        try:
            df = ak.stock_institute_hold(symbol=symbol)

            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "证券代码": "symbol",
                    "证券简称": "name",
                    "机构数": "institution_count",
                    "持股比例": "holding_pct",
                    "占流通股比例": "float_holding_pct",
                }
            )

            cols = ["symbol", "name", "institution_count", "holding_pct", "float_holding_pct"]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
