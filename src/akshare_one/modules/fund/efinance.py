"""
Efinance fund data provider.

This module implements the fund data provider using efinance as the data source.
"""

import time
from typing import Literal

import efinance as ef
import pandas as pd

from .base import FIELD_MAPPING, FundFactory, FundProvider


@FundFactory.register("efinance")
class EfinanceFundProvider(FundProvider):
    """
    Fund data provider using efinance as the data source.
    """

    def __init__(
        self,
        fund_code: str = "",
        **kwargs,
    ) -> None:
        super().__init__(fund_code=fund_code, **kwargs)

    def get_source_name(self) -> str:
        return "efinance"

    def _map_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map Chinese field names to English field names.

        Args:
            df: DataFrame with Chinese field names

        Returns:
            DataFrame with English field names
        """
        if df.empty:
            return df

        rename_dict = {}
        for chinese_name, english_name in FIELD_MAPPING.items():
            if chinese_name in df.columns:
                rename_dict[chinese_name] = english_name

        if rename_dict:
            df = df.rename(columns=rename_dict)

        return df

    def get_quote_history(
        self,
        fund_code: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund historical net value data from efinance.

        Args:
            fund_code: Fund code (e.g., '000001')
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund historical net value data
        """
        code = fund_code or self.fund_code
        if not code:
            return pd.DataFrame()

        start_time = time.time()
        try:
            raw_df = ef.fund.get_quote_history(code)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_quote_history completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_quote_history",
                        "fund_code": code,
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(raw_df) if raw_df is not None and not raw_df.empty else 0,
                    }
                },
            )

            if raw_df is None or raw_df.empty:
                return pd.DataFrame(columns=["fund_code", "date", "net_value", "accumulated_net_value", "pct_change"])

            df = self._map_fields(raw_df)
            df = self.ensure_json_compatible(df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(
                f"get_quote_history failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_quote_history",
                        "fund_code": code,
                        "error": str(e),
                    }
                },
            )
            return pd.DataFrame(columns=["fund_code", "date", "net_value", "accumulated_net_value", "pct_change"])

    def get_base_info(
        self,
        fund_codes: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund basic information from efinance.

        Args:
            fund_codes: Fund code or list of codes
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund basic information
        """
        codes = fund_codes
        if codes is None:
            codes = self.fund_code if self.fund_code else []

        if isinstance(codes, str):
            codes = [codes]

        if not codes:
            return pd.DataFrame()

        start_time = time.time()
        try:
            raw_df = ef.fund.get_base_info(codes)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_base_info completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_base_info",
                        "fund_codes": codes,
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(raw_df) if raw_df is not None and not raw_df.empty else 0,
                    }
                },
            )

            if raw_df is None or raw_df.empty:
                return pd.DataFrame(
                    columns=["fund_code", "fund_name", "fund_type", "fund_manager", "fund_scale", "establish_date"]
                )

            df = self._map_fields(raw_df)
            df = self.ensure_json_compatible(df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(
                f"get_base_info failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_base_info",
                        "fund_codes": codes,
                        "error": str(e),
                    }
                },
            )
            return pd.DataFrame(
                columns=["fund_code", "fund_name", "fund_type", "fund_manager", "fund_scale", "establish_date"]
            )

    def get_invest_position(
        self,
        fund_code: str | None = None,
        dates: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund investment positions/holdings from efinance.

        Args:
            fund_code: Fund code
            dates: Date or list of dates for holdings
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund holdings data
        """
        code = fund_code or self.fund_code
        if not code:
            return pd.DataFrame()

        if isinstance(dates, str):
            dates = [dates]

        start_time = time.time()
        try:
            raw_df = ef.fund.get_invest_position(code, dates)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_invest_position completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_invest_position",
                        "fund_code": code,
                        "dates": dates,
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(raw_df) if raw_df is not None and not raw_df.empty else 0,
                    }
                },
            )

            if raw_df is None or raw_df.empty:
                return pd.DataFrame(columns=["fund_code", "date", "symbol", "name", "holding_ratio", "holding_value"])

            df = self._map_fields(raw_df)
            df = self.ensure_json_compatible(df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(
                f"get_invest_position failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_invest_position",
                        "fund_code": code,
                        "dates": dates,
                        "error": str(e),
                    }
                },
            )
            return pd.DataFrame(columns=["fund_code", "date", "symbol", "name", "holding_ratio", "holding_value"])

    def get_industry_distribution(
        self,
        fund_code: str | None = None,
        dates: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund industry distribution/allocation from efinance.

        Args:
            fund_code: Fund code
            dates: Date or list of dates
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund industry distribution data
        """
        code = fund_code or self.fund_code
        if not code:
            return pd.DataFrame()

        if isinstance(dates, str):
            dates = [dates]

        start_time = time.time()
        try:
            raw_df = ef.fund.get_industry_distribution(code, dates)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_industry_distribution completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_industry_distribution",
                        "fund_code": code,
                        "dates": dates,
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(raw_df) if raw_df is not None and not raw_df.empty else 0,
                    }
                },
            )

            if raw_df is None or raw_df.empty:
                return pd.DataFrame(columns=["fund_code", "date", "industry", "holding_ratio"])

            df = self._map_fields(raw_df)
            df = self.ensure_json_compatible(df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(
                f"get_industry_distribution failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_industry_distribution",
                        "fund_code": code,
                        "dates": dates,
                        "error": str(e),
                    }
                },
            )
            return pd.DataFrame(columns=["fund_code", "date", "industry", "holding_ratio"])

    def get_types_percentage(
        self,
        fund_code: str | None = None,
        dates: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund asset allocation/types percentage from efinance.

        Args:
            fund_code: Fund code
            dates: Date or list of dates
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund asset allocation data
        """
        code = fund_code or self.fund_code
        if not code:
            return pd.DataFrame()

        if isinstance(dates, str):
            dates = [dates]

        start_time = time.time()
        try:
            raw_df = ef.fund.get_types_percentage(code, dates)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_types_percentage completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_types_percentage",
                        "fund_code": code,
                        "dates": dates,
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(raw_df) if raw_df is not None and not raw_df.empty else 0,
                    }
                },
            )

            if raw_df is None or raw_df.empty:
                return pd.DataFrame(columns=["fund_code", "date", "asset_type", "asset_ratio"])

            df = self._map_fields(raw_df)
            df = self.ensure_json_compatible(df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(
                f"get_types_percentage failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_types_percentage",
                        "fund_code": code,
                        "dates": dates,
                        "error": str(e),
                    }
                },
            )
            return pd.DataFrame(columns=["fund_code", "date", "asset_type", "asset_ratio"])

    def get_fund_codes(
        self,
        ft: Literal["open", "closed", "etf", "index", "all"] = "all",
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get list of fund codes from efinance.

        Args:
            ft: Fund type filter
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund codes list
        """
        start_time = time.time()
        try:
            raw_df = ef.fund.get_fund_codes(ft)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_fund_codes completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_fund_codes",
                        "ft": ft,
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(raw_df) if raw_df is not None and not raw_df.empty else 0,
                    }
                },
            )

            if raw_df is None or raw_df.empty:
                return pd.DataFrame(columns=["fund_code", "fund_name", "fund_type"])

            df = self._map_fields(raw_df)
            df = self.ensure_json_compatible(df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(
                f"get_fund_codes failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_fund_codes",
                        "ft": ft,
                        "error": str(e),
                    }
                },
            )
            return pd.DataFrame(columns=["fund_code", "fund_name", "fund_type"])

    def get_fund_manager(
        self,
        ft: Literal["open", "closed", "etf", "index", "all"] = "all",
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund manager information from efinance.

        Args:
            ft: Fund type filter
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with fund manager data
        """
        start_time = time.time()
        try:
            raw_df = ef.fund.get_fund_manager(ft)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_fund_manager completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_fund_manager",
                        "ft": ft,
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(raw_df) if raw_df is not None and not raw_df.empty else 0,
                    }
                },
            )

            if raw_df is None or raw_df.empty:
                return pd.DataFrame(columns=["fund_code", "fund_name", "fund_manager"])

            df = self._map_fields(raw_df)
            df = self.ensure_json_compatible(df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(
                f"get_fund_manager failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_fund_manager",
                        "ft": ft,
                        "error": str(e),
                    }
                },
            )
            return pd.DataFrame(columns=["fund_code", "fund_name", "fund_manager"])

    def get_realtime_increase_rate(
        self,
        fund_codes: str | list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund realtime increase rate (change percentage) from efinance.

        Args:
            fund_codes: Fund code or list of codes
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with realtime change data
        """
        codes = fund_codes
        if codes is None:
            codes = self.fund_code if self.fund_code else []

        if isinstance(codes, str):
            codes = [codes]

        if not codes:
            return pd.DataFrame()

        start_time = time.time()
        try:
            raw_df = ef.fund.get_realtime_increase_rate(codes)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_realtime_increase_rate completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_realtime_increase_rate",
                        "fund_codes": codes,
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(raw_df) if raw_df is not None and not raw_df.empty else 0,
                    }
                },
            )

            if raw_df is None or raw_df.empty:
                return pd.DataFrame(columns=["fund_code", "fund_name", "realtime_pct_change"])

            df = self._map_fields(raw_df)
            df = self.ensure_json_compatible(df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(
                f"get_realtime_increase_rate failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_realtime_increase_rate",
                        "fund_codes": codes,
                        "error": str(e),
                    }
                },
            )
            return pd.DataFrame(columns=["fund_code", "fund_name", "realtime_pct_change"])

    def get_quote_history_multi(
        self,
        fund_codes: list[str],
        pz: int = 100,
        **kwargs,
    ) -> dict[str, pd.DataFrame]:
        """
        Get fund historical net value data for multiple funds from efinance.

        Args:
            fund_codes: List of fund codes
            pz: Number of records per fund

        Returns:
            Dict mapping fund codes to DataFrames with historical data
        """
        if not fund_codes:
            return {}

        start_time = time.time()
        try:
            raw_dict = ef.fund.get_quote_history_multi(fund_codes, pz)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_quote_history_multi completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_quote_history_multi",
                        "fund_codes": fund_codes,
                        "pz": pz,
                        "duration_ms": round(duration_ms, 2),
                        "fund_count": len(raw_dict) if raw_dict else 0,
                    }
                },
            )

            if raw_dict is None:
                return {}

            result = {}
            for code, df in raw_dict.items():
                if df is not None and not df.empty:
                    df = self._map_fields(df)
                    df = self.ensure_json_compatible(df)
                    result[code] = df
                else:
                    result[code] = pd.DataFrame(
                        columns=["fund_code", "date", "net_value", "accumulated_net_value", "pct_change"]
                    )

            return result

        except Exception as e:
            self.logger.error(
                f"get_quote_history_multi failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_quote_history_multi",
                        "fund_codes": fund_codes,
                        "error": str(e),
                    }
                },
            )
            return {}

    def get_public_dates(
        self,
        fund_code: str | None = None,
        **kwargs,
    ) -> list[str]:
        """
        Get list of public announcement dates for a fund from efinance.

        Args:
            fund_code: Fund code

        Returns:
            List of date strings
        """
        code = fund_code or self.fund_code
        if not code:
            return []

        start_time = time.time()
        try:
            dates = ef.fund.get_public_dates(code)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_public_dates completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_public_dates",
                        "fund_code": code,
                        "duration_ms": round(duration_ms, 2),
                        "date_count": len(dates) if dates else 0,
                    }
                },
            )

            return dates if dates else []

        except Exception as e:
            self.logger.error(
                f"get_public_dates failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_public_dates",
                        "fund_code": code,
                        "error": str(e),
                    }
                },
            )
            return []

    def get_period_change(
        self,
        fund_code: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund performance in different periods from efinance.

        Args:
            fund_code: Fund code
            columns: Columns to keep
            row_filter: Row filter configuration

        Returns:
            DataFrame with period performance data
        """
        code = fund_code or self.fund_code
        if not code:
            return pd.DataFrame()

        start_time = time.time()
        try:
            raw_df = ef.fund.get_period_change(code)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_period_change completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_period_change",
                        "fund_code": code,
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(raw_df) if raw_df is not None and not raw_df.empty else 0,
                    }
                },
            )

            if raw_df is None or raw_df.empty:
                return pd.DataFrame(columns=["fund_code", "week1", "month1", "month3", "month6", "year1", "year3"])

            df = self._map_fields(raw_df)
            df = self.ensure_json_compatible(df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(
                f"get_period_change failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_period_change",
                        "fund_code": code,
                        "error": str(e),
                    }
                },
            )
            return pd.DataFrame(columns=["fund_code", "week1", "month1", "month3", "month6", "year1", "year3"])

    def get_pdf_reports(
        self,
        fund_code: str | None = None,
        max_count: int = 12,
        save_dir: str = "pdf",
        **kwargs,
    ) -> list[str] | None:
        """
        Download PDF reports for a fund from efinance.

        Args:
            fund_code: Fund code
            max_count: Maximum number of PDF reports to download
            save_dir: Directory to save PDF reports

        Returns:
            List of file paths or None on error
        """
        code = fund_code or self.fund_code
        if not code:
            return None

        start_time = time.time()
        try:
            result = ef.fund.get_pdf_reports(code, max_count, save_dir)

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"get_pdf_reports completed",
                extra={
                    "context": {
                        "log_type": "api_request",
                        "source": "efinance",
                        "endpoint": "get_pdf_reports",
                        "fund_code": code,
                        "max_count": max_count,
                        "save_dir": save_dir,
                        "duration_ms": round(duration_ms, 2),
                    }
                },
            )

            return result

        except Exception as e:
            self.logger.error(
                f"get_pdf_reports failed",
                extra={
                    "context": {
                        "log_type": "api_error",
                        "source": "efinance",
                        "endpoint": "get_pdf_reports",
                        "fund_code": code,
                        "error": str(e),
                    }
                },
            )
            return None
