"""
Base provider class for index data.

This module defines the abstract interface for index data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class IndexProvider(BaseProvider):
    """
    Base class for index data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "index"

    def get_update_frequency(self) -> str:
        """Index data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Index data has minimal delay."""
        return 0

    def get_index_hist(self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs) -> pd.DataFrame:
        """
        Get index historical data.
        """
        return self._execute_api_mapped("get_index_hist", symbol=symbol, start_date=start_date, end_date=end_date, interval=interval, **kwargs)

    def get_index_hist_data(self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs) -> pd.DataFrame:
        return self.get_index_hist(symbol=symbol, start_date=start_date, end_date=end_date, interval=interval, **kwargs)

    def get_index_realtime(self, symbol: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get index realtime quotes.
        """
        return self._execute_api_mapped("get_index_realtime", symbol=symbol, **kwargs)

    def get_index_realtime_data(self, symbol: str | None = None, **kwargs) -> pd.DataFrame:
        return self.get_index_realtime(symbol=symbol, **kwargs)

    def get_index_list(self, category: str = "cn", **kwargs) -> pd.DataFrame:
        """
        Get index list.
        """
        return self._execute_api_mapped("get_index_list", category=category, **kwargs)

    def get_index_constituents(self, symbol: str, include_weight: bool = True, **kwargs) -> pd.DataFrame:
        """
        Get index constituent stocks.
        """
        return self._execute_api_mapped("get_index_constituents", symbol=symbol, include_weight=include_weight, **kwargs)


class IndexFactory(BaseFactory["IndexProvider"]):
    """
    Factory class for creating index data providers.
    """

    _providers: dict[str, type["IndexProvider"]] = {}
