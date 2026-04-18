"""
Base provider class for IPO data.
"""

import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class IPOProvider(BaseProvider):
    """Base class for IPO data providers."""

    def get_data_type(self) -> str:
        return "ipo"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    def get_new_stocks(self, **kwargs) -> pd.DataFrame:
        """Get newly listed stocks."""
        return self._execute_api_mapped("get_new_stocks", **kwargs)

    def get_ipo_info(self, **kwargs) -> pd.DataFrame:
        """Get IPO information."""
        return self._execute_api_mapped("get_ipo_info", **kwargs)


class IPOFactory(BaseFactory["IPOProvider"]):
    """Factory class for creating IPO data providers."""

    _providers: dict[str, type["IPOProvider"]] = {}
