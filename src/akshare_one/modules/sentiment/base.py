"""
Base provider class for sentiment data.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class SentimentProvider(BaseProvider):
    """Base class for sentiment data providers."""

    def get_data_type(self) -> str:
        return "sentiment"

    def get_update_frequency(self) -> str:
        return "realtime"

    def get_delay_minutes(self) -> int:
        return 0

    def get_hot_rank(self, **kwargs) -> pd.DataFrame:
        """Get hot stock ranking."""
        return self._execute_api_mapped("get_hot_rank", **kwargs)

    def get_stock_comment(self, **kwargs) -> pd.DataFrame:
        """Get stock comments and sentiment scores."""
        return self._execute_api_mapped("get_stock_comment", **kwargs)


class SentimentFactory(BaseFactory["SentimentProvider"]):
    """Factory class for creating sentiment data providers."""

    _providers: dict[str, type["SentimentProvider"]] = {}
