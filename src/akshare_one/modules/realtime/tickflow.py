"""
TickFlow provider for realtime market data.

This module implements realtime data provider using TickFlow API.
"""

import pandas as pd

from ...tickflow_client import get_tickflow_client
from .base import RealtimeDataFactory, RealtimeDataProvider


@RealtimeDataFactory.register("tickflow")
class TickFlowRealtimeProvider(RealtimeDataProvider):
    """
    Realtime data provider using TickFlow API.

    Provides realtime quotes for A股、ETF、美股、港股.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "tickflow"

    def get_current_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get realtime market data from TickFlow.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters
                - symbols: List of symbols or comma-separated string (e.g., "600000.SH,000001.SZ")
                - universes: List of universe IDs or comma-separated string

        Returns:
            pd.DataFrame: Realtime data with columns:
                - symbol: Stock code
                - name: Stock name
                - last_price: Latest price
                - prev_close: Previous close price
                - open: Open price
                - high: High price
                - low: Low price
                - volume: Volume
                - amount: Amount
                - timestamp: Timestamp (milliseconds)
                - change_pct: Change percentage
                - change_amount: Change amount
                - amplitude: Amplitude
                - turnover_rate: Turnover rate
        """
        client = get_tickflow_client()

        symbols = kwargs.get("symbols")
        universes = kwargs.get("universes")

        if self.symbol:
            if isinstance(self.symbol, list):
                symbols = self.symbol
            else:
                symbols = (
                    [self.symbol]
                    if "." in self.symbol
                    else [f"{self.symbol}.SH" if self.symbol.startswith(("6", "9", "5")) else f"{self.symbol}.SZ"]
                )

        if not symbols and not universes:
            universes = ["CN_Equity_A"]
            self.logger.info(
                "No symbols/universes provided, using default universe: CN_Equity_A",
                extra={
                    "context": {
                        "log_type": "default_universe",
                        "provider": "tickflow",
                    }
                },
            )

        if symbols and isinstance(symbols, list):
            data = {"symbols": symbols}
            response = client.query_api("/v1/quotes", method="POST", data=data)
        elif universes and isinstance(universes, list):
            data = {"universes": universes}
            response = client.query_api("/v1/quotes", method="POST", data=data)
        elif symbols:
            params = {"symbols": symbols}
            response = client.query_api("/v1/quotes", method="GET", params=params)
        elif universes:
            params = {"universes": universes}
            response = client.query_api("/v1/quotes", method="GET", params=params)
        else:
            return pd.DataFrame()

        quotes = response.get("data", [])
        if not quotes:
            return pd.DataFrame()

        df = pd.DataFrame(quotes)

        if "ext" in df.columns:
            ext_data = df["ext"].apply(lambda x: x if isinstance(x, dict) else {})
            ext_df = pd.DataFrame(ext_data.tolist())

            for col in ext_df.columns:
                if col not in df.columns and col != "type":
                    df[col] = ext_df[col]

            df.drop(columns=["ext"], errors="ignore", inplace=True)

        column_rename = {
            "last_price": "price",
            "change_pct": "pct_change",
            "change_amount": "change",
        }
        df = df.rename(columns={k: v for k, v in column_rename.items() if k in df.columns})

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        return self.standardize_and_filter(df, source="tickflow", columns=columns, row_filter=row_filter)
