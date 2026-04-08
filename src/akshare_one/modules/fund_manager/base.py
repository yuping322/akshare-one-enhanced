"""
Base provider class for fund manager data.

This module defines the abstract interface for fund manager data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class FundManagerProvider(BaseProvider):
    """
    Base class for fund manager data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "fund_manager"

    def get_update_frequency(self) -> str:
        """Fund manager data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Fund manager data has minimal delay."""
        return 0

    def get_fund_manager_info(self, stock_codes: list[str] | None = None, **kwargs) -> pd.DataFrame:
        """
        Get fund manager information.

        Args:
            stock_codes: List of fund manager codes (optional)

        Returns:
            pd.DataFrame: Fund manager information
        """
        return self._execute_api_mapped("get_fund_manager_info", stock_codes=stock_codes, **kwargs)

    def get_fund_manager_hot_fmp(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get hot fund manager profit ratio (收益率).

        Args:
            stock_codes: List of fund manager codes

        Returns:
            pd.DataFrame: Fund manager profit ratio data
        """
        return self._execute_api_mapped("get_fund_manager_hot_fmp", stock_codes=stock_codes, **kwargs)

    def get_fund_manager_management_funds(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get funds managed by fund manager.

        Args:
            stock_codes: List of fund manager codes

        Returns:
            pd.DataFrame: Managed funds data
        """
        return self._execute_api_mapped("get_fund_manager_management_funds", stock_codes=stock_codes, **kwargs)

    def get_fund_manager_profit_ratio(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund manager profit ratio data.

        Args:
            stock_code: Fund manager code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Profit ratio data
        """
        return self._execute_api_mapped(
            "get_fund_manager_profit_ratio",
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            **kwargs,
        )

    def get_fund_manager_shareholdings(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund manager shareholdings data.

        Args:
            stock_code: Fund manager code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Shareholdings data
        """
        return self._execute_api_mapped(
            "get_fund_manager_shareholdings",
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            **kwargs,
        )


class FundManagerFactory(BaseFactory["FundManagerProvider"]):
    """
    Factory class for creating fund manager data providers.
    """

    _providers: dict[str, type["FundManagerProvider"]] = {}
