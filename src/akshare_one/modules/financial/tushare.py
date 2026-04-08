"""
Tushare financial data provider.

This module provides financial data from Tushare Pro API.
"""

import pandas as pd
from typing import Optional

from ..cache import cache
from .base import FinancialDataFactory, FinancialDataProvider
from ...tushare_client import get_tushare_client


@FinancialDataFactory.register("tushare")
class TushareFinancialReport(FinancialDataProvider):
    """Financial data provider for Tushare Pro."""

    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(symbol, **kwargs)
        self._convert_symbol_to_ts_code()

    def get_source_name(self) -> str:
        return "tushare"

    def _convert_symbol_to_ts_code(self) -> None:
        """Convert symbol to Tushare ts_code format."""
        symbol = self.symbol
        if "." in symbol:
            self.ts_code = symbol
        elif symbol.startswith("6"):
            self.ts_code = f"{symbol}.SH"
        elif symbol.startswith(("0", "3")):
            self.ts_code = f"{symbol}.SZ"
        elif symbol.startswith(("4", "8", "9")):
            self.ts_code = f"{symbol}.BJ"
        else:
            self.ts_code = f"{symbol}.SH"

    @cache(
        "financial_cache",
        key=lambda self, columns=None, row_filter=None: f"tushare_balance_{self.symbol}_{columns}_{row_filter}",
    )
    def get_balance_sheet(
        self, columns: Optional[list] = None, row_filter: Optional[dict] = None, **kwargs
    ) -> pd.DataFrame:
        """Get balance sheet data from Tushare."""
        client = get_tushare_client()

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        try:
            raw_df = client.get_balancesheet(
                ts_code=self.ts_code,
                start_date=start_date,
                end_date=end_date,
                report_type=kwargs.get("report_type", "1"),
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_balance_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get balance sheet from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "financial_cache",
        key=lambda self, columns=None, row_filter=None: f"tushare_income_{self.symbol}_{columns}_{row_filter}",
    )
    def get_income_statement(
        self, columns: Optional[list] = None, row_filter: Optional[dict] = None, **kwargs
    ) -> pd.DataFrame:
        """Get income statement data from Tushare."""
        client = get_tushare_client()

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        try:
            raw_df = client.get_income(
                ts_code=self.ts_code,
                start_date=start_date,
                end_date=end_date,
                report_type=kwargs.get("report_type", "1"),
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_income_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get income statement from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "financial_cache",
        key=lambda self, columns=None, row_filter=None: f"tushare_cashflow_{self.symbol}_{columns}_{row_filter}",
    )
    def get_cash_flow(
        self, columns: Optional[list] = None, row_filter: Optional[dict] = None, **kwargs
    ) -> pd.DataFrame:
        """Get cash flow statement data from Tushare."""
        client = get_tushare_client()

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        try:
            raw_df = client.get_cashflow(
                ts_code=self.ts_code,
                start_date=start_date,
                end_date=end_date,
                report_type=kwargs.get("report_type", "1"),
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_cashflow_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get cash flow from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "financial_cache",
        key=lambda self, columns=None, row_filter=None: f"tushare_metrics_{self.symbol}_{columns}_{row_filter}",
    )
    def get_financial_metrics(
        self, columns: Optional[list] = None, row_filter: Optional[dict] = None, **kwargs
    ) -> pd.DataFrame:
        """Get financial indicators from Tushare."""
        client = get_tushare_client()

        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        try:
            raw_df = client.get_fina_indicator(ts_code=self.ts_code, start_date=start_date, end_date=end_date)

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_metrics_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get financial metrics from Tushare: {e}")
            return pd.DataFrame()

    def _process_balance_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize balance sheet data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "end_date" in df.columns:
            df["report_date"] = pd.to_datetime(df["end_date"], format="%Y%m%d")
            df["date"] = df["report_date"]

        return df

    def _process_income_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize income statement data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "end_date" in df.columns:
            df["report_date"] = pd.to_datetime(df["end_date"], format="%Y%m%d")
            df["date"] = df["report_date"]

        return df

    def _process_cashflow_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize cash flow data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "end_date" in df.columns:
            df["report_date"] = pd.to_datetime(df["end_date"], format="%Y%m%d")
            df["date"] = df["report_date"]

        return df

    def _process_metrics_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize financial metrics data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "end_date" in df.columns:
            df["report_date"] = pd.to_datetime(df["end_date"], format="%Y%m%d")
            df["date"] = df["report_date"]

        return df
