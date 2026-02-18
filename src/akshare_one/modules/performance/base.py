"""
Base provider class for performance data.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class PerformanceProvider(BaseProvider):
    """Abstract base class for performance data providers."""

    def get_data_type(self) -> str:
        return "performance"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_performance_forecast(self, date: str) -> pd.DataFrame:
        """Get performance forecast data."""
        pass

    @abstractmethod
    def get_performance_express(self, date: str) -> pd.DataFrame:
        """Get performance express data."""
        pass
