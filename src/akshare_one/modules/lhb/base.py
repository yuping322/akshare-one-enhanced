"""
Base provider class for dragon tiger list data.

This module defines the abstract interface for dragon tiger list data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class DragonTigerProvider(BaseProvider):
    """
    Base class for dragon tiger list data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "lhb"

    def get_update_frequency(self) -> str:
        """Dragon tiger list data is updated daily (T+1)."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Dragon tiger list data is T+1, so delay is approximately 1 day."""
        return 1440  # 24 hours

    def get_dragon_tiger_list(self, date: str, symbol: str | None, **kwargs) -> pd.DataFrame:
        """
        Get dragon tiger list data.
        """
        return self._execute_api_mapped("get_dragon_tiger_list", date=date, symbol=symbol, **kwargs)

    def get_dragon_tiger_summary(self, start_date: str, end_date: str, group_by: str, **kwargs) -> pd.DataFrame:
        """
        Get dragon tiger list summary statistics.
        """
        return self._execute_api_mapped("get_dragon_tiger_summary", start_date=start_date, end_date=end_date, group_by=group_by, **kwargs)

    def get_dragon_tiger_broker_stats(self, start_date: str, end_date: str, top_n: int, **kwargs) -> pd.DataFrame:
        """
        Get broker statistics from dragon tiger list.
        """
        return self._execute_api_mapped("get_dragon_tiger_broker_stats", start_date=start_date, end_date=end_date, top_n=top_n, **kwargs)


class DragonTigerFactory(BaseFactory["DragonTigerProvider"]):
    """Factory class for creating dragon tiger list data providers."""

    _providers: dict[str, type["DragonTigerProvider"]] = {}
