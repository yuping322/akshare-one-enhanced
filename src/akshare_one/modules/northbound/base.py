"""
Base provider class for northbound capital data.

This module defines the abstract interface for northbound capital data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class NorthboundProvider(BaseProvider):
    """
    Abstract base class for northbound capital data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "northbound"

    def get_update_frequency(self) -> str:
        """Northbound data is updated daily (T+1)."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Northbound data has T+1 delay."""
        return 1440  # 24 hours

    @abstractmethod
    def get_northbound_flow(self, start_date: str, end_date: str, market: str, **kwargs) -> pd.DataFrame:
        """
        Get northbound capital flow data.
        """
        pass

    @abstractmethod
    def get_northbound_holdings(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get northbound holdings details.
        """
        pass

    @abstractmethod
    def get_northbound_top_stocks(self, date: str, market: str, top_n: int, **kwargs) -> pd.DataFrame:
        """
        Get northbound capital top stocks ranking.
        """
        pass


class NorthboundFactory(BaseFactory["NorthboundProvider"]):
    """
    Factory class for creating northbound capital data providers.
    """

    _providers: dict[str, type["NorthboundProvider"]] = {}
