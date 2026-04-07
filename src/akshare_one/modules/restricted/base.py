"""
Base provider class for restricted stock release data.

This module defines the abstract interface for restricted stock release data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class RestrictedReleaseProvider(BaseProvider):
    """
    Base class for restricted stock release data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "restricted"

    def get_update_frequency(self) -> str:
        """Restricted release data is updated irregularly."""
        return "irregular"

    def get_delay_minutes(self) -> int:
        """Restricted release data is updated irregularly, no fixed delay."""
        return 0

    def get_restricted_release(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get restricted stock release data.
        """
        return self._execute_api_mapped("get_restricted_release", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)

    def get_restricted_release_calendar(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get restricted stock release calendar.
        """
        return self._execute_api_mapped("get_restricted_release_calendar", start_date=start_date, end_date=end_date, **kwargs)


class RestrictedReleaseFactory(BaseFactory["RestrictedReleaseProvider"]):
    """Factory class for creating restricted release data providers."""

    _providers: dict[str, type["RestrictedReleaseProvider"]] = {}
