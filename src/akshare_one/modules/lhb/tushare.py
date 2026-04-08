"""
Tushare dragon tiger list data provider.

This module provides dragon tiger list data from Tushare Pro API.
"""

import pandas as pd
from typing import Optional

from ..cache import cache
from .base import DragonTigerFactory, DragonTigerProvider
from ...tushare_client import get_tushare_client


@DragonTigerFactory.register("tushare")
class TushareDragonTigerProvider(DragonTigerProvider):
    """Dragon tiger list data provider for Tushare Pro."""

    def get_source_name(self) -> str:
        return "tushare"

    def _convert_date_format(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to YYYYMMDD format for Tushare."""
        return date_str.replace("-", "")

    @cache(
        "lhb_cache",
        key=lambda self, date, symbol=None: f"tushare_lhb_list_{date}_{symbol}",
    )
    def get_dragon_tiger_list(self, date: str, symbol: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get dragon tiger list data from Tushare.

        Args:
            date: Date (YYYY-MM-DD)
            symbol: Stock symbol (optional, if None returns all stocks)

        Returns:
            pd.DataFrame: Standardized dragon tiger list data
        """
        self.validate_date(date)
        if symbol:
            self.validate_symbol(symbol)

        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return self.create_empty_dataframe(
                [
                    "date",
                    "symbol",
                    "name",
                    "close_price",
                    "pct_change",
                    "reason",
                    "buy_amount",
                    "sell_amount",
                    "net_amount",
                    "total_amount",
                    "turnover_rate",
                ]
            )

        trade_date = self._convert_date_format(date)

        try:
            params = {"trade_date": trade_date}
            if symbol:
                ts_code = self._convert_symbol_to_ts_code(symbol)
                params = {"ts_code": ts_code, "trade_date": trade_date}

            raw_df = client.get_top_list(**params)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    [
                        "date",
                        "symbol",
                        "name",
                        "close_price",
                        "pct_change",
                        "reason",
                        "buy_amount",
                        "sell_amount",
                        "net_amount",
                        "total_amount",
                        "turnover_rate",
                    ]
                )

            df = self._process_top_list_data(raw_df)
            return self.ensure_json_compatible(df)

        except Exception as e:
            self.logger.error(f"Failed to fetch dragon tiger list from Tushare: {e}")
            return self.create_empty_dataframe(
                [
                    "date",
                    "symbol",
                    "name",
                    "close_price",
                    "pct_change",
                    "reason",
                    "buy_amount",
                    "sell_amount",
                    "net_amount",
                    "total_amount",
                    "turnover_rate",
                ]
            )

    @cache(
        "lhb_cache",
        key=lambda self,
        start_date,
        end_date,
        group_by="date": f"tushare_lhb_summary_{start_date}_{end_date}_{group_by}",
    )
    def get_dragon_tiger_summary(
        self, start_date: str, end_date: str, group_by: str = "date", **kwargs
    ) -> pd.DataFrame:
        """
        Get dragon tiger list summary statistics from Tushare.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            group_by: Grouping dimension ('date', 'stock', or 'broker')

        Returns:
            pd.DataFrame: Summary statistics
        """
        self.validate_date_range(start_date, end_date)

        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return self.create_empty_dataframe(
                ["date", "stock_count", "total_buy_amount", "total_sell_amount", "net_amount"]
            )

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            raw_df = client.get_top_list(start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    ["date", "stock_count", "total_buy_amount", "total_sell_amount", "net_amount"]
                )

            df = self._process_summary_data(raw_df, group_by)
            return self.ensure_json_compatible(df)

        except Exception as e:
            self.logger.error(f"Failed to fetch dragon tiger summary from Tushare: {e}")
            return self.create_empty_dataframe(
                ["date", "stock_count", "total_buy_amount", "total_sell_amount", "net_amount"]
            )

    @cache(
        "lhb_cache",
        key=lambda self, start_date, end_date, top_n=100: f"tushare_lhb_broker_{start_date}_{end_date}_{top_n}",
    )
    def get_dragon_tiger_broker_stats(self, start_date: str, end_date: str, top_n: int = 100, **kwargs) -> pd.DataFrame:
        """
        Get broker statistics from dragon tiger list from Tushare.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            top_n: Number of top brokers to return

        Returns:
            pd.DataFrame: Broker statistics
        """
        self.validate_date_range(start_date, end_date)
        if top_n <= 0:
            raise ValueError(f"top_n must be positive, got {top_n}")

        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return self.create_empty_dataframe(
                [
                    "rank",
                    "broker_name",
                    "list_count",
                    "buy_amount",
                    "buy_count",
                    "sell_amount",
                    "sell_count",
                    "net_amount",
                    "total_amount",
                ]
            )

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            raw_df = client.get_top_inst(start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    [
                        "rank",
                        "broker_name",
                        "list_count",
                        "buy_amount",
                        "buy_count",
                        "sell_amount",
                        "sell_count",
                        "net_amount",
                        "total_amount",
                    ]
                )

            df = self._process_broker_stats_data(raw_df, top_n)
            return self.ensure_json_compatible(df)

        except Exception as e:
            self.logger.error(f"Failed to fetch broker statistics from Tushare: {e}")
            return self.create_empty_dataframe(
                [
                    "rank",
                    "broker_name",
                    "list_count",
                    "buy_amount",
                    "buy_count",
                    "sell_amount",
                    "sell_count",
                    "net_amount",
                    "total_amount",
                ]
            )

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

    def _process_top_list_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize top_list data."""
        df = pd.DataFrame()

        if "trade_date" in raw_df.columns:
            df["date"] = pd.to_datetime(raw_df["trade_date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")

        if "ts_code" in raw_df.columns:
            df["symbol"] = raw_df["ts_code"].str.split(".").str[0]

        if "name" in raw_df.columns:
            df["name"] = raw_df["name"].astype(str)

        if "close" in raw_df.columns:
            df["close_price"] = raw_df["close"].astype(float)

        if "pct_change" in raw_df.columns:
            df["pct_change"] = raw_df["pct_change"].astype(float)

        if "turnover_rate" in raw_df.columns:
            df["turnover_rate"] = raw_df["turnover_rate"].astype(float)

        amount_fields = {
            "buy_amount": "buy_elg_vol",
            "sell_amount": "sell_elg_vol",
            "net_amount": "net_elg_vol",
            "total_amount": "total_vol",
        }

        for target_col, source_col in amount_fields.items():
            if source_col in raw_df.columns:
                df[target_col] = raw_df[source_col].astype(float)

        if "abnormal_type" in raw_df.columns:
            df["reason"] = raw_df["abnormal_type"].astype(str)
        else:
            df["reason"] = ""

        df = df.reset_index(drop=True)
        return df

    def _process_summary_data(self, raw_df: pd.DataFrame, group_by: str) -> pd.DataFrame:
        """Process and aggregate summary data."""
        if raw_df.empty:
            return pd.DataFrame()

        if "trade_date" in raw_df.columns:
            raw_df["date"] = pd.to_datetime(raw_df["trade_date"], format="%Y%m%d")

        if group_by == "date":
            grouped = (
                raw_df.groupby("date")
                .agg(
                    {
                        "ts_code": "count",
                        "buy_elg_vol": "sum",
                        "sell_elg_vol": "sum",
                        "net_elg_vol": "sum",
                    }
                )
                .reset_index()
            )

            df = pd.DataFrame()
            df["date"] = grouped["date"].dt.strftime("%Y-%m-%d")
            df["stock_count"] = grouped["ts_code"].astype(int)
            df["total_buy_amount"] = grouped["buy_elg_vol"].astype(float)
            df["total_sell_amount"] = grouped["sell_elg_vol"].astype(float)
            df["net_amount"] = grouped["net_elg_vol"].astype(float)

        elif group_by == "stock":
            if "ts_code" not in raw_df.columns:
                return pd.DataFrame()

            grouped = (
                raw_df.groupby("ts_code")
                .agg(
                    {
                        "trade_date": "count",
                        "buy_elg_vol": "sum",
                        "sell_elg_vol": "sum",
                        "net_elg_vol": "sum",
                        "total_vol": "sum",
                    }
                )
                .reset_index()
            )

            df = pd.DataFrame()
            df["symbol"] = grouped["ts_code"].str.split(".").str[0]
            df["list_count"] = grouped["trade_date"].astype(int)
            df["total_buy_amount"] = grouped["buy_elg_vol"].astype(float)
            df["total_sell_amount"] = grouped["sell_elg_vol"].astype(float)
            df["net_amount"] = grouped["net_elg_vol"].astype(float)
            df["total_amount"] = grouped["total_vol"].astype(float)

        else:
            df = pd.DataFrame()

        return df.reset_index(drop=True)

    def _process_broker_stats_data(self, raw_df: pd.DataFrame, top_n: int) -> pd.DataFrame:
        """Process and aggregate broker statistics data."""
        if raw_df.empty:
            return pd.DataFrame()

        if "exalter" not in raw_df.columns:
            return pd.DataFrame()

        grouped = (
            raw_df.groupby("exalter")
            .agg(
                {
                    "trade_date": "count",
                    "buy_value": "sum",
                    "sell_value": "sum",
                }
            )
            .reset_index()
        )

        grouped["net_amount"] = grouped["buy_value"] - grouped["sell_value"]
        grouped["total_amount"] = grouped["buy_value"] + grouped["sell_value"]

        grouped = grouped.sort_values("total_amount", ascending=False).head(top_n)

        df = pd.DataFrame()
        df["rank"] = range(1, len(grouped) + 1)
        df["broker_name"] = grouped["exalter"].astype(str)
        df["list_count"] = grouped["trade_date"].astype(int)
        df["buy_amount"] = grouped["buy_value"].astype(float)
        df["buy_count"] = 0
        df["sell_amount"] = grouped["sell_value"].astype(float)
        df["sell_count"] = 0
        df["net_amount"] = grouped["net_amount"].astype(float)
        df["total_amount"] = grouped["total_amount"].astype(float)

        return df.reset_index(drop=True)
