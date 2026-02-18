"""
Base provider class for suspended stocks data.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class SuspendedProvider(BaseProvider):
    """Abstract base class for suspended stocks data providers."""

    def get_data_type(self) -> str:
        return "suspended"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_suspended_stocks(self) -> pd.DataFrame:
        """Get suspended/halted stocks."""
        pass
