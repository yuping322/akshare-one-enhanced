"""
Tushare special data provider.

This module provides special market data from Tushare Pro API.
"""

import pandas as pd
from typing import Optional

from ..cache import cache
from .base import SpecialDataFactory, SpecialDataProvider
from ...tushare_client import get_tushare_client


@SpecialDataFactory.register("tushare")
class TushareSpecialDataProvider(SpecialDataProvider):
    """Special data provider for Tushare Pro."""

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
        "special_cache",
        key=lambda self,
        symbol,
        start_date="1970-01-01",
        end_date="2030-12-31",
        columns=None,
        row_filter=None: f"tushare_chip_{symbol}_{start_date}_{end_date}",
    )
    def get_chip_distribution(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get chip distribution data from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        ts_code = self._convert_symbol_to_ts_code(symbol)
        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            raw_df = client.get_cyq_chips(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(["symbol", "date", "price", "chip_ratio", "chip_volume"])

            df = self._process_chip_data(raw_df, symbol)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get chip distribution from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "special_cache",
        key=lambda self,
        symbol=None,
        start_date="1970-01-01",
        end_date="2030-12-31",
        columns=None,
        row_filter=None: f"tushare_forecast_{symbol}_{start_date}_{end_date}",
    )
    def get_broker_forecast(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get broker profit forecast data from Tushare."""
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
            raw_df = client.get_stk_factor(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(["symbol", "date", "broker", "forecast_eps", "forecast_pe"])

            df = self._process_forecast_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get broker forecast from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "special_cache",
        key=lambda self,
        symbol=None,
        start_date="1970-01-01",
        end_date="2030-12-31",
        columns=None,
        row_filter=None: f"tushare_research_{symbol}_{start_date}_{end_date}",
    )
    def get_institutional_research(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get institutional research data from Tushare."""
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
            raw_df = client.get_stk_research(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(["symbol", "date", "institution", "research_type", "participants"])

            df = self._process_research_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get institutional research from Tushare: {e}")
            return pd.DataFrame()

    def _process_chip_data(self, raw_df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Process and standardize chip distribution data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].str.split(".").str[0]
        else:
            df["symbol"] = symbol

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "date" not in df.columns:
            df["date"] = ""

        return df

    def _process_forecast_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize broker forecast data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].str.split(".").str[0]
        elif "symbol" not in df.columns:
            df["symbol"] = ""

        if "ann_date" in df.columns:
            df["date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "date" not in df.columns:
            df["date"] = ""

        return df

    def _process_research_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize institutional research data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].str.split(".").str[0]
        elif "symbol" not in df.columns:
            df["symbol"] = ""

        if "ann_date" in df.columns:
            df["date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "research_date" in df.columns:
            df["date"] = pd.to_datetime(df["research_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "date" not in df.columns:
            df["date"] = ""

        return df
