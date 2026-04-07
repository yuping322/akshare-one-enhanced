"""
Base provider class for ETF data.

This module defines the abstract interface for ETF data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class ETFProvider(BaseProvider):
    """
    Base class for ETF data providers.
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

    def get_etf_hist(self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs) -> pd.DataFrame:
        """
        Get ETF historical data.
        """
        return self._execute_api_mapped("get_etf_hist", symbol=symbol, start_date=start_date, end_date=end_date, interval=interval, **kwargs)

    def get_etf_hist_data(self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs) -> pd.DataFrame:
        return self.get_etf_hist(symbol=symbol, start_date=start_date, end_date=end_date, interval=interval, **kwargs)

    def get_etf_spot(self, **kwargs) -> pd.DataFrame:
        """
        Get all ETF realtime quotes.
        """
        return self._execute_api_mapped("get_etf_spot", **kwargs)

    def get_etf_realtime_data(self, **kwargs) -> pd.DataFrame:
        return self.get_etf_spot(**kwargs)

    def get_etf_list(self, category: str = "all", **kwargs) -> pd.DataFrame:
        """
        Get ETF list.
        """
        return self._execute_api_mapped("get_etf_list", category=category, **kwargs)

    def get_fund_manager(self, **kwargs) -> pd.DataFrame:
        """
        Get fund manager information.
        """
        return self._execute_api_mapped("get_fund_manager", **kwargs)

    def get_fund_manager_info(self, **kwargs) -> pd.DataFrame:
        return self.get_fund_manager(**kwargs)

    def get_fund_rating(self, **kwargs) -> pd.DataFrame:
        return self._execute_api_mapped("get_fund_rating", **kwargs)

    def get_fund_rating_data(self, **kwargs) -> pd.DataFrame:
        return self.get_fund_rating(**kwargs)


class ETFFactory(BaseFactory["ETFProvider"]):
    """
    Factory class for creating ETF data providers.
    """

    _providers: dict[str, type["ETFProvider"]] = {}
