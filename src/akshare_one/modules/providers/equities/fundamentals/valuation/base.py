"""
Base provider class for valuation data.

This module defines the abstract interface for valuation data providers.
"""

import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class ValuationProvider(BaseProvider):
    """
    Base class for valuation data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "valuation"

    def get_update_frequency(self) -> str:
        """Valuation data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Valuation data has 1 day delay."""
        return 0

    def get_stock_valuation(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get stock valuation data.
        """
        return self._execute_api_mapped("get_stock_valuation", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)

    def get_market_valuation(self, **kwargs) -> pd.DataFrame:
        """
        Get market-wide valuation data.
        """
        return self._execute_api_mapped("get_market_valuation", **kwargs)


class ValuationFactory(BaseFactory["ValuationProvider"]):
    """Factory class for creating valuation data providers."""

    _providers: dict[str, type["ValuationProvider"]] = {}
