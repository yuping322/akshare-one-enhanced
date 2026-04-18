"""
Tushare macro economic data provider.

This module implements the macro data provider using Tushare Pro API
for Chinese macro economic data including Shibor, LPR, GDP, CPI, PPI, and PMI.
"""

import pandas as pd

from ....logging_config import get_logger
from ....tushare_client import get_tushare_client
from ...core.cache import cache
from .base import MacroFactory, MacroProvider


@MacroFactory.register("tushare")
class TushareMacroProvider(MacroProvider):
    """
    Macro economic data provider using Tushare Pro API.

    This provider wraps Tushare functions to fetch macro data including:
    - Shibor rates
    - LPR rates
    - GDP monthly data
    - CPI data
    - PPI data
    - PMI data
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)
        self.client = get_tushare_client()

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "tushare"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Tushare.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def _convert_date_format(self, date_str: str) -> str:
        """
        Convert YYYY-MM-DD to YYYYMMDD format for Tushare API.

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            Date in YYYYMMDD format
        """
        if date_str and "-" in date_str:
            return date_str.replace("-", "")
        return date_str

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"tushare_shibor_{start_date}_{end_date}",
    )
    def get_shibor_rate(self, start_date: str = "1990-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get Shibor (Shanghai Interbank Offered Rate) data from Tushare.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized Shibor rate data with columns:
                - date: Date (YYYY-MM-DD)
                - on_rate: Overnight rate (%)
                - 1w_rate: 1-week rate (%)
                - 2w_rate: 2-week rate (%)
                - 1m_rate: 1-month rate (%)
                - 3m_rate: 3-month rate (%)
                - 6m_rate: 6-month rate (%)
                - 9m_rate: 9-month rate (%)
                - 1y_rate: 1-year rate (%)
        """
        self.validate_date_range(start_date, end_date)

        try:
            tushare_start = self._convert_date_format(start_date)
            tushare_end = self._convert_date_format(end_date)

            raw_df = self.client.get_shibor(start_date=tushare_start, end_date=tushare_end)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    ["date", "on_rate", "1w_rate", "2w_rate", "1m_rate", "3m_rate", "6m_rate", "9m_rate", "1y_rate"]
                )

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["date"]).dt.strftime("%Y-%m-%d")

            rate_cols = [
                ("on", "on_rate"),
                ("1w", "1w_rate"),
                ("2w", "2w_rate"),
                ("1m", "1m_rate"),
                ("3m", "3m_rate"),
                ("6m", "6m_rate"),
                ("9m", "9m_rate"),
                ("1y", "1y_rate"),
            ]

            for src_col, target_col in rate_cols:
                if src_col in raw_df.columns:
                    standardized[target_col] = pd.to_numeric(raw_df[src_col], errors="coerce")

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch Shibor rate data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"tushare_lpr_{start_date}_{end_date}",
    )
    def get_lpr_rate(self, start_date: str = "1990-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get LPR (Loan Prime Rate) data from Tushare.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized LPR rate data with columns:
                - date: Date (YYYY-MM-DD)
                - lpr_1y: 1-year LPR (%)
                - lpr_5y: 5-year LPR (%)
        """
        self.validate_date_range(start_date, end_date)

        try:
            tushare_start = self._convert_date_format(start_date)
            tushare_end = self._convert_date_format(end_date)

            raw_df = self.client.get_lpr(start_date=tushare_start, end_date=tushare_end)

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "lpr_1y", "lpr_5y"])

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["date"]).dt.strftime("%Y-%m-%d")

            rate_cols = [
                ("lpr_1y", "lpr_1y"),
                ("lpr_5y", "lpr_5y"),
            ]

            for src_col, target_col in rate_cols:
                if src_col in raw_df.columns:
                    standardized[target_col] = pd.to_numeric(raw_df[src_col], errors="coerce")

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch LPR rate data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"tushare_gdp_{start_date}_{end_date}",
    )
    def get_gdp(self, start_date: str = "1990-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get GDP monthly data from Tushare.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized GDP data with columns:
                - date: Date (YYYY-MM-DD)
                - gdp: GDP value
                - gdp_yoy: GDP year-over-year growth (%)
        """
        self.validate_date_range(start_date, end_date)

        try:
            tushare_start = self._convert_date_format(start_date)
            tushare_end = self._convert_date_format(end_date)

            raw_df = self.client.get_gdp_monthly(start_date=tushare_start, end_date=tushare_end)

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "gdp", "gdp_yoy"])

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["month"]).dt.strftime("%Y-%m-01")

            numeric_cols = [
                ("gdp", "gdp"),
                ("gdp_yoy", "gdp_yoy"),
            ]

            for src_col, target_col in numeric_cols:
                if src_col in raw_df.columns:
                    standardized[target_col] = pd.to_numeric(raw_df[src_col], errors="coerce")

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch GDP data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"tushare_cpi_{start_date}_{end_date}",
    )
    def get_cpi_data(self, start_date: str = "1990-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get CPI (Consumer Price Index) data from Tushare.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized CPI data with columns:
                - date: Date (YYYY-MM-DD)
                - cpi: CPI index value
                - cpi_yoy: CPI year-over-year growth (%)
                - cpi_mom: CPI month-over-month growth (%)
        """
        self.validate_date_range(start_date, end_date)

        try:
            tushare_start = self._convert_date_format(start_date)
            tushare_end = self._convert_date_format(end_date)

            raw_df = self.client.get_cpi(start_date=tushare_start, end_date=tushare_end)

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "cpi", "cpi_yoy", "cpi_mom"])

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["month"]).dt.strftime("%Y-%m-01")

            numeric_cols = [
                ("cpi", "cpi"),
                ("cpi_yoy", "cpi_yoy"),
                ("cpi_mom", "cpi_mom"),
            ]

            for src_col, target_col in numeric_cols:
                if src_col in raw_df.columns:
                    standardized[target_col] = pd.to_numeric(raw_df[src_col], errors="coerce")

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch CPI data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date: f"tushare_ppi_{start_date}_{end_date}",
    )
    def get_ppi_data(self, start_date: str = "1990-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get PPI (Producer Price Index) data from Tushare.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Standardized PPI data with columns:
                - date: Date (YYYY-MM-DD)
                - ppi: PPI index value
                - ppi_yoy: PPI year-over-year growth (%)
                - ppi_mom: PPI month-over-month growth (%)
        """
        self.validate_date_range(start_date, end_date)

        try:
            tushare_start = self._convert_date_format(start_date)
            tushare_end = self._convert_date_format(end_date)

            raw_df = self.client.get_ppi(start_date=tushare_start, end_date=tushare_end)

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "ppi", "ppi_yoy", "ppi_mom"])

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["month"]).dt.strftime("%Y-%m-01")

            numeric_cols = [
                ("ppi", "ppi"),
                ("ppi_yoy", "ppi_yoy"),
                ("ppi_mom", "ppi_mom"),
            ]

            for src_col, target_col in numeric_cols:
                if src_col in raw_df.columns:
                    standardized[target_col] = pd.to_numeric(raw_df[src_col], errors="coerce")

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch PPI data: {e}") from e

    @cache(
        "macro_cache",
        key=lambda self, start_date, end_date, pmi_type: f"tushare_pmi_{start_date}_{end_date}_{pmi_type}",
    )
    def get_pmi_index(
        self, start_date: str = "1990-01-01", end_date: str = "2030-12-31", pmi_type: str = "manufacturing"
    ) -> pd.DataFrame:
        """
        Get PMI (Purchasing Managers' Index) data from Tushare.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            pmi_type: PMI type ('manufacturing' or 'non_manufacturing')

        Returns:
            pd.DataFrame: Standardized PMI data with columns:
                - date: Date (YYYY-MM-DD)
                - pmi: PMI index value
        """
        self.validate_date_range(start_date, end_date)

        try:
            tushare_start = self._convert_date_format(start_date)
            tushare_end = self._convert_date_format(end_date)

            raw_df = self.client.get_pmi(start_date=tushare_start, end_date=tushare_end)

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "pmi"])

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["month"]).dt.strftime("%Y-%m-01")

            pmi_col_map = {
                "manufacturing": "pmi_m",
                "non_manufacturing": "pmi_nm",
            }

            src_col = pmi_col_map.get(pmi_type, "pmi_m")
            if src_col in raw_df.columns:
                standardized["pmi"] = pd.to_numeric(raw_df[src_col], errors="coerce")

            mask = (standardized["date"] >= start_date) & (standardized["date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch PMI data: {e}") from e
