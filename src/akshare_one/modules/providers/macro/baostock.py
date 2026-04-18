"""
Baostock macro economic data provider.

This module implements the macro data provider using Baostock API
for Chinese macro economic data including deposit rates, loan rates,
reserve ratio, and money supply.
"""

import time

import pandas as pd

from ....logging_config import get_logger, log_api_request
from ...core.cache import cache
from .base import MacroFactory, MacroProvider


@MacroFactory.register("baostock")
class BaostockMacroProvider(MacroProvider):
    """
    Macro economic data provider using Baostock API.

    This provider wraps Baostock functions to fetch macro data including:
    - Deposit rates
    - Loan rates
    - Required reserve ratio
    - Money supply (monthly and yearly)

    Baostock requires login/logout management for all API calls.
    """

    _bs_instance = None
    _is_logged_in = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)
        self._ensure_login()

    @classmethod
    def _ensure_login(cls):
        """Ensure baostock is logged in"""
        if not cls._is_logged_in:
            try:
                import baostock as bs

                cls._bs_instance = bs
                lg = bs.login()
                if lg.error_code == "0":
                    cls._is_logged_in = True
                else:
                    raise ConnectionError(f"Baostock login failed: {lg.error_msg}")
            except ImportError:
                raise ImportError("baostock is not installed. Install it with: pip install baostock")

    @classmethod
    def logout(cls):
        """Logout from baostock"""
        if cls._is_logged_in and cls._bs_instance:
            cls._bs_instance.logout()
            cls._is_logged_in = False

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "baostock"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Baostock.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def _query_baostock_macro(self, query_func: str, **kwargs) -> pd.DataFrame:
        """
        Generic method to query Baostock macro data.

        Args:
            query_func: Baostock query function name
            **kwargs: Parameters for the query function

        Returns:
            pd.DataFrame: Raw data from Baostock
        """
        start_time = time.time()

        try:
            self.logger.debug(
                f"Querying Baostock macro data: {query_func}",
                extra={
                    "context": {
                        "source": "baostock",
                        "endpoint": query_func,
                        "params": kwargs,
                        "action": "query_start",
                    }
                },
            )

            rs = getattr(self._bs_instance, query_func)(**kwargs)

            if rs.error_code != "0":
                raise ValueError(f"Baostock query failed: {rs.error_msg}")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return pd.DataFrame()

            raw_df = pd.DataFrame(data_list, columns=rs.fields)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint=query_func,
                params=kwargs,
                duration_ms=duration_ms,
                status="success",
                rows=len(raw_df),
            )

            return raw_df

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint=query_func,
                params=kwargs,
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise RuntimeError(f"Failed to fetch Baostock macro data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"baostock_deposit_rate_{start_date}_{end_date}",
    )
    def get_deposit_rate_data(self, start_date: str = "1990-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get deposit rate data from Baostock.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized deposit rate data with columns:
                - date: Date (YYYY-MM-DD)
                - deposit_rate: Deposit rate (%)
                - deposit_rate_type: Rate type (e.g., '活期存款', '定期存款三个月')
        """
        self.validate_date_range(start_date, end_date)

        try:
            raw_df = self._query_baostock_macro("query_deposit_rate_data")

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "deposit_rate", "deposit_rate_type"])

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["date"]).dt.strftime("%Y-%m-%d")
            standardized["deposit_rate"] = pd.to_numeric(raw_df["rate"], errors="coerce")
            standardized["deposit_rate_type"] = raw_df["rateType"]

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch deposit rate data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"baostock_loan_rate_{start_date}_{end_date}",
    )
    def get_loan_rate_data(self, start_date: str = "1990-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get loan rate data from Baostock.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized loan rate data with columns:
                - date: Date (YYYY-MM-DD)
                - loan_rate: Loan rate (%)
                - loan_rate_type: Rate type (e.g., '短期贷款', '中长期贷款')
        """
        self.validate_date_range(start_date, end_date)

        try:
            raw_df = self._query_baostock_macro("query_loan_rate_data")

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "loan_rate", "loan_rate_type"])

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["date"]).dt.strftime("%Y-%m-%d")
            standardized["loan_rate"] = pd.to_numeric(raw_df["rate"], errors="coerce")
            standardized["loan_rate_type"] = raw_df["rateType"]

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch loan rate data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"baostock_reserve_ratio_{start_date}_{end_date}",
    )
    def get_required_reserve_ratio_data(
        self, start_date: str = "1990-01-01", end_date: str = "2030-12-31"
    ) -> pd.DataFrame:
        """
        Get required reserve ratio data from Baostock.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized reserve ratio data with columns:
                - date: Date (YYYY-MM-DD)
                - reserve_ratio: Reserve ratio (%)
                - reserve_ratio_type: Ratio type (e.g., '大型金融机构', '中小金融机构')
        """
        self.validate_date_range(start_date, end_date)

        try:
            raw_df = self._query_baostock_macro("query_required_reserve_ratio_data")

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "reserve_ratio", "reserve_ratio_type"])

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["date"]).dt.strftime("%Y-%m-%d")
            standardized["reserve_ratio"] = pd.to_numeric(raw_df["reserveRatio"], errors="coerce")
            standardized["reserve_ratio_type"] = raw_df["reserveType"]

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch reserve ratio data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"baostock_money_supply_month_{start_date}_{end_date}",
    )
    def get_money_supply_data_month(self, start_date: str = "1990-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get monthly money supply data from Baostock.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized money supply data with columns:
                - date: Date (YYYY-MM-DD)
                - m0: M0 money supply (million yuan)
                - m1: M1 money supply (million yuan)
                - m2: M2 money supply (million yuan)
                - m0_yoy: M0 year-over-year growth (%)
                - m1_yoy: M1 year-over-year growth (%)
                - m2_yoy: M2 year-over-year growth (%)
                - m0_mom: M0 month-over-month growth (%)
                - m1_mom: M1 month-over-month growth (%)
                - m2_mom: M2 month-over-month growth (%)
        """
        self.validate_date_range(start_date, end_date)

        try:
            raw_df = self._query_baostock_macro("query_money_supply_data_month")

            if raw_df.empty:
                return self.create_empty_dataframe(
                    [
                        "date",
                        "m0",
                        "m1",
                        "m2",
                        "m0_yoy",
                        "m1_yoy",
                        "m2_yoy",
                        "m0_mom",
                        "m1_mom",
                        "m2_mom",
                    ]
                )

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["date"]).dt.strftime("%Y-%m-%d")

            numeric_cols = [
                ("m0", "m0"),
                ("m1", "m1"),
                ("m2", "m2"),
                ("m0YoY", "m0_yoy"),
                ("m1YoY", "m1_yoy"),
                ("m2YoY", "m2_yoy"),
                ("m0MonthYoY", "m0_mom"),
                ("m1MonthYoY", "m1_mom"),
                ("m2MonthYoY", "m2_mom"),
            ]

            for src_col, target_col in numeric_cols:
                if src_col in raw_df.columns:
                    standardized[target_col] = pd.to_numeric(raw_df[src_col], errors="coerce")

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch monthly money supply data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"baostock_money_supply_year_{start_date}_{end_date}",
    )
    def get_money_supply_data_year(self, start_date: str = "1990-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get yearly money supply data from Baostock.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized money supply data with columns:
                - date: Date (YYYY-MM-DD, set to January 1st of each year)
                - m0: M0 money supply (million yuan)
                - m1: M1 money supply (million yuan)
                - m2: M2 money supply (million yuan)
                - m0_yoy: M0 year-over-year growth (%)
                - m1_yoy: M1 year-over-year growth (%)
                - m2_yoy: M2 year-over-year growth (%)
        """
        self.validate_date_range(start_date, end_date)

        try:
            raw_df = self._query_baostock_macro("query_money_supply_data_year")

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "m0", "m1", "m2", "m0_yoy", "m1_yoy", "m2_yoy"])

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["year"]).dt.strftime("%Y-01-01")

            numeric_cols = [
                ("m0", "m0"),
                ("m1", "m1"),
                ("m2", "m2"),
                ("m0YoY", "m0_yoy"),
                ("m1YoY", "m1_yoy"),
                ("m2YoY", "m2_yoy"),
            ]

            for src_col, target_col in numeric_cols:
                if src_col in raw_df.columns:
                    standardized[target_col] = pd.to_numeric(raw_df[src_col], errors="coerce")

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch yearly money supply data: {e}") from e
