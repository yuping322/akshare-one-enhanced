"""
Base provider class for fund company data.

This module defines the abstract interface for fund company data providers.
"""

import pandas as pd

from ....core.base import BaseProvider
from ....core.factory import BaseFactory


class FundCompanyProvider(BaseProvider):
    """
    Base class for fund company data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "fund_company"

    def get_update_frequency(self) -> str:
        """Fund company data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Fund company data has minimal delay."""
        return 0

    def get_fund_company_info(self, stock_codes: list[str] | None = None, **kwargs) -> pd.DataFrame:
        """
        Get fund company information.

        Args:
            stock_codes: List of fund company codes (optional)

        Returns:
            pd.DataFrame: Fund company information
        """
        return self._execute_api_mapped("get_fund_company_info", stock_codes=stock_codes, **kwargs)

    def get_fund_company_fund_list(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get fund list managed by fund company.

        Args:
            stock_codes: List of fund company codes

        Returns:
            pd.DataFrame: Fund list data
        """
        return self._execute_api_mapped("get_fund_company_fund_list", stock_codes=stock_codes, **kwargs)

    def get_fund_company_fund_manager_list(self, stock_codes: list[str], **kwargs) -> pd.DataFrame:
        """
        Get fund manager list of fund company.

        Args:
            stock_codes: List of fund company codes

        Returns:
            pd.DataFrame: Fund manager list data
        """
        return self._execute_api_mapped("get_fund_company_fund_manager_list", stock_codes=stock_codes, **kwargs)

    def get_fund_company_shareholdings(
        self,
        stock_code: str,
        start_date: str,
        market: str,
        end_date: str | None = None,
        limit: int | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fund company shareholdings data.

        Args:
            stock_code: Fund company code
            start_date: Start date (YYYY-MM-DD)
            market: Stock market ('a' or 'h')
            end_date: End date (YYYY-MM-DD, optional)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Shareholdings data
        """
        return self._execute_api_mapped(
            "get_fund_company_shareholdings",
            stock_code=stock_code,
            start_date=start_date,
            market=market,
            end_date=end_date,
            limit=limit,
            **kwargs,
        )

    def get_fund_company_asset_scale(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund company asset scale data.

        Args:
            stock_code: Fund company code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Asset scale data
        """
        return self._execute_api_mapped(
            "get_fund_company_asset_scale",
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            **kwargs,
        )


class FundCompanyFactory(BaseFactory["FundCompanyProvider"]):
    """
    Factory class for creating fund company data providers.
    """

    _providers: dict[str, type["FundCompanyProvider"]] = {}


"""
Base provider class for fund manager data.

This module defines the abstract interface for fund manager data providers.
"""

import pandas as pd

from ....core.base import BaseProvider
from ....core.factory import BaseFactory


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
