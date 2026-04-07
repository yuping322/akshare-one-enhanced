"""
Base provider class for bond data.

This module defines the abstract interface for bond data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class BondProvider(BaseProvider):
    """
    Base class for bond data providers.
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

    @staticmethod
    def validate_symbol(symbol: str) -> None:
        """
        Validate bond symbol format.

        Args:
            symbol: Bond symbol (e.g., 'sh113050', 'sz123456')

        Raises:
            InvalidParameterError: If symbol format is invalid
        """
        from ..base import MarketType
        BaseProvider.validate_symbol(symbol, MarketType.BOND)

    def get_bond_list(self, **kwargs) -> pd.DataFrame:
        """
        Get convertible bond list.
        """
        return self._execute_api_mapped("get_bond_list", **kwargs)

    def get_bond_hist(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get bond historical data.
        """
        return self._execute_api_mapped("get_bond_hist", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)

    def get_bond_hist_data(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        return self.get_bond_hist(symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)

    def get_bond_realtime(self, **kwargs) -> pd.DataFrame:
        """
        Get bond realtime quotes.
        """
        return self._execute_api_mapped("get_bond_realtime", **kwargs)

    def get_bond_realtime_data(self, **kwargs) -> pd.DataFrame:
        return self.get_bond_realtime(**kwargs)


class BondFactory(BaseFactory["BondProvider"]):
    """
    Factory class for creating bond data providers.
    """

    _providers: dict[str, type["BondProvider"]] = {}
