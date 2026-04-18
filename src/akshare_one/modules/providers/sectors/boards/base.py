"""
Base provider class for board (KCB/CYB) data.
"""

import pandas as pd

from ....core.base import BaseProvider
from ....core.factory import BaseFactory


class BoardProvider(BaseProvider):
    """Base class for board data providers."""

    def get_data_type(self) -> str:
        return "board"

    def get_update_frequency(self) -> str:
        return "realtime"

    def get_delay_minutes(self) -> int:
        return 0

    def get_kcb_stocks(self, **kwargs) -> pd.DataFrame:
        """Get KCB (科创板) stocks."""
        return self._execute_api_mapped("get_kcb_stocks", **kwargs)

    def get_cyb_stocks(self, **kwargs) -> pd.DataFrame:
        """Get CYB (创业板) stocks."""
        return self._execute_api_mapped("get_cyb_stocks", **kwargs)


class BoardFactory(BaseFactory["BoardProvider"]):
    """Factory class for creating board data providers."""

    _providers: dict[str, type["BoardProvider"]] = {}
