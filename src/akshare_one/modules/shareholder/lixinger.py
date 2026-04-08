"""
Lixinger provider for shareholder data.

This module implements shareholder data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import ShareholderFactory, ShareholderProvider


@ShareholderFactory.register("lixinger")
class LixingerShareholderProvider(ShareholderProvider):
    """
    Shareholder data provider using Lixinger OpenAPI.

    Provides top 10 shareholders, top 10 float shareholders, and fund shareholders.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data - not directly used.

        Each specific method fetches its own data.
        """
        return pd.DataFrame()

    def get_top10_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get top 10 shareholders from Lixinger.

        Args:
            symbol: Stock symbol (e.g., '600000')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Top 10 shareholders with columns:
                - date: Date
                - symbol: Stock symbol
                - name: Shareholder name
                - holdings: Holdings
                - property: Property type
                - capitalization: Total share capital
                - proportion_of_capitalization: Proportion of total share capital
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/majority-shareholders", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)
        df["symbol"] = symbol

        if "proportionOfCapitalization" in df.columns:
            df = df.rename(columns={"proportionOfCapitalization": "proportion_of_capitalization"})

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_top10_float_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get top 10 float shareholders from Lixinger.

        Args:
            symbol: Stock symbol (e.g., '600000')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Top 10 float shareholders with columns:
                - date: Date
                - symbol: Stock symbol
                - name: Shareholder name
                - holdings: Holdings
                - property: Property type
                - outstanding_shares_a: Outstanding shares A
                - proportion_of_outstanding_shares_a: Proportion of outstanding shares A
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/nolimit-shareholders", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)
        df["symbol"] = symbol

        column_mapping = {
            "outstandingSharesA": "outstanding_shares_a",
            "proportionOfOutstandingSharesA": "proportion_of_outstanding_shares_a",
        }
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get fund shareholders from Lixinger.

        Args:
            symbol: Stock symbol (e.g., '600000')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Fund shareholders with columns:
                - date: Date
                - symbol: Stock symbol
                - fund_code: Fund code
                - name: Fund name
                - holdings: Holdings
                - market_cap: Market cap
                - market_cap_rank: Market cap rank
                - net_value_ratio: Net value ratio
                - outstanding_shares_a: Outstanding shares A
                - proportion_of_capitalization: Proportion of outstanding shares A
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/fund-shareholders", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)
        df["symbol"] = symbol

        column_mapping = {
            "fundCode": "fund_code",
            "marketCap": "market_cap",
            "marketCapRank": "market_cap_rank",
            "netValueRatio": "net_value_ratio",
            "outstandingSharesA": "outstanding_shares_a",
            "proportionOfCapitalization": "proportion_of_capitalization",
        }
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_shareholder_changes(
        self,
        symbol: str | None = None,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get shareholder changes - not supported by Lixinger.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def get_top_shareholders(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get top shareholders - defaults to top 10 shareholders.

        This is an alias for get_top10_shareholders for compatibility.
        """
        return self.get_top10_shareholders(symbol, **kwargs)

    def get_institution_holdings(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get institution holdings - defaults to fund shareholders.

        This is an alias for get_fund_shareholders for compatibility.
        """
        return self.get_fund_shareholders(symbol, **kwargs)
