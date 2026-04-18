"""
Base provider class for company depth data.

This module defines the abstract interface for company depth data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class CompanyDepthProvider(BaseProvider):
    """
    Base class for company depth data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "companydepth"

    def get_update_frequency(self) -> str:
        """Company depth data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Company depth data has minimal delay."""
        return 0

    def get_security_status(self, symbol: str, date: str = "", **kwargs) -> pd.DataFrame:
        """
        Get security status (ST, suspended, etc.).

        Args:
            symbol: Stock symbol
            date: Optional date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Security status data
        """
        return self._execute_api_mapped("get_security_status", symbol=symbol, date=date, **kwargs)

    def get_name_history(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get stock name history.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Name history data
        """
        return self._execute_api_mapped("get_name_history", symbol=symbol, **kwargs)

    def get_management_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get management information.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Management info data
        """
        return self._execute_api_mapped("get_management_info", symbol=symbol, **kwargs)

    def get_employee_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get employee information.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Employee info data
        """
        return self._execute_api_mapped("get_employee_info", symbol=symbol, **kwargs)

    def get_listing_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get listing information.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Listing info data
        """
        return self._execute_api_mapped("get_listing_info", symbol=symbol, **kwargs)

    def get_industry_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get industry classification information.

        Args:
            symbol: Stock symbol

        Returns:
            pd.DataFrame: Industry info data
        """
        return self._execute_api_mapped("get_industry_info", symbol=symbol, **kwargs)


class CompanyDepthFactory(BaseFactory["CompanyDepthProvider"]):
    """
    Factory class for creating company depth data providers.
    """

    _providers: dict[str, type["CompanyDepthProvider"]] = {}
