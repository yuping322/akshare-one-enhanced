"""
Base provider class for shareholder depth data.

This module defines the abstract interface for shareholder depth data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class ShareholderDepthProvider(BaseProvider):
    """
    Base class for shareholder depth data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "shareholderdepth"

    def get_update_frequency(self) -> str:
        """Shareholder depth data is updated quarterly."""
        return "quarterly"

    def get_delay_minutes(self) -> int:
        """Shareholder depth data has minimal delay."""
        return 0

    def get_shareholder_structure(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get shareholder structure information.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Shareholder structure data
        """
        return self._execute_api_mapped("get_shareholder_structure", symbol=symbol, **kwargs)

    def get_shareholder_concentration(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get shareholder concentration information.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Shareholder concentration data
        """
        return self._execute_api_mapped("get_shareholder_concentration", symbol=symbol, **kwargs)

    def get_top_float_shareholders(self, symbol: str, date: str = None, **kwargs) -> pd.DataFrame:
        """
        Get top float shareholders.

        Args:
            symbol: Stock symbol
            date: Optional date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Top float shareholders data
        """
        return self._execute_api_mapped("get_top_float_shareholders", symbol=symbol, date=date, **kwargs)


class ShareholderDepthFactory(BaseFactory["ShareholderDepthProvider"]):
    """
    Factory class for creating shareholder depth data providers.
    """

    _providers: dict[str, type["ShareholderDepthProvider"]] = {}
