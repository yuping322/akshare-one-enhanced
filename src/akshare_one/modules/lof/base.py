"""
Base classes for LOF (Listed Open-Ended Fund) data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class LOFProvider(BaseProvider):
    """Base class for LOF data providers."""

    def get_data_type(self) -> str:
        return "lof"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_lof_list(self) -> pd.DataFrame:
        """Get list of LOF funds."""
        return self._execute_api_mapped("get_lof_list")

    def get_lof_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get LOF historical data."""
        return self._execute_api_mapped("get_lof_hist", symbol=symbol, start_date=start_date, end_date=end_date)

    def get_lof_spot(self) -> pd.DataFrame:
        """Get LOF realtime quotes."""
        return self._execute_api_mapped("get_lof_spot")

    def get_lof_nav(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get LOF Net Asset Value (NAV) history."""
        return self._execute_api_mapped("get_lof_nav", symbol=symbol, start_date=start_date, end_date=end_date)


class LOFFactory(BaseFactory[LOFProvider]):
    """Factory for LOF data providers."""

    _providers: dict[str, type[LOFProvider]] = {}
