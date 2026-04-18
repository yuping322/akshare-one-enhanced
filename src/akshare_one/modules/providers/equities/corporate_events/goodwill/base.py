"""
Base provider class for goodwill data.

This module defines the abstract interface for goodwill data providers.
"""

import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class GoodwillProvider(BaseProvider):
    """
    Base class for goodwill data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "goodwill"

    def get_update_frequency(self) -> str:
        """Goodwill data is updated quarterly."""
        return "quarterly"

    def get_delay_minutes(self) -> int:
        """Goodwill data is updated quarterly, typically with a delay."""
        return 43200  # 30 days in minutes

    def get_goodwill_data(self, symbol: str | None = None, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs) -> pd.DataFrame:
        """
        Get goodwill data.
        """
        return self._execute_api_mapped("get_goodwill_data", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)

    def get_goodwill_impairment(self, date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get goodwill impairment expectations.
        """
        return self._execute_api_mapped("get_goodwill_impairment", date=date, **kwargs)

    def get_goodwill_by_industry(self, date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get goodwill statistics by industry.
        """
        return self._execute_api_mapped("get_goodwill_by_industry", date=date, **kwargs)


class GoodwillFactory(BaseFactory["GoodwillProvider"]):
    """Factory class for creating goodwill data providers."""

    _providers: dict[str, type["GoodwillProvider"]] = {}
