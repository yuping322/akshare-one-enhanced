"""
Lixinger insider data provider.

This module implements insider data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import InsiderDataFactory, InsiderDataProvider


@InsiderDataFactory.register("lixinger")
class LixingerInsiderProvider(InsiderDataProvider):
    """
    Insider data provider using Lixinger OpenAPI.

    Provides major shareholders shares change and senior executive shares change.
    """

    _major_shareholders_column_map = {
        "date": "transaction_date",
        "stockCode": "symbol",
        "shareholderName": "name",
        "changeQuantity": "transaction_shares",
        "sharesChangeRatio": "shares_change_ratio",
        "priceFloor": "price_floor",
        "priceCeiling": "price_ceiling",
        "avgPrice": "transaction_price_per_share",
        "quantityHeldAfterChange": "shares_owned_after_transaction",
        "sharesHeldAfterChange": "shares_held_ratio",
        "sharesChangeAmount": "transaction_value",
    }

    _executive_column_map = {
        "date": "transaction_date",
        "stockCode": "symbol",
        "shareholderName": "name",
        "executiveName": "executive_name",
        "duty": "title",
        "relationBetweenES": "relationship",
        "changeReason": "change_reason",
        "beforeChangeShares": "shares_owned_before_transaction",
        "changedShares": "transaction_shares",
        "afterChangeShares": "shares_owned_after_transaction",
        "avgPrice": "transaction_price_per_share",
        "sharesChangeAmount": "transaction_value",
        "changedSharesForCapitalizationProportion": "shares_change_ratio",
    }

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def _fetch_major_shareholders_change(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        date: str | None = None,
        limit: int | None = None,
    ) -> pd.DataFrame:
        """
        Fetch major shareholders shares change data from Lixinger API.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            date: Specific date (YYYY-MM-DD)
            limit: Number of recent records to return

        Returns:
            pd.DataFrame: Raw major shareholders change data
        """
        client = get_lixinger_client()

        params = {}

        if self.symbol:
            params["stockCode"] = self.symbol

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("cn/company/major-shareholders-shares-change", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        return pd.json_normalize(data)

    def _fetch_executive_change(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        date: str | None = None,
        limit: int | None = None,
    ) -> pd.DataFrame:
        """
        Fetch senior executive shares change data from Lixinger API.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            date: Specific date (YYYY-MM-DD)
            limit: Number of recent records to return

        Returns:
            pd.DataFrame: Raw executive change data
        """
        client = get_lixinger_client()

        params = {}

        if self.symbol:
            params["stockCode"] = self.symbol

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("cn/company/senior-executive-shares-change", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        return pd.json_normalize(data)

    def get_major_shareholders_change(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get major shareholders shares change data.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters:
                - start_date: Start date (YYYY-MM-DD)
                - end_date: End date (YYYY-MM-DD)
                - date: Specific date (YYYY-MM-DD)
                - limit: Number of recent records to return

        Returns:
            pd.DataFrame: Major shareholders change data with columns:
                - symbol: 股票代码
                - transaction_date: 变动日期
                - name: 股东名称
                - transaction_shares: 变动持股量
                - shares_change_ratio: 变动数量占总股本比例
                - price_floor: 增持价格下限
                - price_ceiling: 增持价格上限
                - transaction_price_per_share: 增减持平均价格
                - shares_owned_after_transaction: 变动后持股数量
                - shares_held_ratio: 变动后占比
                - transaction_value: 增减持金额
        """
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        date = kwargs.get("date")
        limit = kwargs.get("limit")

        df = self._fetch_major_shareholders_change(start_date, end_date, date, limit)

        if df.empty:
            return pd.DataFrame()

        df = df.rename(columns=self._major_shareholders_column_map)

        if "transaction_date" in df.columns:
            df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.tz_localize("Asia/Shanghai")

        numeric_cols = [
            "transaction_shares",
            "shares_change_ratio",
            "price_floor",
            "price_ceiling",
            "transaction_price_per_share",
            "shares_owned_after_transaction",
            "shares_held_ratio",
            "transaction_value",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "transaction_date" in df.columns:
            df = df.sort_values("transaction_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_executive_change(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get senior executive shares change data.

        Args:
            columns: Optional column filter
            row_filter: Optional row filter
            **kwargs: Additional parameters:
                - start_date: Start date (YYYY-MM-DD)
                - end_date: End date (YYYY-MM-DD)
                - date: Specific date (YYYY-MM-DD)
                - limit: Number of recent records to return

        Returns:
            pd.DataFrame: Executive change data with columns:
                - symbol: 股票代码
                - transaction_date: 变动日期
                - name: 股东名称
                - executive_name: 高管姓名
                - title: 职务
                - relationship: 持股人与高管关系
                - change_reason: 变动原因
                - shares_owned_before_transaction: 变动前持股量
                - transaction_shares: 变动持股量
                - shares_owned_after_transaction: 变动后持股量
                - transaction_price_per_share: 成交均价
                - transaction_value: 增减持金额
                - shares_change_ratio: 增减持占总股本比例
        """
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        date = kwargs.get("date")
        limit = kwargs.get("limit")

        df = self._fetch_executive_change(start_date, end_date, date, limit)

        if df.empty:
            return pd.DataFrame()

        df = df.rename(columns=self._executive_column_map)

        if "transaction_date" in df.columns:
            df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.tz_localize("Asia/Shanghai")

        numeric_cols = [
            "shares_owned_before_transaction",
            "transaction_shares",
            "shares_owned_after_transaction",
            "transaction_price_per_share",
            "transaction_value",
            "shares_change_ratio",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "transaction_date" in df.columns:
            df = df.sort_values("transaction_date", ascending=False).reset_index(drop=True)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_inner_trade_data(self, **kwargs) -> pd.DataFrame:
        """
        Get insider trade data.

        By default, returns executive change data.
        For major shareholders change, use get_major_shareholders_change().

        Args:
            **kwargs: Additional parameters for get_executive_change()

        Returns:
            pd.DataFrame: Insider trade data
        """
        return self.get_executive_change(**kwargs)
