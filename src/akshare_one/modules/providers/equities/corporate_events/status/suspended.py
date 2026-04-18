"""
Base provider class for suspended stocks data.
"""

import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class SuspendedProvider(BaseProvider):
    """Base class for suspended stocks data providers."""

    def get_data_type(self) -> str:
        return "suspended"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    def get_suspended_stocks(self, **kwargs) -> pd.DataFrame:
        """Get suspended/halted stocks."""
        return self._execute_api_mapped("get_suspended_stocks", **kwargs)


class SuspendedFactory(BaseFactory["SuspendedProvider"]):
    """Factory class for creating suspended stocks data providers."""

    _providers: dict[str, type["SuspendedProvider"]] = {}
