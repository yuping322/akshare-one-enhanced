"""
Lixinger provider for block deal data.

This module implements block deal data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import BlockDealFactory, BlockDealProvider


@BlockDealFactory.register("lixinger")
class LixingerBlockDealProvider(BlockDealProvider):
    """
    Block deal data provider using Lixinger OpenAPI.

    Provides block deal transaction details from Lixinger API.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_block_deal(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get block deal transaction details from Lixinger.

        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Block deal data with standardized fields
        """
        self.validate_date_range(start_date, end_date)
        if symbol:
            self.validate_symbol(symbol)

        client = get_lixinger_client()

        params = {"startDate": start_date, "endDate": end_date}
        if symbol:
            params["stockCode"] = symbol

        response = client.query_api("cn/company/block-deal", params)

        if response.get("code") != 1:
            return self.create_empty_dataframe(
                [
                    "date",
                    "symbol",
                    "name",
                    "price",
                    "volume",
                    "amount",
                    "buyer_branch",
                    "seller_branch",
                    "premium_rate",
                ]
            )

        data = response.get("data", [])
        if not data:
            return self.create_empty_dataframe(
                [
                    "date",
                    "symbol",
                    "name",
                    "price",
                    "volume",
                    "amount",
                    "buyer_branch",
                    "seller_branch",
                    "premium_rate",
                ]
            )

        df = pd.json_normalize(data)

        standardized = pd.DataFrame()
        standardized["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        standardized["symbol"] = df["stockCode"].astype(str).str.zfill(6)
        standardized["name"] = None
        standardized["price"] = pd.to_numeric(df["tradingPrice"], errors="coerce")
        standardized["volume"] = pd.to_numeric(df["tradingVolume"], errors="coerce")
        standardized["amount"] = pd.to_numeric(df["tradingAmount"], errors="coerce")
        standardized["buyer_branch"] = df["buyBranch"].astype(str) if "buyBranch" in df.columns else None
        standardized["seller_branch"] = df["sellBranch"].astype(str) if "sellBranch" in df.columns else None
        standardized["premium_rate"] = pd.to_numeric(df.get("discountRate"), errors="coerce")

        return self.ensure_json_compatible(standardized.reset_index(drop=True))

    def get_block_deal_summary(self, start_date: str, end_date: str, group_by: str, **kwargs) -> pd.DataFrame:
        """
        Get block deal summary statistics from Lixinger.

        Note: Lixinger doesn't provide summary API directly.
        This method aggregates from block deal data.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            group_by: Grouping dimension ('stock', 'date', or 'broker')

        Returns:
            pd.DataFrame: Summary statistics
        """
        self.validate_date_range(start_date, end_date)

        if group_by not in ["stock", "date", "broker"]:
            raise ValueError(f"Invalid group_by: {group_by}. Must be 'stock', 'date', or 'broker'")

        all_data = self.get_block_deal(None, start_date, end_date)

        if all_data.empty:
            if group_by == "stock":
                return self.create_empty_dataframe(["symbol", "name", "deal_count", "total_amount", "avg_premium_rate"])
            elif group_by == "date":
                return self.create_empty_dataframe(["date", "deal_count", "total_amount", "avg_premium_rate"])
            else:
                return self.create_empty_dataframe(["broker_name", "deal_count", "total_amount", "avg_premium_rate"])

        if group_by == "stock":
            summary = (
                all_data.groupby(["symbol", "name"])
                .agg({"amount": ["count", "sum"], "premium_rate": "mean"})
                .reset_index()
            )
            summary.columns = ["symbol", "name", "deal_count", "total_amount", "avg_premium_rate"]

        elif group_by == "date":
            summary = all_data.groupby("date").agg({"amount": ["count", "sum"], "premium_rate": "mean"}).reset_index()
            summary.columns = ["date", "deal_count", "total_amount", "avg_premium_rate"]

        else:
            buyer_summary = (
                all_data.groupby("buyer_branch").agg({"amount": ["count", "sum"], "premium_rate": "mean"}).reset_index()
            )
            buyer_summary.columns = ["broker_name", "deal_count", "total_amount", "avg_premium_rate"]

            seller_summary = (
                all_data.groupby("seller_branch")
                .agg({"amount": ["count", "sum"], "premium_rate": "mean"})
                .reset_index()
            )
            seller_summary.columns = ["broker_name", "deal_count", "total_amount", "avg_premium_rate"]

            summary = (
                pd.concat([buyer_summary, seller_summary])
                .groupby("broker_name")
                .agg({"deal_count": "sum", "total_amount": "sum", "avg_premium_rate": "mean"})
                .reset_index()
            )

        return self.ensure_json_compatible(summary)
