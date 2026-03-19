"""
Base provider class for bond data.

This module defines the abstract interface for bond data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class BondProvider(BaseProvider):
    """
    Abstract base class for bond data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "bond"

    def get_update_frequency(self) -> str:
        """Bond data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Bond data has minimal delay."""
        return 0

    @abstractmethod
    def get_bond_list(self, **kwargs) -> pd.DataFrame:
        """
        Get convertible bond list.
        """
        pass

    @abstractmethod
    def get_bond_hist(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get bond historical data.
        """
        pass

    @abstractmethod
    def get_bond_realtime(self, **kwargs) -> pd.DataFrame:
        """
        Get bond realtime quotes.
        """
        pass


class BondFactory(BaseFactory["BondProvider"]):
    """
    Factory class for creating bond data providers.
    """

    _providers: dict[str, type["BondProvider"]] = {}
