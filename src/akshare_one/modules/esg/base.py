"""
Base provider class for ESG rating data.

This module defines the abstract interface for ESG rating data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class ESGProvider(BaseProvider):
    """
    Base class for ESG rating data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "esg"

    def get_update_frequency(self) -> str:
        """ESG data is updated irregularly."""
        return "irregular"

    def get_delay_minutes(self) -> int:
        """ESG data is updated irregularly, typically with a delay."""
        return 43200  # 30 days in minutes

    def get_esg_rating(
        self,
        symbol: str | None = None,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        page: int = 1,
        page_size: int | None = 1,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get ESG rating data.
        """
        return self._execute_api_mapped("get_esg_rating", symbol=symbol, start_date=start_date, end_date=end_date, page=page, page_size=page_size, **kwargs)

    def get_esg_rating_rank(self, date: str | None = None, industry: str | None = None, top_n: int = 100, **kwargs) -> pd.DataFrame:
        """
        Get ESG rating rankings.
        """
        return self._execute_api_mapped("get_esg_rating_rank", date=date, industry=industry, top_n=top_n, **kwargs)


class ESGFactory(BaseFactory["ESGProvider"]):
    """Factory class for creating ESG data providers."""

    _providers: dict[str, type["ESGProvider"]] = {}
