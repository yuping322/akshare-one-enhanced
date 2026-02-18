"""
Base provider class for board (KCB/CYB) data.
"""

from abc import abstractmethod
import pandas as pd

from ..base import BaseProvider


class BoardProvider(BaseProvider):
    """Abstract base class for board data providers."""

    def get_data_type(self) -> str:
        return "board"

    def get_update_frequency(self) -> str:
        return "realtime"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_kcb_stocks(self) -> pd.DataFrame:
        """Get KCB (科创板) stocks."""
        pass

    @abstractmethod
    def get_cyb_stocks(self) -> pd.DataFrame:
        """Get CYB (创业板) stocks."""
        pass
