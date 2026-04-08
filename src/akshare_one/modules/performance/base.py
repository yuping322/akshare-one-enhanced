"""
Base provider class for performance data.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class PerformanceProvider(BaseProvider):
    """Base class for performance data providers."""

    def get_data_type(self) -> str:
        return "performance"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    def get_performance_forecast(self, date: str, **kwargs) -> pd.DataFrame:
        """Get performance forecast data."""
        return self._execute_api_mapped("get_performance_forecast", date=date, **kwargs)

    def get_performance_express(self, date: str, **kwargs) -> pd.DataFrame:
        """Get performance express data."""
        return self._execute_api_mapped("get_performance_express", date=date, **kwargs)

    def get_all_company_performance(self, date: str, **kwargs) -> pd.DataFrame:
        """Get all company performance data."""
        return self._execute_api_mapped("get_all_company_performance", date=date, **kwargs)


class PerformanceFactory(BaseFactory["PerformanceProvider"]):
    """Factory class for creating performance data providers."""

    _providers: dict[str, type["PerformanceProvider"]] = {}
