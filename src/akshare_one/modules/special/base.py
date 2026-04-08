"""
Base provider class for special data.

This module defines the abstract interface for special data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class SpecialDataProvider(BaseProvider):
    """
    Base class for special data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "special"

    def get_update_frequency(self) -> str:
        """Special data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Special data is T+1, no intraday delay."""
        return 0

    def get_chip_distribution(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get chip distribution data.
        """
        return self._execute_api_mapped(
            "get_chip_distribution", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_broker_forecast(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get broker profit forecast data.
        """
        return self._execute_api_mapped(
            "get_broker_forecast", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_institutional_research(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get institutional research data.
        """
        return self._execute_api_mapped(
            "get_institutional_research", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )


class SpecialDataFactory(BaseFactory["SpecialDataProvider"]):
    """Factory class for creating special data providers."""

    _providers: dict[str, type["SpecialDataProvider"]] = {}
