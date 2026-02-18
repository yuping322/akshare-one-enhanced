"""
Base provider class for industry sector data.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class IndustryProvider(BaseProvider):
    """Abstract base class for industry sector data providers."""

    def get_data_type(self) -> str:
        return "industry"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_industry_list(self) -> pd.DataFrame:
        """Get industry sector list."""
        pass

    @abstractmethod
    def get_industry_stocks(self, industry: str) -> pd.DataFrame:
        """Get stocks in an industry sector."""
        pass
