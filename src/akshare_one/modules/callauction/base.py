"""
Base provider class for call auction (集合竞价) data.

This module defines the abstract interface for call auction data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class CallAuctionProvider(BaseProvider):
    """
    Base class for call auction data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "callauction"

    def get_update_frequency(self) -> str:
        """Call auction data is available in realtime during trading hours."""
        return "realtime"

    def get_delay_minutes(self) -> int:
        """Call auction data is realtime, minimal delay."""
        return 0

    def get_call_auction(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get call auction data for a single stock.
        """
        return self._execute_api_mapped("get_call_auction", symbol=symbol, **kwargs)

    def get_call_auction_batch(self, symbols: list[str], **kwargs) -> pd.DataFrame:
        """
        Get call auction data for multiple stocks.
        """
        return self._execute_api_mapped("get_call_auction_batch", symbols=symbols, **kwargs)


class CallAuctionFactory(BaseFactory["CallAuctionProvider"]):
    """Factory class for creating call auction data providers."""

    _providers: dict[str, type["CallAuctionProvider"]] = {}
