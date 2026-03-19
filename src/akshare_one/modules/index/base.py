"""
Base provider class for index data.

This module defines the abstract interface for index data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class IndexProvider(BaseProvider):
    """
    Abstract base class for index data providers.
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

    @abstractmethod
    def get_index_hist(self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs) -> pd.DataFrame:
        """
        Get index historical data.
        """
        pass

    @abstractmethod
    def get_index_realtime(self, symbol: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get index realtime quotes.
        """
        pass

    @abstractmethod
    def get_index_list(self, category: str = "cn", **kwargs) -> pd.DataFrame:
        """
        Get index list.
        """
        pass

    @abstractmethod
    def get_index_constituents(self, symbol: str, include_weight: bool = True, **kwargs) -> pd.DataFrame:
        """
        Get index constituent stocks.
        """
        pass


class IndexFactory(BaseFactory["IndexProvider"]):
    """
    Factory class for creating index data providers.
    """

    _providers: dict[str, type["IndexProvider"]] = {}
