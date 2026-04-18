"""
Base provider class for margin financing data.

This module defines the abstract interface for margin financing data providers.
"""

import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class MarginProvider(BaseProvider):
    """
    Base class for margin financing data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "margin"

    def get_update_frequency(self) -> str:
        """Margin financing data is updated daily (T+1)."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Margin financing data is T+1, updated next trading day."""
        return 1440  # 24 hours

    def get_margin_data(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get margin financing data.
        """
        return self._execute_api_mapped("get_margin_data", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)

    def get_margin_summary(self, start_date: str, end_date: str, market: str, **kwargs) -> pd.DataFrame:
        """
        Get margin financing summary data.
        """
        return self._execute_api_mapped("get_margin_summary", start_date=start_date, end_date=end_date, market=market, **kwargs)


class MarginFactory(BaseFactory["MarginProvider"]):
    """Factory class for creating margin data providers."""

    _providers: dict[str, type["MarginProvider"]] = {}
