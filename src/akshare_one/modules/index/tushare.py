"""
Tushare index data provider.

This module provides index data from Tushare Pro API.
"""

import pandas as pd
from typing import Optional

from ..cache import cache
from .base import IndexFactory, IndexProvider
from ...tushare_client import get_tushare_client


@IndexFactory.register("tushare")
class TushareIndexProvider(IndexProvider):
    """Index data provider for Tushare Pro."""

    def __init__(self, **kwargs):
        """Initialize the Tushare index provider."""
        super().__init__()
        self._kwargs = kwargs

    def get_source_name(self) -> str:
        return "tushare"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Tushare.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def _convert_symbol_to_ts_code(self, symbol: str) -> str:
        """Convert symbol to Tushare ts_code format."""
        if "." in symbol:
            return symbol
        elif symbol.startswith("6") or symbol.startswith("000"):
            return f"{symbol}.SH"
        elif symbol.startswith(("0", "3")):
            return f"{symbol}.SZ"
        else:
            return f"{symbol}.SH"

    def _convert_date_format(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to YYYYMMDD format for Tushare."""
        return date_str.replace("-", "")

    @cache(
        "index_cache",
        key=lambda self, columns=None, row_filter=None, **kwargs: f"tushare_index_list_{columns}_{row_filter}",
    )
    def get_index_list(
        self,
        category: str = "cn",
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get index list from Tushare.

        Args:
            category: Index category ('cn' for Chinese indices)
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Index list
        """
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        try:
            market_map = {"cn": "SSE", "szse": "SZSE", "csi": "CSI"}
            market = market_map.get(category, "SSE")

            raw_df = client.get_index_basic(market=market, **kwargs)

            if raw_df.empty:
                return pd.DataFrame()

            df = self.map_source_fields(raw_df, "tushare")
            df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)

            if not df.empty and "symbol" in df.columns:
                df["type"] = "cn_index"

            return df
        except Exception as e:
            self.logger.error(f"Failed to get index list from Tushare: {e}")
            return pd.DataFrame()

    @cache(
        "index_cache",
        key=lambda self,
        symbol,
        start_date,
        end_date,
        interval="daily",
        columns=None,
        row_filter=None: f"tushare_index_hist_{symbol}_{start_date}_{end_date}_{interval}",
    )
    def get_index_hist(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "daily",
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get index historical data from Tushare.

        Args:
            symbol: Index symbol (e.g., '000001')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('daily', 'weekly', 'monthly')
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Standardized historical data
        """
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        try:
            ts_code = self._convert_symbol_to_ts_code(symbol)
            start_date_ts = self._convert_date_format(start_date)
            end_date_ts = self._convert_date_format(end_date)

            raw_df = client.get_index_daily(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_historical_data(raw_df)
            df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)

            if not df.empty:
                df["symbol"] = symbol

            return df
        except Exception as e:
            self.logger.error(f"Failed to get index historical data from Tushare for {symbol}: {e}")
            return pd.DataFrame()

    def get_index_hist_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "daily",
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Alias for get_index_hist."""
        return self.get_index_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            columns=columns,
            row_filter=row_filter,
            **kwargs,
        )

    @cache(
        "index_cache",
        key=lambda self,
        symbol=None,
        columns=None,
        row_filter=None: f"tushare_index_realtime_{symbol}_{columns}_{row_filter}",
    )
    def get_index_realtime(
        self,
        symbol: Optional[str] = None,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get index realtime data from Tushare (using latest daily data).

        Args:
            symbol: Index symbol (optional)
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Realtime index data
        """
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        try:
            from datetime import datetime

            today = datetime.now().strftime("%Y%m%d")
            yesterday = (datetime.now() - pd.Timedelta(days=1)).strftime("%Y%m%d")

            if symbol:
                ts_code = self._convert_symbol_to_ts_code(symbol)
                raw_df = client.get_index_daily(ts_code=ts_code, start_date=yesterday, end_date=today)
            else:
                raw_df = client.get_index_dailybasic(trade_date=today)

            if raw_df.empty:
                return pd.DataFrame()

            df = self.map_source_fields(raw_df, "tushare")
            df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)

            return df
        except Exception as e:
            self.logger.error(f"Failed to get index realtime data from Tushare: {e}")
            return pd.DataFrame()

    def get_index_realtime_data(
        self,
        symbol: Optional[str] = None,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Alias for get_index_realtime."""
        return self.get_index_realtime(symbol=symbol, columns=columns, row_filter=row_filter, **kwargs)

    @cache(
        "index_cache",
        key=lambda self,
        symbol,
        include_weight=True,
        columns=None,
        row_filter=None: f"tushare_index_constituents_{symbol}_{include_weight}",
    )
    def get_index_constituents(
        self,
        symbol: str,
        include_weight: bool = True,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get index constituent stocks from Tushare.

        Args:
            symbol: Index symbol
            include_weight: Whether to include weight
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Constituent stocks
        """
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        try:
            from datetime import datetime, timedelta

            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

            raw_df = client.get_index_weight(index_code=symbol, start_date=start_date, end_date=end_date)

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_constituent_data(raw_df, include_weight)
            df = self.standardize_and_filter(df, self.get_source_name(), columns=columns, row_filter=row_filter)

            return df
        except Exception as e:
            self.logger.error(f"Failed to get index constituents from Tushare for {symbol}: {e}")
            return pd.DataFrame(columns=["symbol", "name", "weight"])

    def _process_historical_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize historical data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")

        df = df.sort_values("date", ascending=True).reset_index(drop=True)

        return df

    def _process_constituent_data(self, raw_df: pd.DataFrame, include_weight: bool) -> pd.DataFrame:
        """Process and standardize constituent data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "constituent_code" in df.columns:
            df["symbol"] = df["constituent_code"].str.split(".").str[0]

        if not include_weight and "weight" in df.columns:
            df = df.drop(columns=["weight"])

        return df
