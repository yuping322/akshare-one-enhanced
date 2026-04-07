"""
Base provider class for industry sector data.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class IndustryProvider(BaseProvider):
    """Base class for industry sector data providers."""

    def get_data_type(self) -> str:
        return "industry"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    def get_industry_list(self, **kwargs) -> pd.DataFrame:
        """Get industry sector list."""
        return self._execute_api_mapped("get_industry_list", **kwargs)

    def get_industry_stocks(self, industry: str, **kwargs) -> pd.DataFrame:
        """Get stocks in an industry sector."""
        return self._execute_api_mapped("get_industry_stocks", industry=industry, **kwargs)


class IndustryFactory(BaseFactory["IndustryProvider"]):
    """Factory class for creating industry sector data providers."""

    _providers: dict[str, type["IndustryProvider"]] = {}
