"""
Base provider class for limit up/down data.

This module defines the abstract interface for limit up/down data providers.
"""

import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class LimitUpDownProvider(BaseProvider):
    """
    Base class for limit up/down data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "limitup"

    def get_update_frequency(self) -> str:
        """Limit up/down data is updated in realtime during trading hours."""
        return "realtime"

    def get_delay_minutes(self) -> int:
        """Limit up/down data is realtime, minimal delay."""
        return 0

    def get_limit_up_pool(self, date: str, **kwargs) -> pd.DataFrame:
        """
        Get limit up pool data.
        """
        return self._execute_api_mapped("get_limit_up_pool", date=date, **kwargs)

    def get_limit_down_pool(self, date: str, **kwargs) -> pd.DataFrame:
        """
        Get limit down pool data.
        """
        return self._execute_api_mapped("get_limit_down_pool", date=date, **kwargs)

    def get_limit_up_stats(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get limit up/down statistics.
        """
        return self._execute_api_mapped("get_limit_up_stats", start_date=start_date, end_date=end_date, **kwargs)


class LimitUpDownFactory(BaseFactory["LimitUpDownProvider"]):
    """Factory class for creating limit up/down data providers."""

    _providers: dict[str, type["LimitUpDownProvider"]] = {}
