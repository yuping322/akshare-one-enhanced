"""
Lixinger provider for index data.

This module implements index data provider using Lixinger OpenAPI.
"""

import pandas as pd

from .base import IndexProvider, IndexFactory
from ...lixinger_client import get_lixinger_client


@IndexFactory.register("lixinger")
class LixingerIndexProvider(IndexProvider):
    """
    Index data provider using Lixinger OpenAPI.

    Provides index info, constituents, historical data, fundamentals.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_index_hist(
        self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs
    ) -> pd.DataFrame:
        """
        Get index historical/K-line data from Lixinger.

        Args:
            symbol: Index code (e.g., '000300')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (only 'daily' supported)

        Returns:
            pd.DataFrame: Index historical data
        """
        client = get_lixinger_client()

        if interval != "daily":
            self.logger.warning(
                f"Lixinger only supports daily data. Requested interval '{interval}' will be ignored.",
                extra={
                    "context": {
                        "log_type": "unsupported_interval",
                        "provider": "lixinger",
                        "requested_interval": interval,
                    }
                },
            )

        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/index/candlestick", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_list(self, category: str = "cn", **kwargs) -> pd.DataFrame:
        """
        Get index list from Lixinger.

        Args:
            category: Index category ('cn', 'hk', 'us')

        Returns:
            pd.DataFrame: Index list
        """
        client = get_lixinger_client()

        api_map = {"cn": "cn/index", "hk": "hk/index", "us": "us/index"}

        api_suffix = api_map.get(category, "cn/index")

        params = {}

        response = client.query_api(api_suffix, params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_constituents(self, symbol: str, include_weight: bool = True, **kwargs) -> pd.DataFrame:
        """
        Get index constituent stocks from Lixinger.

        Args:
            symbol: Index code
            include_weight: Whether to include weights

        Returns:
            pd.DataFrame: Index constituents
        """
        client = get_lixinger_client()

        if include_weight:
            api_suffix = "cn/index/constituent-weightings"
            flatten_field = "weightings"
        else:
            api_suffix = "cn/index/constituents"
            flatten_field = "constituents"

        params = {"stockCodes": [symbol], "date": "latest"}

        response = client.query_api(api_suffix, params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        if flatten_field:
            flattened_data = []
            for item in data:
                if flatten_field in item and isinstance(item[flatten_field], list):
                    flattened_data.extend(item[flatten_field])
                else:
                    flattened_data.append(item)
            data = flattened_data

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )
