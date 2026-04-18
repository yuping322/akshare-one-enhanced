"""
Lixinger provider for fund company data.

This module implements fund company data provider using Lixinger OpenAPI.
"""

import time

import pandas as pd

from .....lixinger_client import get_lixinger_client
from .....metrics.stats import get_stats_collector
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
        start_time = time.time()
        try:
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

            result = self.standardize_and_filter(
                df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
            )
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, True)
            except Exception:
                pass
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, False)
            except Exception:
                pass
            raise

    def get_fund_company_fund_list(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get fund list managed by fund company from Lixinger.

        Args:
            stock_codes: List of fund company codes (1-100 codes)

        Returns:
            pd.DataFrame: Fund list data with company_code, fund_code
        """
        start_time = time.time()
        try:
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

            result = self.standardize_and_filter(
                df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
            )
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, True)
            except Exception:
                pass
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, False)
            except Exception:
                pass
            raise

    def get_fund_company_fund_manager_list(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get fund manager list of fund company from Lixinger.

        Args:
            stock_codes: List of fund company codes (1-100 codes)

        Returns:
            pd.DataFrame: Fund manager list data with company_code, manager_code
        """
        start_time = time.time()
        try:
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

            result = self.standardize_and_filter(
                df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
            )
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, True)
            except Exception:
                pass
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, False)
            except Exception:
                pass
            raise

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
        start_time = time.time()
        try:
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

            result = self.standardize_and_filter(
                df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
            )
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, True)
            except Exception:
                pass
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, False)
            except Exception:
                pass
            raise

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
        start_time = time.time()
        try:
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

            result = self.standardize_and_filter(
                df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
            )
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, True)
            except Exception:
                pass
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, False)
            except Exception:
                pass
            raise

    def get_fund_company_hot_asset_scale(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get fund company latest asset scale hot data from Lixinger
        (cn/fund-company/hot/fc_as).

        Args:
            stock_codes: List of fund company codes (1-100)

        Returns:
            pd.DataFrame: Latest asset scale snapshot with fc_as, fc_nb_as,
                fc_h_as, fc_e_as, fc_q_as, fc_b_as
        """
        start_time = time.time()
        try:
            client = get_lixinger_client()
            response = client.query_api("cn/fund-company/hot/fc_as", {"stockCodes": stock_codes})
            if response.get("code") != 1:
                return pd.DataFrame()
            data = response.get("data", [])
            if not data:
                return pd.DataFrame()
            df = pd.json_normalize(data)
            if "stockCode" in df.columns:
                df = df.rename(columns={"stockCode": "symbol"})
            result = self.standardize_and_filter(
                df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
            )
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, True)
            except Exception:
                pass
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                get_stats_collector().record_request("lixinger", duration_ms, False)
            except Exception:
                pass
            raise


"""
Lixinger provider for fund manager data.

This module implements fund manager data provider using Lixinger OpenAPI.
"""

import pandas as pd

from .....lixinger_client import get_lixinger_client
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
