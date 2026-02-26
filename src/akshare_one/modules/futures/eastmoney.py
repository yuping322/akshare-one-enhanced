"""
Eastmoney futures data provider.

This module implements the futures data provider using Eastmoney as the data source.
"""

import pandas as pd

from .base import HistoricalFuturesDataProvider, RealtimeFuturesDataProvider


class EastmoneyFuturesHistoricalProvider(HistoricalFuturesDataProvider):
    """
    Historical futures data provider using Eastmoney as the data source.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def get_hist_data(self) -> pd.DataFrame:
        """Get historical futures data from Eastmoney."""
        return pd.DataFrame(
            columns=[
                "timestamp",
                "symbol",
                "contract",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "open_interest",
                "settlement",
            ]
        )

    def get_main_contracts(self) -> pd.DataFrame:
        """Get main contract list from Eastmoney."""
        return pd.DataFrame(columns=["symbol", "name", "contract", "exchange"])


class EastmoneyFuturesRealtimeProvider(RealtimeFuturesDataProvider):
    """
    Realtime futures data provider using Eastmoney as the data source.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def get_current_data(self) -> pd.DataFrame:
        """Get realtime futures data from Eastmoney."""
        return pd.DataFrame(
            columns=[
                "symbol",
                "contract",
                "price",
                "change",
                "pct_change",
                "timestamp",
                "volume",
                "open_interest",
                "open",
                "high",
                "low",
                "prev_settlement",
                "settlement",
            ]
        )

    def get_all_quotes(self) -> pd.DataFrame:
        """Get all futures quotes from Eastmoney."""
        return pd.DataFrame(columns=["symbol", "contract", "price", "change", "pct_change", "volume", "open_interest"])
