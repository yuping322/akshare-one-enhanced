"""
Base provider class for index weights data.
"""

import pandas as pd

from ....core.base import BaseProvider
from ....core.factory import BaseFactory


class IndexWeightsProvider(BaseProvider):
    """Base class for index weights data providers."""

    def get_data_type(self) -> str:
        return "indexweights"

    def get_index_weights(self, index_code: str, date: str = "") -> pd.DataFrame:
        """Get index component weights."""
        return self._execute_api_mapped("get_index_weights", index_code=index_code, date=date)

    def get_index_weights_history(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get index component weights history."""
        return self._execute_api_mapped(
            "get_index_weights_history", index_code=index_code, start_date=start_date, end_date=end_date
        )

    def get_index_info(self, index_code: str = "") -> pd.DataFrame:
        """Get index basic information."""
        return self._execute_api_mapped("get_index_info", index_code=index_code)


class IndexWeightsFactory(BaseFactory[IndexWeightsProvider]):
    """Factory for index weights data providers."""

    _providers: dict[str, type[IndexWeightsProvider]] = {}
