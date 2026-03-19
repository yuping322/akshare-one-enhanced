"""
Base provider class for ETF data.

This module defines the abstract interface for ETF data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class ETFProvider(BaseProvider):
    """
    Abstract base class for ETF data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "etf"

    def get_update_frequency(self) -> str:
        """ETF data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """ETF data has 1 day delay for some fields."""
        return 0

    @abstractmethod
    def get_etf_hist(self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs) -> pd.DataFrame:
        """
        Get ETF historical data.
        """
        pass

    @abstractmethod
    def get_etf_spot(self, **kwargs) -> pd.DataFrame:
        """
        Get all ETF realtime quotes.
        """
        pass

    @abstractmethod
    def get_etf_list(self, category: str = "all", **kwargs) -> pd.DataFrame:
        """
        Get ETF list.
        """
        pass

    @abstractmethod
    def get_fund_manager(self, **kwargs) -> pd.DataFrame:
        """
        Get fund manager information.
        """
        pass


class ETFFactory(BaseFactory["ETFProvider"]):
    """
    Factory class for creating ETF data providers.
    """

    _providers: dict[str, type["ETFProvider"]] = {}
