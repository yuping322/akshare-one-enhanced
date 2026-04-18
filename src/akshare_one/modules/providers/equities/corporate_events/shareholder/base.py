"""
Base provider class for shareholder data.

This module defines the abstract interface for shareholder data providers.
"""

import pandas as pd

from .....core.base import BaseProvider
from .....core.factory import BaseFactory


class ShareholderProvider(BaseProvider):
    """
    Base class for shareholder data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "shareholder"

    def get_update_frequency(self) -> str:
        """Shareholder data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Shareholder data has 1 day delay."""
        return 0

    def get_shareholder_changes(
        self,
        symbol: str | None = None,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get shareholder changes (增减持) data.
        """
        return self._execute_api_mapped(
            "get_shareholder_changes", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_top_shareholders(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get top shareholders of a stock.
        """
        return self._execute_api_mapped("get_top_shareholders", symbol=symbol, **kwargs)

    def get_institution_holdings(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get institution holdings of a stock.
        """
        return self._execute_api_mapped("get_institution_holdings", symbol=symbol, **kwargs)

    def get_top10_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get top 10 shareholders of a stock.
        """
        return self._execute_api_mapped(
            "get_top10_shareholders", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_top10_float_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get top 10 float shareholders of a stock.
        """
        return self._execute_api_mapped(
            "get_top10_float_shareholders", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_fund_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get fund shareholders of a stock.
        """
        return self._execute_api_mapped(
            "get_fund_shareholders", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_top10_stock_holder_info(self, stock_code: str, top: int = 10, **kwargs) -> pd.DataFrame:
        """
        Get top 10 stock holder information.
        """
        return self._execute_api_mapped("get_top10_stock_holder_info", stock_code=stock_code, top=top, **kwargs)

    def get_latest_holder_number(self, date: str, **kwargs) -> pd.DataFrame:
        """
        Get latest holder number for all stocks.
        """
        return self._execute_api_mapped("get_latest_holder_number", date=date, **kwargs)


class ShareholderFactory(BaseFactory["ShareholderProvider"]):
    """Factory class for creating shareholder data providers."""

    _providers: dict[str, type["ShareholderProvider"]] = {}
