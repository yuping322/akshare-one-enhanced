"""
Eastmoney futures data provider.

This module implements the futures data provider using Eastmoney as the data source.
"""

import pandas as pd

from .base import (
    FuturesHistoricalFactory,
    FuturesRealtimeFactory,
    HistoricalFuturesDataProvider,
    RealtimeFuturesDataProvider,
)


@FuturesHistoricalFactory.register("eastmoney")
class EastmoneyFuturesHistoricalProvider(HistoricalFuturesDataProvider):
    """
    Historical futures data provider using Eastmoney as the data source.
    """

    _API_MAP = {
        "get_hist_data": {
            "ak_func": None,  # Eastmoney futures historical data not implemented
        },
        "get_main_contracts": {
            "ak_func": None,  # Eastmoney futures main contracts not implemented
        },
    }

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def get_hist_data(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Get historical futures data from Eastmoney."""
        df = pd.DataFrame(
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
        return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

    def get_main_contracts(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Get main contract list from Eastmoney."""
        df = pd.DataFrame(columns=["symbol", "name", "contract", "exchange"])
        return self.apply_data_filter(df, columns=columns, row_filter=row_filter)


@FuturesRealtimeFactory.register("eastmoney")
class EastmoneyFuturesRealtimeProvider(RealtimeFuturesDataProvider):
    """
    Realtime futures data provider using Eastmoney as the data source.
    """

    _API_MAP = {
        "get_current_data": {
            "ak_func": None,  # Eastmoney futures realtime data not implemented
        },
        "get_all_quotes": {
            "ak_func": None,  # Eastmoney futures all quotes not implemented
        },
    }

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def get_current_data(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Get realtime futures data from Eastmoney."""
        df = pd.DataFrame(
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
        return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

    def get_all_quotes(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Get all futures quotes from Eastmoney."""
        df = pd.DataFrame(columns=["symbol", "contract", "price", "change", "pct_change", "volume", "open_interest"])
        return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
