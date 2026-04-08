"""
Lixinger provider for ETF/fund data.

This module implements ETF/fund data provider using Lixinger OpenAPI.
"""

import pandas as pd

from .base import ETFProvider, ETFFactory
from ...lixinger_client import get_lixinger_client


@ETFFactory.register("lixinger")
class LixingerETFProvider(ETFProvider):
    """
    ETF/fund data provider using Lixinger OpenAPI.

    Provides fund info and holdings data.
    """

    _API_MAP = {}

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_fund_info(self, stock_codes: list[str] | None = None, page_index: int = 0, **kwargs) -> pd.DataFrame:
        """
        Get fund information from Lixinger.

        Args:
            stock_codes: List of fund codes (optional, returns all funds if not specified)
            page_index: Page index (default 0)

        Returns:
            pd.DataFrame: Fund information
        """
        client = get_lixinger_client()

        params = {"pageIndex": page_index}
        if stock_codes:
            params["stockCodes"] = stock_codes

        response = client.query_api("cn/fund", params)

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
                "fundFirstLevel": "fund_first_level",
                "fundSecondLevel": "fund_second_level",
                "shortName": "short_name",
                "areaCode": "area_code",
                "market": "market",
                "exchange": "exchange",
                "inceptionDate": "inception_date",
                "delistedDate": "delisted_date",
            }
        )

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_holdings(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund holdings data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Fund holdings data
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/shareholdings", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "stockCode": "stock_code",
                "stockAreaCode": "stock_area_code",
                "holdings": "holdings",
                "marketCap": "market_cap",
                "netValueRatio": "net_value_ratio",
            }
        )

        df["fund_code"] = stock_code

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )
