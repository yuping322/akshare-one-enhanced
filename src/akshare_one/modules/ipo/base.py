"""
Base provider class for IPO data.
"""

from abc import abstractmethod
import pandas as pd

from ..base import BaseProvider


class IPOProvider(BaseProvider):
    """Abstract base class for IPO data providers."""

    def get_data_type(self) -> str:
        return "ipo"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_new_stocks(self) -> pd.DataFrame:
        """Get newly listed stocks."""
        pass

    @abstractmethod
    def get_ipo_info(self) -> pd.DataFrame:
        """Get IPO information."""
        pass
