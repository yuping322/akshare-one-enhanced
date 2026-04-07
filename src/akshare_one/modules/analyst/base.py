"""
Base provider class for analyst data.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class AnalystProvider(BaseProvider):
    """Base class for analyst data providers."""

    def get_data_type(self) -> str:
        return "analyst"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    def get_analyst_rank(self, **kwargs) -> pd.DataFrame:
        """Get analyst ranking."""
        return self._execute_api_mapped("get_analyst_rank", **kwargs)

    def get_research_report(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get research reports for a stock."""
        return self._execute_api_mapped("get_research_report", symbol=symbol, **kwargs)


class AnalystFactory(BaseFactory["AnalystProvider"]):
    """Factory class for creating analyst data providers."""

    _providers: dict[str, type["AnalystProvider"]] = {}
