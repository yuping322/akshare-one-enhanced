"""
Lixinger provider for fund company data.

This module implements fund company data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import FundCompanyFactory, FundCompanyProvider


@FundCompanyFactory.register("lixinger")
class LixingerFundCompanyProvider(FundCompanyProvider):
    """
    Fund company data provider using Lixinger OpenAPI.

    Provides fund company info, fund list, fund manager list, shareholdings, and asset scale.
    """

    _API_MAP = {}

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_fund_company_info(self, stock_codes: list[str] | None = None, **kwargs) -> pd.DataFrame:
        """
        Get fund company information from Lixinger.

        Args:
            stock_codes: List of fund company codes (optional, returns all if not specified)

        Returns:
            pd.DataFrame: Fund company information with name, stock_code, inception_date, funds_num, asset_scale, fund_collection_type
        """
        client = get_lixinger_client()

        params = {}
        if stock_codes:
            params["stockCodes"] = stock_codes

        response = client.query_api("cn/fund-company", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "name": "name",
                "stockCode": "symbol",
                "inceptionDate": "inception_date",
                "fundsNum": "funds_num",
                "assetScale": "asset_scale",
                "fundCollectionType": "fund_collection_type",
            }
        )

        if "inception_date" in df.columns:
            df["inception_date"] = pd.to_datetime(df["inception_date"], errors="coerce").dt.strftime("%Y-%m-%d")

        numeric_cols = ["funds_num", "asset_scale"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_company_fund_list(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get fund list managed by fund company from Lixinger.

        Args:
            stock_codes: List of fund company codes (1-100 codes)

        Returns:
            pd.DataFrame: Fund list data with company_code, fund_code
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        response = client.query_api("cn/fund-company/fund-list", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        rows = []
        for item in data:
            company_code = item.get("stockCode")
            fund_codes = item.get("fundCodes", [])
            for fund_code in fund_codes:
                rows.append({"company_code": company_code, "fund_code": fund_code})

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_company_fund_manager_list(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get fund manager list of fund company from Lixinger.

        Args:
            stock_codes: List of fund company codes (1-100 codes)

        Returns:
            pd.DataFrame: Fund manager list data with company_code, manager_code
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        response = client.query_api("cn/fund-company/fund-manager-list", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        rows = []
        for item in data:
            company_code = item.get("stockCode")
            manager_codes = item.get("fundManagerCodes", [])
            for manager_code in manager_codes:
                rows.append({"company_code": company_code, "manager_code": manager_code})

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_company_shareholdings(
        self,
        stock_code: str,
        start_date: str,
        market: str,
        end_date: str | None = None,
        limit: int | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund company shareholdings data from Lixinger.

        Args:
            stock_code: Fund company code
            start_date: Start date (YYYY-MM-DD)
            market: Stock market ('a' for A-share, 'h' for Hong Kong)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Shareholdings data with date, holdings, market_cap, stock_code
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date, "market": market}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund-company/shareholdings", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "holdings": "holdings",
                "marketCap": "market_cap",
                "stockCode": "stock_code",
            }
        )

        df["company_code"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        numeric_cols = ["holdings", "market_cap"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_company_asset_scale(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund company asset scale data from Lixinger.

        Args:
            stock_code: Fund company code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Asset scale data with date, equity_asset_scale, hybrid_asset_scale, qdii_asset_scale, bond_asset_scale
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund-company/asset-scale", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "equityAssetScale": "equity_asset_scale",
                "hybridAssetScale": "hybrid_asset_scale",
                "qdiiAssetScale": "qdii_asset_scale",
                "bondAssetScale": "bond_asset_scale",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        numeric_cols = ["equity_asset_scale", "hybrid_asset_scale", "qdii_asset_scale", "bond_asset_scale"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )
