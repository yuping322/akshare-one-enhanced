"""
Base provider class for analyst data.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class AnalystProvider(BaseProvider):
    """Abstract base class for analyst data providers."""

    def get_data_type(self) -> str:
        return "analyst"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_analyst_rank(self) -> pd.DataFrame:
        """Get analyst ranking."""
        pass

    @abstractmethod
    def get_research_report(self, symbol: str) -> pd.DataFrame:
        """Get research reports for a stock."""
        pass
