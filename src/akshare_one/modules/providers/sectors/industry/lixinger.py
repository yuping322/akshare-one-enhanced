"""
Lixinger provider for industry data.

This module implements industry data provider using Lixinger OpenAPI.
"""

import pandas as pd

from .....lixinger_client import get_lixinger_client
from .base import IndustryFactory, IndustryProvider


@IndustryFactory.register("lixinger")
class LixingerIndustryProvider(IndustryProvider):
    """
    Industry data provider using Lixinger OpenAPI.

    Provides industry info, constituents, fundamentals, financial statements,
    mutual market data, margin trading data.
    """

    def get_source_name(self) -> str:
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_industry_list(
        self, source: str = "sw_2021", level: str = None, stock_codes: list = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get industry list from Lixinger.

        Args:
            source: Industry source ('sw', 'sw_2021', 'cni')
            level: Industry level ('one', 'two', 'three')
            stock_codes: List of industry codes to filter

        Returns:
            pd.DataFrame: Industry list
        """
        client = get_lixinger_client()

        params = {"source": source}
        if level:
            params["level"] = level
        if stock_codes:
            params["stockCodes"] = stock_codes

        response = client.query_api("cn/industry", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_industry_stocks(
        self, industry: str, date: str = "latest", source: str = "sw_2021", **kwargs
    ) -> pd.DataFrame:
        """
        Get constituent stocks for an industry from Lixinger.

        Args:
            industry: Industry code (e.g., '490000')
            date: Date string ('latest' or YYYY-MM-DD)
            source: Industry source ('sw_2021')

        Returns:
            pd.DataFrame: Constituent stocks
        """
        client = get_lixinger_client()

        api_suffix = f"cn/industry/constituents/{source}"
        params = {"stockCodes": [industry], "date": date}

        response = client.query_api(api_suffix, params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        flattened_data = []
        for item in data:
            if "constituents" in item and isinstance(item["constituents"], list):
                flattened_data.extend(item["constituents"])
            else:
                flattened_data.append(item)

        df = pd.json_normalize(flattened_data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_industry_fundamental(
        self,
        stock_codes: list,
        metrics_list: list = None,
        date: str = None,
        start_date: str = None,
        end_date: str = None,
        source: str = "sw_2021",
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get industry fundamental data (PE, PB, etc.) from Lixinger.

        Args:
            stock_codes: List of industry codes
            metrics_list: List of metrics (e.g., ['pe_ttm.mcw', 'mc'])
            date: Single date (YYYY-MM-DD)
            start_date: Start date for range query
            end_date: End date for range query
            source: Industry source ('sw_2021')

        Returns:
            pd.DataFrame: Fundamental data
        """
        client = get_lixinger_client()

        api_suffix = f"cn/industry/fundamental/{source}"

        params = {"stockCodes": stock_codes}
        if metrics_list:
            params["metricsList"] = metrics_list
        else:
            params["metricsList"] = ["mc", "pe_ttm.mcw", "pb.mcw"]

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

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

    def get_industry_financial_statements(
        self,
        stock_codes: list,
        metrics_list: list,
        date: str = None,
        start_date: str = None,
        end_date: str = None,
        source: str = "sw_2021",
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get industry financial statement data from Lixinger.

        Args:
            stock_codes: List of industry codes
            metrics_list: List of metrics (e.g., ['q.ps.oi.t', 'q.bs.ar.c_y2y'])
            date: Single date (YYYY-MM-DD or 'latest')
            start_date: Start date for range query
            end_date: End date for range query
            source: Industry source ('sw_2021')

        Returns:
            pd.DataFrame: Financial statement data
        """
        client = get_lixinger_client()

        api_suffix = f"cn/industry/fs/{source}/hybrid"

        params = {"stockCodes": stock_codes, "metricsList": metrics_list}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

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

    def get_industry_hot_mutual_market(self, stock_codes: list, source: str = "sw_2021", **kwargs) -> pd.DataFrame:
        """
        Get industry hot mutual market data from Lixinger.

        Args:
            stock_codes: List of industry codes
            source: Industry source ('sw_2021')

        Returns:
            pd.DataFrame: Hot mutual market data
        """
        client = get_lixinger_client()

        api_suffix = f"cn/industry/hot/mm_ha/{source}"
        params = {"stockCodes": stock_codes}

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

    def get_industry_margin_trading(
        self, stock_code: str, start_date: str, end_date: str = None, source: str = "sw_2021", **kwargs
    ) -> pd.DataFrame:
        """
        Get industry margin trading data from Lixinger.

        Args:
            stock_code: Industry code (single code only)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            source: Industry source ('sw_2021')

        Returns:
            pd.DataFrame: Margin trading data
        """
        client = get_lixinger_client()

        api_suffix = f"cn/industry/margin-trading-and-securities-lending/{source}"

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

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

    def get_industry_mutual_market(
        self, stock_code: str, start_date: str, end_date: str = None, source: str = "sw_2021", **kwargs
    ) -> pd.DataFrame:
        """
        Get industry mutual market data from Lixinger.

        Args:
            stock_code: Industry code (single code only)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            source: Industry source ('sw_2021')

        Returns:
            pd.DataFrame: Mutual market data
        """
        client = get_lixinger_client()

        api_suffix = f"cn/industry/mutual-market/{source}"

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

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
