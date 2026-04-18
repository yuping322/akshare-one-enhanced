"""
Base classes for FOF (Fund of Funds) data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class FOFProvider(BaseProvider):
    """Base class for FOF data providers."""

    def get_data_type(self) -> str:
        return "fundof"

    def get_fof_list(self) -> pd.DataFrame:
        """Get list of FOF funds."""
        return self._execute_api_mapped("get_fof_list")

    def get_fof_nav(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """Get FOF Net Asset Value (NAV) history."""
        return self._execute_api_mapped("get_fof_nav", symbol=symbol, start_date=start_date, end_date=end_date)

    def get_fof_info(self, symbol: str) -> pd.DataFrame:
        """Get FOF fund information."""
        return self._execute_api_mapped("get_fof_info", symbol=symbol)


class FOFFactory(BaseFactory[FOFProvider]):
    """Factory for FOF data providers."""

    _providers: dict[str, type[FOFProvider]] = {}
