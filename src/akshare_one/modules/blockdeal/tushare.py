"""
Tushare block deal data provider.

This module provides block deal data from Tushare Pro API.
"""

import time

import pandas as pd
from typing import Optional

from ...metrics import get_stats_collector
from ...tushare_client import get_tushare_client
from ..cache import cache
from .base import BlockDealFactory, BlockDealProvider


@BlockDealFactory.register("tushare")
class TushareBlockDealProvider(BlockDealProvider):
    """Block deal data provider for Tushare Pro."""

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
        "blockdeal_cache",
        key=lambda self,
        symbol=None,
        start_date="1970-01-01",
        end_date="2030-12-31",
        columns=None,
        row_filter=None: f"tushare_blockdeal_{symbol}_{start_date}_{end_date}",
    )
    def get_block_deal(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get block deal transaction details from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        ts_code = None
        if symbol:
            ts_code = self._convert_symbol_to_ts_code(symbol)

        start_time = time.time()
        try:
            raw_df = client.get_block_trade(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)

            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, True)
            except (ImportError, AttributeError):
                pass

            if raw_df.empty:
                return self.create_empty_dataframe(["symbol", "date", "price", "volume", "amount", "buyer", "seller"])

            df = self._process_block_deal_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, False)
            except (ImportError, AttributeError):
                pass
            self.logger.error(f"Failed to get block deal data from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "blockdeal_cache",
        key=lambda self,
        start_date="1970-01-01",
        end_date="2030-12-31",
        group_by="date",
        columns=None,
        row_filter=None: f"tushare_blockdeal_summary_{start_date}_{end_date}_{group_by}",
    )
    def get_block_deal_summary(
        self,
        start_date: str,
        end_date: str,
        group_by: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get block deal summary statistics from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        start_time = time.time()
        try:
            raw_df = client.get_block_trade(start_date=start_date_ts, end_date=end_date_ts)

            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, True)
            except (ImportError, AttributeError):
                pass

            if raw_df.empty:
                return self.create_empty_dataframe(["group_key", "total_volume", "total_amount", "deal_count"])

            df = self._process_summary_data(raw_df, group_by)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, False)
            except (ImportError, AttributeError):
                pass
            self.logger.error(f"Failed to get block deal summary from Tushare: {e}")
            return pd.DataFrame()

    def _process_block_deal_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize block deal data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].str.split(".").str[0]
        elif "symbol" not in df.columns:
            df["symbol"] = ""

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")
        elif "date" not in df.columns:
            df["date"] = ""

        return df

    def _process_summary_data(self, raw_df: pd.DataFrame, group_by: str) -> pd.DataFrame:
        """Process and standardize summary data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d", errors="coerce").dt.strftime("%Y-%m-%d")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].str.split(".").str[0]

        group_col = (
            "date"
            if group_by == "date"
            else "symbol"
            if group_by == "stock"
            else "buyer_broker"
            if group_by == "broker"
            else "date"
        )

        if group_col not in df.columns:
            df[group_col] = ""

        agg_dict = {}
        if "vol" in df.columns or "volume" in df.columns:
            vol_col = "vol" if "vol" in df.columns else "volume"
            agg_dict[vol_col] = "sum"
        if "amount" in df.columns:
            agg_dict["amount"] = "sum"

        if not agg_dict:
            return df

        summary = df.groupby(group_col).agg(agg_dict).reset_index()

        summary["deal_count"] = df.groupby(group_col).size().values

        summary = summary.rename(columns={group_col: "group_key"})
        if "vol" in summary.columns:
            summary = summary.rename(columns={"vol": "total_volume"})
        elif "volume" in summary.columns:
            summary = summary.rename(columns={"volume": "total_volume"})
        else:
            summary["total_volume"] = 0

        if "amount" in summary.columns:
            summary = summary.rename(columns={"amount": "total_amount"})
        else:
            summary["total_amount"] = 0

        return summary
