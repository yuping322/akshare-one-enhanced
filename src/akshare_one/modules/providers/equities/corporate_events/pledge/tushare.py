"""
Tushare pledge data provider.

This module provides equity pledge data from Tushare Pro API.
"""

import pandas as pd
from typing import Optional

from .....core.cache import cache
from .base import EquityPledgeFactory, EquityPledgeProvider
from ......tushare_client import get_tushare_client


@EquityPledgeFactory.register("tushare")
class TushareEquityPledgeProvider(EquityPledgeProvider):
    """Equity pledge data provider for Tushare Pro."""

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
        "pledge_cache",
        key=lambda self,
        symbol=None,
        start_date="1970-01-01",
        end_date="2030-12-31",
        columns=None,
        row_filter=None: f"tushare_pledge_{symbol}_{start_date}_{end_date}",
    )
    def get_equity_pledge(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get equity pledge data from Tushare."""
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
            raw_df = client.get_pledge_detail(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    ["symbol", "shareholder_name", "pledge_shares", "pledge_ratio", "pledgee", "pledge_date"]
                )

            df = self._process_pledge_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get pledge data from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "pledge_cache",
        key=lambda self, date=None, top_n=100, columns=None, row_filter=None: f"tushare_pledge_rank_{date}_{top_n}",
    )
    def get_equity_pledge_ratio_rank(
        self, date: str, top_n: int, columns: Optional[list] = None, row_filter: Optional[dict] = None, **kwargs
    ) -> pd.DataFrame:
        """Get equity pledge ratio ranking from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        date_ts = self._convert_date_format(date)

        try:
            raw_df = client.get_share_pledge(end_date=date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(["rank", "symbol", "name", "pledge_ratio", "pledge_value"])

            df = self._process_rank_data(raw_df, top_n)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get pledge ranking from Tushare: {e}")
            return pd.DataFrame()

    def _process_pledge_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize pledge data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].str.split(".").str[0]
        elif "symbol" not in df.columns:
            df["symbol"] = ""

        if "ann_date" in df.columns:
            df["pledge_date"] = pd.to_datetime(df["ann_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "end_date" in df.columns:
            df["pledge_date"] = pd.to_datetime(df["end_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "pledge_date" not in df.columns:
            df["pledge_date"] = ""

        return df

    def _process_rank_data(self, raw_df: pd.DataFrame, top_n: int) -> pd.DataFrame:
        """Process and standardize ranking data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].str.split(".").str[0]
        elif "symbol" not in df.columns:
            df["symbol"] = ""

        if "pledge_ratio" in df.columns:
            df = df.sort_values("pledge_ratio", ascending=False).reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)

        df.insert(0, "rank", range(1, len(df) + 1))

        result = df.head(top_n)

        return result
