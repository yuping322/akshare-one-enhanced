"""
Base provider class for equity pledge data.

This module defines the abstract interface for equity pledge data providers.
"""

import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class EquityPledgeProvider(BaseProvider):
    """
    Base class for equity pledge data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "pledge"

    def get_update_frequency(self) -> str:
        """Equity pledge data is updated irregularly."""
        return "irregular"

    def get_delay_minutes(self) -> int:
        """Equity pledge data is updated irregularly, no fixed delay."""
        return 0

    def get_equity_pledge(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get equity pledge data.
        """
        return self._execute_api_mapped("get_equity_pledge", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)

    def get_equity_pledge_ratio_rank(self, date: str, top_n: int, **kwargs) -> pd.DataFrame:
        """
        Get equity pledge ratio ranking.
        """
        return self._execute_api_mapped("get_equity_pledge_ratio_rank", date=date, top_n=top_n, **kwargs)


class EquityPledgeFactory(BaseFactory["EquityPledgeProvider"]):
    """Factory class for creating equity pledge data providers."""

    _providers: dict[str, type["EquityPledgeProvider"]] = {}
