"""
Lixinger provider for macro economic data.

This module implements macro economic data provider using Lixinger OpenAPI.
"""

import pandas as pd

from .base import MacroProvider, MacroFactory
from ...lixinger_client import get_lixinger_client


@MacroFactory.register("lixinger")
class LixingerMacroProvider(MacroProvider):
    """
    Macro economic data provider using Lixinger OpenAPI.

    Provides GDP, CPI, interest rates, money supply, etc.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_cpi_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get CPI data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: CPI data
        """
        client = get_lixinger_client()

        params = {"startDate": start_date, "endDate": end_date}

        response = client.query_api("macro/price-index", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_m2_supply(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get M2 money supply data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: M2 data
        """
        client = get_lixinger_client()

        params = {"startDate": start_date, "endDate": end_date}

        response = client.query_api("macro/money-supply", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_social_financing(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get social financing data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Social financing data
        """
        client = get_lixinger_client()

        params = {"startDate": start_date, "endDate": end_date}

        response = client.query_api("macro/social-financing", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_lpr_rate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get LPR interest rate data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: LPR data
        """
        client = get_lixinger_client()

        params = {"startDate": start_date, "endDate": end_date}

        response = client.query_api("macro/interest-rates", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_gdp(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get GDP data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            area_code: Area code ('cn' for China, 'us' for USA). Default: 'cn'
            metrics_list: List of metrics (e.g., ['q.gdp.t', 'q.gdp.t_y2y'])
            limit: Number of recent data points to return

        Returns:
            pd.DataFrame: GDP data
        """
        client = get_lixinger_client()

        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": kwargs.get("area_code", "cn"),
            "metricsList": kwargs.get("metrics_list", ["q.gdp.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("macro/gdp", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_foreign_trade(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get foreign trade data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            area_code: Area code ('cn' for China). Default: 'cn'
            metrics_list: List of metrics (e.g., ['m.tiae_rmb.t', 'm.te_usd.t'])
            limit: Number of recent data points to return

        Returns:
            pd.DataFrame: Foreign trade data
        """
        client = get_lixinger_client()

        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": kwargs.get("area_code", "cn"),
            "metricsList": kwargs.get("metrics_list", ["m.tiae_rmb.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("macro/foreign-trade", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )
