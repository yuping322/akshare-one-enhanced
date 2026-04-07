"""
Base provider class for block deal data.

This module defines the abstract interface for block deal data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class BlockDealProvider(BaseProvider):
    """
    Base class for block deal data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "blockdeal"

    def get_update_frequency(self) -> str:
        """Block deal data is updated daily (T+1)."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Block deal data is T+1, no intraday delay."""
        return 0

    def get_block_deal(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get block deal transaction details.
        """
        return self._execute_api_mapped("get_block_deal", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)

    def get_block_deal_summary(self, start_date: str, end_date: str, group_by: str, **kwargs) -> pd.DataFrame:
        """
        Get block deal summary statistics.
        """
        return self._execute_api_mapped("get_block_deal_summary", start_date=start_date, end_date=end_date, group_by=group_by, **kwargs)


class BlockDealFactory(BaseFactory["BlockDealProvider"]):
    """Factory class for creating block deal data providers."""

    _providers: dict[str, type["BlockDealProvider"]] = {}
