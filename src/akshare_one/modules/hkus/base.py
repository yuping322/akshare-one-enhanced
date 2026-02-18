"""
Base provider class for HK/US stock data.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class HKUSProvider(BaseProvider):
    """Abstract base class for HK/US stock data providers."""

    def get_data_type(self) -> str:
        return "hkus"

    def get_update_frequency(self) -> str:
        return "realtime"

    def get_delay_minutes(self) -> int:
        return 0

    @abstractmethod
    def get_hk_stocks(self) -> pd.DataFrame:
        """Get Hong Kong stock list."""
        pass

    @abstractmethod
    def get_us_stocks(self) -> pd.DataFrame:
        """Get US stock list."""
        pass
