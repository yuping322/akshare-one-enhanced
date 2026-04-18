"""
TickFlow provider for historical data (K-line).

This module implements historical/K-line data provider using TickFlow API.
"""

import pandas as pd
from typing import Literal

from ......tickflow_client import get_tickflow_client
from .base import HistoricalDataFactory, HistoricalDataProvider


@HistoricalDataFactory.register("tickflow")
class TickFlowHistoricalProvider(HistoricalDataProvider):
    """
    Historical/K-line data provider using TickFlow API.

    Provides candlestick data with different periods and adjustment types.
    """

    PERIOD_MAP = {
        "day": "1d",
        "week": "1w",
        "month": "1M",
        "minute": "1m",
        "5min": "5m",
        "10min": "10m",
        "15min": "15m",
        "30min": "30m",
        "60min": "60m",
        "4hour": "4h",
        "quarter": "1Q",
        "year": "1Y",
    }

    ADJUST_MAP = {
        "none": "none",
        "qfq": "forward",
        "hfq": "backward",
    }

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "tickflow"

    def get_hist_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get historical/K-line data from TickFlow.

        Args:
            columns: Columns to return
            row_filter: Row filter

        Returns:
            pd.DataFrame: Candlestick data with columns:
                - timestamp: Timestamp
                - open: Open price
                - close: Close price
                - high: High price
                - low: Low price
                - volume: Volume
                - amount: Amount
        """
        client = get_tickflow_client()

        period = self.PERIOD_MAP.get(self.interval, "1d")

        adjust = self.ADJUST_MAP.get(self.adjust, "none")

        symbol = self.symbol
        if not "." in symbol:
            if symbol.startswith(("6", "9", "5")):
                symbol = f"{symbol}.SH"
            elif symbol.startswith(("0", "3", "1", "2")):
                symbol = f"{symbol}.SZ"
            elif symbol.startswith(("8", "4")):
                symbol = f"{symbol}.BJ"

        params = {
            "symbol": symbol,
            "period": period,
            "adjust": adjust,
        }

        if self.start_date and self.end_date:
            start_dt = pd.to_datetime(self.start_date)
            end_dt = pd.to_datetime(self.end_date)
            params["start_time"] = int(start_dt.timestamp() * 1000)
            params["end_time"] = int(end_dt.timestamp() * 1000)
        elif self.interval in ["minute", "5min", "10min", "15min", "30min", "60min"]:
            params["count"] = kwargs.get("count", 240)

        response = client.query_api("/v1/klines", method="GET", params=params)

        klines = response.get("data", [])
        if not klines:
            return pd.DataFrame()

        df = pd.DataFrame(klines)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        df = df.rename(columns={"timestamp": "datetime"})

        if "datetime" in df.columns:
            df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")
            df["time"] = df["datetime"].dt.strftime("%H:%M:%S")

        return self.standardize_and_filter(df, source="tickflow", columns=columns, row_filter=row_filter)

    def get_intraday_klines(
        self,
        period: Literal["1m", "5m", "10m", "15m", "30m", "60m"] = "1m",
        count: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get intraday (minute) K-line data for current day.

        Args:
            period: Minute period (1m, 5m, 10m, 15m, 30m, 60m)
            count: Number of bars to return
            columns: Columns to return
            row_filter: Row filter

        Returns:
            pd.DataFrame: Intraday K-line data
        """
        client = get_tickflow_client()

        symbol = self.symbol
        if not "." in symbol:
            if symbol.startswith(("6", "9", "5")):
                symbol = f"{symbol}.SH"
            elif symbol.startswith(("0", "3", "1", "2")):
                symbol = f"{symbol}.SZ"
            elif symbol.startswith(("8", "4")):
                symbol = f"{symbol}.BJ"

        params = {
            "symbol": symbol,
            "period": period,
        }

        if count:
            params["count"] = count

        response = client.query_api("/v1/klines/intraday", method="GET", params=params)

        klines = response.get("data", [])
        if not klines:
            return pd.DataFrame()

        df = pd.DataFrame(klines)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.rename(columns={"timestamp": "datetime"})
            df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")
            df["time"] = df["datetime"].dt.strftime("%H:%M:%S")

        return self.standardize_and_filter(df, source="tickflow", columns=columns, row_filter=row_filter)

    def get_ex_factors(
        self,
        start_time: int | None = None,
        end_time: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get ex-rights factors (除权因子).

        Args:
            start_time: Start timestamp (milliseconds)
            end_time: End timestamp (milliseconds)
            columns: Columns to return
            row_filter: Row filter

        Returns:
            pd.DataFrame: Ex-rights factors
        """
        client = get_tickflow_client()

        symbol = self.symbol
        if not "." in symbol:
            if symbol.startswith(("6", "9", "5")):
                symbol = f"{symbol}.SH"
            elif symbol.startswith(("0", "3", "1", "2")):
                symbol = f"{symbol}.SZ"

        params = {"symbols": symbol}

        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        response = client.query_api("/v1/klines/ex-factors", method="GET", params=params)

        factors = response.get("data", {}).get(symbol, [])
        if not factors:
            return pd.DataFrame()

        df = pd.DataFrame(factors)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")

        return self.standardize_and_filter(df, source="tickflow", columns=columns, row_filter=row_filter)
