"""
Base provider class for ST stocks data.
"""

from abc import abstractmethod
import pandas as pd

from ..base import BaseProvider


class STProvider(BaseProvider):
    """Abstract base class for ST stocks data providers."""

    def get_data_type(self) -> str:
        return "st"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_st_stocks(self) -> pd.DataFrame:
        """Get ST (Special Treatment) stocks."""
        pass
