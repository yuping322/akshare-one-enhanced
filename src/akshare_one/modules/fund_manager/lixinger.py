"""
Lixinger provider for fund manager data.

This module implements fund manager data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import FundManagerFactory, FundManagerProvider


@FundManagerFactory.register("lixinger")
class LixingerFundManagerProvider(FundManagerProvider):
    """
    Fund manager data provider using Lixinger OpenAPI.

    Provides fund manager info, hot fund manager, management funds, profit ratio, and shareholdings.
    """

    _API_MAP = {}

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_fund_manager_info(self, stock_codes: list[str] | None = None, **kwargs) -> pd.DataFrame:
        """
        Get fund manager information from Lixinger.

        Args:
            stock_codes: List of fund manager codes (optional, returns all if not specified)

        Returns:
            pd.DataFrame: Fund manager information with name, birth_year, resume, stock_code, gender
        """
        client = get_lixinger_client()

        params = {}
        if stock_codes:
            params["stockCodes"] = stock_codes

        response = client.query_api("cn/fund-manager", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "name": "name",
                "birthYear": "birth_year",
                "resume": "resume",
                "stockCode": "symbol",
                "gender": "gender",
            }
        )

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_manager_hot_fmp(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get hot fund manager profit ratio (收益率) data from Lixinger.

        Args:
            stock_codes: List of fund manager codes (1-100 codes)

        Returns:
            pd.DataFrame: Profit ratio data with various return metrics and rankings
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        response = client.query_api("cn/fund-manager/hot/fmp", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        rename = {
            "stockCode": "symbol",
            "fm_p_r_d": "profit_ratio_date",
            "fm_p_r_fys": "return_ytd",
            "fm_p_r_m1": "return_1m",
            "fm_p_r_m3": "return_3m",
            "fm_p_r_m6": "return_6m",
            "fm_p_r_y1": "return_1y",
            "fm_p_r_y3": "return_3y",
            "fm_p_r_y5": "return_5y",
            "fm_p_r_y10": "return_10y",
            "fm_cagr_p_r_fs": "cagr_since_start",
            "fm_p_r_fys_rp": "rank_ytd",
            "fm_p_r_m1_rp": "rank_1m",
            "fm_p_r_m3_rp": "rank_3m",
            "fm_p_r_m6_rp": "rank_6m",
            "fm_p_r_y1_rp": "rank_1y",
            "fm_p_r_y3_rp": "rank_3y",
            "fm_p_r_y5_rp": "rank_5y",
            "fm_p_r_y10_rp": "rank_10y",
            "fm_cagr_p_r_fs_rp": "rank_cagr_since_start",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

        if "profit_ratio_date" in df.columns:
            df["profit_ratio_date"] = pd.to_datetime(df["profit_ratio_date"], errors="coerce").dt.strftime("%Y-%m-%d")

        numeric_cols = [
            "return_ytd",
            "return_1m",
            "return_3m",
            "return_6m",
            "return_1y",
            "return_3y",
            "return_5y",
            "return_10y",
            "cagr_since_start",
            "rank_ytd",
            "rank_1m",
            "rank_3m",
            "rank_6m",
            "rank_1y",
            "rank_3y",
            "rank_5y",
            "rank_10y",
            "rank_cagr_since_start",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_manager_management_funds(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get funds managed by fund manager from Lixinger.

        Args:
            stock_codes: List of fund manager codes (1-100 codes)

        Returns:
            pd.DataFrame: Managed funds data with fund name, code, appointment_date, departure_date
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        response = client.query_api("cn/fund-manager/management-funds", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        rows = []
        for item in data:
            manager_code = item.get("stockCode")
            funds = item.get("funds", [])
            for fund in funds:
                rows.append(
                    {
                        "manager_code": manager_code,
                        "fund_name": fund.get("name"),
                        "fund_code": fund.get("code"),
                        "appointment_date": fund.get("appointmentDate"),
                        "departure_date": fund.get("departureDate"),
                    }
                )

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)

        if "appointment_date" in df.columns:
            df["appointment_date"] = pd.to_datetime(df["appointment_date"], errors="coerce").dt.strftime("%Y-%m-%d")

        if "departure_date" in df.columns:
            df["departure_date"] = pd.to_datetime(df["departure_date"], errors="coerce").dt.strftime("%Y-%m-%d")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_manager_profit_ratio(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund manager profit ratio data from Lixinger.

        Args:
            stock_code: Fund manager code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Profit ratio data with date, start_date, value
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund-manager/profit-ratio", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "startDate": "calc_start_date",
                "value": "value",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        if "calc_start_date" in df.columns:
            df["calc_start_date"] = pd.to_datetime(df["calc_start_date"], errors="coerce").dt.strftime("%Y-%m-%d")

        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_manager_shareholdings(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund manager shareholdings data from Lixinger.

        Args:
            stock_code: Fund manager code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Shareholdings data with date, market_cap, holdings, holdings_to_cc_ratio, stock_code
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund-manager/shareholdings", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "marketCap": "market_cap",
                "holdings": "holdings",
                "holdingsToCcRatio": "holdings_to_cc_ratio",
                "stockCode": "stock_code",
            }
        )

        df["manager_code"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        numeric_cols = ["market_cap", "holdings", "holdings_to_cc_ratio"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )
