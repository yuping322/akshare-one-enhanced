"""
Base provider class for sentiment data.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class SentimentProvider(BaseProvider):
    """Abstract base class for sentiment data providers."""

    def get_data_type(self) -> str:
        return "sentiment"

    def get_update_frequency(self) -> str:
        return "realtime"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_hot_rank(self) -> pd.DataFrame:
        """Get hot stock ranking."""
        pass

    @abstractmethod
    def get_stock_comment(self) -> pd.DataFrame:
        """Get stock comments and sentiment scores."""
        pass
