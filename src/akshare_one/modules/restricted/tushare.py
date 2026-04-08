"""
Tushare restricted stock release data provider.

This module provides restricted stock release data from Tushare Pro API.
"""

import pandas as pd
from typing import Optional

from ..cache import cache
from .base import RestrictedReleaseFactory, RestrictedReleaseProvider
from ...tushare_client import get_tushare_client


@RestrictedReleaseFactory.register("tushare")
class TushareRestrictedReleaseProvider(RestrictedReleaseProvider):
    """Restricted stock release data provider for Tushare Pro."""

    def get_source_name(self) -> str:
        return "tushare"

    def _convert_symbol_to_ts_code(self, symbol: str) -> str:
        """Convert symbol to Tushare ts_code format."""
        if "." in symbol:
            return symbol
        elif symbol.startswith("6"):
            return f"{symbol}.SH"
        elif symbol.startswith(("0", "3")):
            return f"{symbol}.SZ"
        elif symbol.startswith(("4", "8", "9")):
            return f"{symbol}.BJ"
        else:
            return f"{symbol}.SH"

    def _convert_date_format(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to YYYYMMDD format for Tushare."""
        return date_str.replace("-", "")

    @cache(
        "restricted_cache",
        key=lambda self,
        symbol=None,
        start_date="1970-01-01",
        end_date="2030-12-31",
        columns=None,
        row_filter=None: f"tushare_restricted_{symbol}_{start_date}_{end_date}",
    )
    def get_restricted_release(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get restricted stock release data from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        ts_code = None
        if symbol:
            ts_code = self._convert_symbol_to_ts_code(symbol)

        try:
            raw_df = client.get_share_float(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    ["symbol", "release_date", "release_shares", "release_ratio", "holder_type"]
                )

            df = self._process_release_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get restricted release data from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "restricted_cache",
        key=lambda self,
        start_date="1970-01-01",
        end_date="2030-12-31",
        columns=None,
        row_filter=None: f"tushare_restricted_calendar_{start_date}_{end_date}",
    )
    def get_restricted_release_calendar(
        self,
        start_date: str,
        end_date: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get restricted stock release calendar from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            raw_df = client.get_share_float(start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(["date", "total_shares", "total_value", "stock_count"])

            df = self._process_calendar_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get restricted release calendar from Tushare: {e}")
            return pd.DataFrame()

    def _process_release_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize release data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].str.split(".").str[0]
        elif "symbol" not in df.columns:
            df["symbol"] = ""

        if "ann_date" in df.columns:
            df["release_date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d", errors="coerce").dt.strftime(
                "%Y-%m-%d"
            )
        elif "float_date" in df.columns:
            df["release_date"] = pd.to_datetime(df["float_date"], format="%Y%m%d", errors="coerce").dt.strftime(
                "%Y-%m-%d"
            )
        elif "release_date" not in df.columns:
            df["release_date"] = ""

        return df

    def _process_calendar_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize calendar data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ann_date" in df.columns:
            df["date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "float_date" in df.columns:
            df["date"] = pd.to_datetime(df["float_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "date" not in df.columns:
            df["date"] = ""

        if "date" in df.columns and df["date"].iloc[0]:
            calendar = (
                df.groupby("date")
                .agg(
                    {
                        "float_share": "sum" if "float_share" in df.columns else "count",
                        "ts_code": "count" if "ts_code" in df.columns else "count",
                    }
                )
                .reset_index()
            )

            if "float_share" in df.columns:
                calendar = calendar.rename(columns={"float_share": "total_shares"})
            else:
                calendar["total_shares"] = 0

            calendar = calendar.rename(columns={"ts_code": "stock_count"})
            calendar["total_value"] = 0

            return calendar

        return df
