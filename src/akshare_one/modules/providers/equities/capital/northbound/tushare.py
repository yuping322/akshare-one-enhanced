"""
Tushare provider for northbound capital data.

This module implements the northbound capital data provider using Tushare as the data source.
"""

import time

import pandas as pd

from ......metrics.stats import get_stats_collector
from ......tushare_client import get_tushare_client
from ......constants import SYMBOL_ZFILL_WIDTH
from .....core.cache import cache
from .base import NorthboundFactory, NorthboundProvider


@NorthboundFactory.register("tushare")
class TushareNorthboundProvider(NorthboundProvider):
    """
    Tushare implementation of northbound capital data provider.

    Uses Tushare Pro API to fetch northbound capital data.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "tushare"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Tushare.

        This method is not used directly; specific methods fetch their own data.
        """
        return pd.DataFrame()

    @cache(
        "northbound_cache",
        key=lambda self,
        start_date="1970-01-01",
        end_date="2030-12-31",
        market="all": f"tushare_flow_{start_date}_{end_date}_{market}",
    )
    def get_northbound_flow(self, start_date: str, end_date: str, market: str) -> pd.DataFrame:
        """
        Get northbound capital flow data from Tushare.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            market: Market type ('sh', 'sz', or 'all')

        Returns:
            pd.DataFrame: Standardized northbound flow data
        """
        self.validate_date_range(start_date, end_date)

        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return self.create_empty_dataframe(
                ["date", "market", "northbound_net_buy", "northbound_buy_amount", "northbound_sell_amount"]
            )

        start_time = time.time()
        try:
            start_date_ts = self._convert_date_format(start_date)
            end_date_ts = self._convert_date_format(end_date)

            raw_df = client.get_moneyflow_hkctl(start_date=start_date_ts, end_date=end_date_ts)

            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, True)
            except (ImportError, AttributeError):
                pass

            if raw_df.empty:
                return self.create_empty_dataframe(
                    ["date", "market", "northbound_net_buy", "northbound_buy_amount", "northbound_sell_amount"]
                )

            df = self._standardize_flow_data(raw_df, market)
            df = self._filter_by_date_range(df, start_date, end_date)
            return self.ensure_json_compatible(df)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, False)
            except (ImportError, AttributeError):
                pass
            self.logger.error(f"Failed to fetch northbound flow from Tushare: {e}")
            return self.create_empty_dataframe(
                ["date", "market", "northbound_net_buy", "northbound_buy_amount", "northbound_sell_amount"]
            )

    @cache(
        "northbound_cache",
        key=lambda self,
        symbol=None,
        start_date="1970-01-01",
        end_date="2030-12-31": f"tushare_hold_{symbol}_{start_date}_{end_date}",
    )
    def get_northbound_holdings(self, symbol: str | None, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get northbound holdings details from Tushare.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized northbound holdings data
        """
        self.validate_date_range(start_date, end_date)
        if symbol is not None:
            self.validate_symbol(symbol)

        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return self.create_empty_dataframe(
                ["date", "symbol", "holdings_shares", "holdings_value", "holdings_ratio"]
            )

        start_time = time.time()
        try:
            start_date_ts = self._convert_date_format(start_date)
            end_date_ts = self._convert_date_format(end_date)

            ts_code = None
            if symbol:
                ts_code = self._convert_symbol_to_ts_code(symbol)

            raw_df = client.get_hk_hold(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)

            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, True)
            except (ImportError, AttributeError):
                pass

            if raw_df.empty:
                return self.create_empty_dataframe(
                    ["date", "symbol", "holdings_shares", "holdings_value", "holdings_ratio"]
                )

            df = self._standardize_holdings_data(raw_df)
            df = self._filter_by_date_range(df, start_date, end_date)
            return self.ensure_json_compatible(df)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, False)
            except (ImportError, AttributeError):
                pass
            self.logger.error(f"Failed to fetch northbound holdings from Tushare: {e}")
            return self.create_empty_dataframe(
                ["date", "symbol", "holdings_shares", "holdings_value", "holdings_ratio"]
            )

    @cache(
        "northbound_cache",
        key=lambda self, date=None, market="all", top_n=100: f"tushare_top10_{date}_{market}_{top_n}",
    )
    def get_northbound_top_stocks(self, date: str | None, market: str, top_n: int) -> pd.DataFrame:
        """
        Get northbound capital top stocks ranking from Tushare (沪深股通十大成交股).

        Args:
            date: Date (YYYY-MM-DD). If None, returns latest.
            market: Market type ('sh', 'sz', or 'all')
            top_n: Number of top stocks to return

        Returns:
            pd.DataFrame: Ranked northbound top stocks data
        """
        if date:
            self.validate_date(date)

        if market not in ["sh", "sz", "all"]:
            raise ValueError(f"Invalid market: {market}. Must be 'sh', 'sz', or 'all'")

        if top_n <= 0:
            raise ValueError(f"top_n must be positive, got {top_n}")

        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return self.create_empty_dataframe(
                ["rank", "symbol", "name", "northbound_net_buy", "buy_amount", "sell_amount"]
            )

        start_time = time.time()
        try:
            trade_date = None
            if date:
                trade_date = self._convert_date_format(date)

            raw_df = client.get_hk_top10(trade_date=trade_date)

            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, True)
            except (ImportError, AttributeError):
                pass

            if raw_df.empty:
                return self.create_empty_dataframe(
                    ["rank", "symbol", "name", "northbound_net_buy", "buy_amount", "sell_amount"]
                )

            df = self._standardize_top10_data(raw_df, market)
            df = df.head(top_n).reset_index(drop=True)
            df["rank"] = range(1, len(df) + 1)
            return self.ensure_json_compatible(df)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            try:
                stats_collector = get_stats_collector()
                stats_collector.record_request("tushare", duration_ms, False)
            except (ImportError, AttributeError):
                pass
            self.logger.error(f"Failed to fetch northbound top stocks from Tushare: {e}")
            return self.create_empty_dataframe(
                ["rank", "symbol", "name", "northbound_net_buy", "buy_amount", "sell_amount"]
            )

    def _convert_date_format(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to YYYYMMDD format for Tushare."""
        return date_str.replace("-", "")

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

    def _standardize_flow_data(self, raw_df: pd.DataFrame, market: str) -> pd.DataFrame:
        """Standardize northbound flow data from Tushare."""
        df = self.map_source_fields(raw_df, "tushare")

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")

        df["market"] = market

        return df

    def _standardize_holdings_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Standardize northbound holdings data from Tushare."""
        df = self.map_source_fields(raw_df, "tushare")

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].astype(str).str.split(".").str[0].str.zfill(SYMBOL_ZFILL_WIDTH)

        return df

    def _standardize_top10_data(self, raw_df: pd.DataFrame, market: str) -> pd.DataFrame:
        """Standardize top 10 data from Tushare."""
        df = self.map_source_fields(raw_df, "tushare")

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")

        if "ts_code" in df.columns:
            df["symbol"] = df["ts_code"].astype(str).str.split(".").str[0].str.zfill(SYMBOL_ZFILL_WIDTH)

        if market == "sh":
            df = df[df["symbol"].str.startswith("6")].reset_index(drop=True)
        elif market == "sz":
            df = df[df["symbol"].str.match(r"^[03]")].reset_index(drop=True)

        return df

    def _filter_by_date_range(self, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter DataFrame by date range."""
        if "date" in df.columns and not df.empty:
            mask = (df["date"] >= start_date) & (df["date"] <= end_date)
            return df[mask].reset_index(drop=True)
        return df
