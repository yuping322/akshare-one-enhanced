"""
Base provider class for ST stocks data.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class STProvider(BaseProvider):
    """Base class for ST stocks data providers."""

    def get_data_type(self) -> str:
        return "st"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    def get_st_stocks(self, **kwargs) -> pd.DataFrame:
        """Get ST (Special Treatment) stocks."""
        return self._execute_api_mapped("get_st_stocks", **kwargs)


class STFactory(BaseFactory["STProvider"]):
    """Factory class for creating ST stocks data providers."""

    _providers: dict[str, type["STProvider"]] = {}
