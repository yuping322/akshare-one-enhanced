"""
src/akshare_one/modules/etf/base.py
Base classes for ETF data providers.
"""

import pandas as pd

from ....core.base import BaseProvider
from ....core.factory import BaseFactory


class ETFProvider(BaseProvider):
    """Base class for ETF/LOF data providers."""
    def get_data_type(self) -> str:
        return "etf"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_etf_list(self, category: str = "all") -> pd.DataFrame:
        """Get list of ETFs."""
        return self._execute_api_mapped("get_etf_list", category=category)

    def get_etf_hist(self, symbol: str, start_date: str, end_date: str, interval: str = "daily") -> pd.DataFrame:
        """Get ETF historical data."""
        return self._execute_api_mapped("get_etf_hist", symbol=symbol, start_date=start_date, end_date=end_date, interval=interval)

    def get_etf_spot(self) -> pd.DataFrame:
        """Get ETF realtime quotes."""
        return self._execute_api_mapped("get_etf_spot")

    def get_fund_manager(self) -> pd.DataFrame:
        """Get fund manager information."""
        return self._execute_api_mapped("get_fund_manager")

    def get_fund_rating(self) -> pd.DataFrame:
        """Get fund ratings."""
        return self._execute_api_mapped("get_fund_rating")

    def get_fund_nav(self, symbol: str) -> pd.DataFrame:
        """Get Net Asset Value (NAV) history."""
        return self._execute_api_mapped("get_fund_nav", symbol=symbol)

class ETFFactory(BaseFactory[ETFProvider]):
    """Factory for ETF data providers."""
    _providers: dict[str, type[ETFProvider]] = {}
