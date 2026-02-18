"""
SSE (上海证券交易所) shareholder data provider.

This module implements the shareholder data provider using SSE as the data source.
"""

import pandas as pd

from .base import ShareholderProvider


class SSEShareholderProvider(ShareholderProvider):
    """
    Shareholder data provider using SSE (上海证券交易所) as the data source.

    SSE provides shareholder change data:
    - Shareholder changes (增减持)
    """

    def __init__(self):
        """Initialize the SSE shareholder provider."""
        super().__init__()

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "sse"

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
        Get shareholder changes from SSE.

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
                    "变动后持股数": "shares_after",
                    "本次变动前持股数": "shares_before",
                    "本次变动平均价格": "avg_price",
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
                "shares_before",
                "shares_after",
                "avg_price",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()

    def get_top_shareholders(self, symbol: str) -> pd.DataFrame:
        """
        Get top shareholders.

        Note: SSE doesn't provide this data directly.
        Returns empty DataFrame.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame(columns=["rank", "holder_name", "shares", "pct", "change"])

    def get_institution_holdings(self, symbol: str) -> pd.DataFrame:
        """
        Get institution holdings.

        Note: SSE doesn't provide this data directly.
        Returns empty DataFrame.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame(columns=["institution_count", "holding_pct", "change_pct"])
