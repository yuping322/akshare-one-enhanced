"""
Lixinger provider for HK stock data.

This module implements HK stock data provider using Lixinger OpenAPI.
"""

import pandas as pd

from .base import HKUSProvider, HKUSFactory
from ...lixinger_client import get_lixinger_client


@HKUSFactory.register("lixinger")
class LixingerHkusProvider(HKUSProvider):
    """
    HK stock data provider using Lixinger OpenAPI.

    Provides HK company info and index info.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_hk_company_info(
        self,
        stock_codes: list[str] | None = None,
        fs_table_type: str | None = None,
        mutual_markets: list[str] | None = None,
        include_delisted: bool = False,
        page_index: int = 0,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company information from Lixinger.

        Args:
            stock_codes: List of stock codes (e.g., ['00700']). None returns all stocks.
            fs_table_type: Financial statement type. Options:
                - 'non_financial': Non-financial companies
                - 'bank': Banks
                - 'security': Securities
                - 'insurance': Insurance
                - 'reit': Real estate investment trusts
                - 'other_financial': Other financial institutions
            mutual_markets: Mutual market types. Options: ['ah'] for HK-SZ/HK-SH stocks
            include_delisted: Whether to include delisted stocks
            page_index: Page index (default 0)
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: HK company information
        """
        client = get_lixinger_client()

        params = {"pageIndex": page_index}

        if stock_codes:
            params["stockCodes"] = stock_codes

        if fs_table_type:
            params["fsTableType"] = fs_table_type

        if mutual_markets:
            params["mutualMarkets"] = mutual_markets

        if include_delisted:
            params["includeDelisted"] = True

        response = client.query_api("hk/company", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_info(
        self,
        stock_codes: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index information from Lixinger.

        Args:
            stock_codes: List of index codes (e.g., ['HSI']). None returns all indices.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: HK index information
        """
        client = get_lixinger_client()

        params = {}

        if stock_codes:
            params["stockCodes"] = stock_codes

        response = client.query_api("hk/index", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK stock list (using company info API).

        This is a convenience method that wraps get_hk_company_info().

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: HK stocks information.
        """
        return self.get_hk_company_info(columns=columns, row_filter=row_filter)

    def get_us_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US stock list.

        Note: Lixinger does not provide US stock API, returns empty DataFrame.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Empty DataFrame (not supported).
        """
        self.logger.warning(
            "Lixinger does not provide US stock data",
            extra={
                "context": {
                    "log_type": "unsupported_api",
                    "provider": "lixinger",
                    "api": "us_stocks",
                }
            },
        )
        return pd.DataFrame()
