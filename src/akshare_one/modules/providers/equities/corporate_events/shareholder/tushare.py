"""
Tushare shareholder data provider.

This module provides shareholder data from Tushare Pro API.
"""

import pandas as pd
from typing import Optional

from .....core.cache import cache
from .base import ShareholderFactory, ShareholderProvider
from ......tushare_client import get_tushare_client


@ShareholderFactory.register("tushare")
class TushareShareholderProvider(ShareholderProvider):
    """Shareholder data provider for Tushare Pro."""

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

    def _convert_date_format(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to YYYYMMDD format for Tushare."""
        return date_str.replace("-", "")

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    @cache(
        "shareholder_cache",
        key=lambda self, columns=None, row_filter=None: f"tushare_top10_holders_{self.symbol}",
    )
    def get_top10_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """Get top 10 shareholders from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            raw_df = client.get_top10_holders(ts_code=self.ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_top10_holders_data(raw_df)
            return self.apply_data_filter(df, columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter"))
        except Exception as e:
            self.logger.error(f"Failed to get top 10 shareholders from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "shareholder_cache",
        key=lambda self, columns=None, row_filter=None: f"tushare_top10_float_shareholders_{self.symbol}",
    )
    def get_top10_float_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """Get top 10 float shareholders from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            raw_df = client.get_top10_floatholders(ts_code=self.ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_top10_float_holders_data(raw_df)
            return self.apply_data_filter(df, columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter"))
        except Exception as e:
            self.logger.error(f"Failed to get top 10 float shareholders from Tushare: {e}")
            return pd.DataFrame()

    def get_shareholder_changes(
        self,
        symbol: str | None = None,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        **kwargs,
    ) -> pd.DataFrame:
        """Get shareholder trade records (changes) from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            ts_code = self.ts_code if symbol else None
            raw_df = client.get_stk_holdertrade(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_holdertrade_data(raw_df)
            return self.apply_data_filter(df, columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter"))
        except Exception as e:
            self.logger.error(f"Failed to get shareholder changes from Tushare: {e}")
            return pd.DataFrame()

    def get_top_shareholders(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get top shareholders - defaults to top 10 shareholders."""
        return self.get_top10_shareholders(symbol, **kwargs)

    def get_institution_holdings(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get institution holdings - not directly supported by Tushare."""
        return pd.DataFrame()

    def _process_top10_holders_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize top 10 shareholders data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ann_date" in df.columns:
            df["date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d")
        elif "end_date" in df.columns:
            df["date"] = pd.to_datetime(df["end_date"], format="%Y%m%d")

        return df

    def _process_top10_float_holders_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize top 10 float shareholders data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ann_date" in df.columns:
            df["date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d")
        elif "end_date" in df.columns:
            df["date"] = pd.to_datetime(df["end_date"], format="%Y%m%d")

        return df

    def _process_holdertrade_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize shareholder trade data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ann_date" in df.columns:
            df["date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d")
        elif "end_date" in df.columns:
            df["date"] = pd.to_datetime(df["end_date"], format="%Y%m%d")

        return df
