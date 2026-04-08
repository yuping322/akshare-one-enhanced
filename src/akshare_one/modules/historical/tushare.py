"""
Tushare historical data provider.

This module provides historical market data from Tushare Pro API.
"""

import pandas as pd
from typing import Optional

from ..cache import cache
from .base import HistoricalDataFactory, HistoricalDataProvider
from ...tushare_client import get_tushare_client


@HistoricalDataFactory.register("tushare")
class TushareHistoricalData(HistoricalDataProvider):
    """Historical data provider for Tushare Pro."""

    def __init__(
        self,
        symbol: str,
        interval: str = "day",
        interval_multiplier: int = 1,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        adjust: str = "none",
        **kwargs,
    ) -> None:
        super().__init__(
            symbol=symbol,
            interval=interval,
            interval_multiplier=interval_multiplier,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            **kwargs,
        )
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

    @cache(
        "hist_data_cache",
        key=lambda self,
        columns=None,
        row_filter=None: f"tushare_hist_{self.symbol}_{self.interval}_{self.start_date}_{self.end_date}_{self.adjust}",
    )
    def get_hist_data(
        self, columns: Optional[list] = None, row_filter: Optional[dict] = None, **kwargs
    ) -> pd.DataFrame:
        """Get historical price data from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(self.start_date)
        end_date_ts = self._convert_date_format(self.end_date)

        try:
            if self.interval == "day":
                raw_df = client.get_daily(ts_code=self.ts_code, start_date=start_date_ts, end_date=end_date_ts)
            elif self.interval == "week":
                raw_df = client.query("weekly", ts_code=self.ts_code, start_date=start_date_ts, end_date=end_date_ts)
            elif self.interval == "month":
                raw_df = client.query("monthly", ts_code=self.ts_code, start_date=start_date_ts, end_date=end_date_ts)
            else:
                self.logger.warning(f"Tushare does not support interval '{self.interval}', falling back to daily")
                raw_df = client.get_daily(ts_code=self.ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_historical_data(raw_df)

            if self.adjust in ["qfq", "hfq"]:
                df = self._apply_adjustment(df)

            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get historical data from Tushare: {e}")
            return pd.DataFrame()

    def _process_historical_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize historical data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")

        df = df.sort_values("date", ascending=True).reset_index(drop=True)

        return df

    def _apply_adjustment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply price adjustment (qfq/hfq)."""
        if df.empty:
            return df

        client = get_tushare_client()

        try:
            adj_df = client.query("adj_factor", ts_code=self.ts_code)

            if adj_df.empty:
                return df

            adj_df["adj_date"] = pd.to_datetime(adj_df["adj_date"], format="%Y%m%d")

            df = df.merge(adj_df, left_on="date", right_on="adj_date", how="left")

            if "adj_factor" in df.columns:
                adj_factor = df["adj_factor"].fillna(1.0)

                for col in ["open", "high", "low", "close"]:
                    if col in df.columns:
                        df[col] = df[col] * adj_factor

            return df.drop(columns=["adj_date", "adj_factor"], errors="ignore")
        except Exception as e:
            self.logger.warning(f"Failed to apply adjustment: {e}")
            return df
