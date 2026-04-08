"""
Tushare disclosure data provider.

This module provides disclosure data from Tushare Pro API.
"""


import pandas as pd

from ...tushare_client import get_tushare_client
from ..cache import cache
from .base import DisclosureFactory, DisclosureProvider


@DisclosureFactory.register("tushare")
class TushareDisclosureProvider(DisclosureProvider):
    """Disclosure data provider for Tushare Pro."""

    def __init__(self, symbol: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol
        if symbol:
            self._convert_symbol_to_ts_code()
        else:
            self.ts_code = None

    def get_source_name(self) -> str:
        return "tushare"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

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

    @cache(
        "dividend_data_cache",
        key=lambda self,
        start_date="1970-01-01",
        end_date="2030-12-31": f"tushare_dividend_{self.symbol}_{start_date}_{end_date}",
    )
    def get_dividend_data(
        self, symbol: str | None = None, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """Get dividend data from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        ts_code = self.ts_code
        if symbol and symbol != self.symbol:
            self.symbol = symbol
            self._convert_symbol_to_ts_code()
            ts_code = self.ts_code

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            raw_df = client.get_dividend(
                ts_code=ts_code,
                start_date=start_date_ts,
                end_date=end_date_ts,
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_dividend_data(raw_df)
            return self.ensure_json_compatible(df)
        except Exception as e:
            self.logger.error(f"Failed to get dividend data from Tushare: {e}")
            return pd.DataFrame()

    def _process_dividend_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize dividend data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ann_date" in df.columns:
            df["announcement_date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d")

        if "end_date" in df.columns:
            df["fiscal_year"] = df["end_date"].astype(str).str[:4]

        df = df.sort_values("announcement_date", ascending=False).reset_index(drop=True)

        return df

    @cache(
        "info_cache",
        key=lambda self,
        start_date="1970-01-01",
        end_date="2030-12-31": f"tushare_forecast_{self.symbol}_{start_date}_{end_date}",
    )
    def get_forecast_data(
        self, symbol: str | None = None, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """Get performance forecast data from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        ts_code = self.ts_code
        if symbol and symbol != self.symbol:
            self.symbol = symbol
            self._convert_symbol_to_ts_code()
            ts_code = self.ts_code

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            raw_df = client.get_forecast(
                ts_code=ts_code,
                start_date=start_date_ts,
                end_date=end_date_ts,
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_forecast_data(raw_df)
            return self.ensure_json_compatible(df)
        except Exception as e:
            self.logger.error(f"Failed to get forecast data from Tushare: {e}")
            return pd.DataFrame()

    def _process_forecast_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize forecast data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ann_date" in df.columns:
            df["announcement_date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d")

        if "end_date" in df.columns:
            df["report_period"] = df["end_date"].astype(str)

        df = df.sort_values("announcement_date", ascending=False).reset_index(drop=True)

        return df

    @cache(
        "info_cache",
        key=lambda self,
        start_date="1970-01-01",
        end_date="2030-12-31": f"tushare_express_{self.symbol}_{start_date}_{end_date}",
    )
    def get_express_data(
        self, symbol: str | None = None, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """Get performance express (quick report) data from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        ts_code = self.ts_code
        if symbol and symbol != self.symbol:
            self.symbol = symbol
            self._convert_symbol_to_ts_code()
            ts_code = self.ts_code

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            raw_df = client.get_express(
                ts_code=ts_code,
                start_date=start_date_ts,
                end_date=end_date_ts,
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_express_data(raw_df)
            return self.ensure_json_compatible(df)
        except Exception as e:
            self.logger.error(f"Failed to get express data from Tushare: {e}")
            return pd.DataFrame()

    def _process_express_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize express data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ann_date" in df.columns:
            df["announcement_date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d")

        if "end_date" in df.columns:
            df["report_period"] = df["end_date"].astype(str)

        df = df.sort_values("announcement_date", ascending=False).reset_index(drop=True)

        return df

    def get_disclosure_news(
        self, symbol: str | None, start_date: str, end_date: str, category: str, **kwargs
    ) -> pd.DataFrame:
        """Get disclosure news - not implemented for Tushare."""
        return pd.DataFrame()

    def get_repurchase_data(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """Get repurchase data - not implemented for Tushare."""
        return pd.DataFrame()

    def get_st_delist_data(self, symbol: str | None, **kwargs) -> pd.DataFrame:
        """Get ST/delist data - not implemented for Tushare."""
        return pd.DataFrame()
