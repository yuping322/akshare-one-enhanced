"""
Base provider class for company data.

This module defines the abstract interface for company data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class CompanyProvider(BaseProvider):
    """
    Base class for company data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "company"

    def get_update_frequency(self) -> str:
        """Company data is updated daily."""
        return "daily"

    def get_delay_minutes(self) -> int:
        """Company data has minimal delay."""
        return 0

    def get_company_profile(self, symbols: list[str] | str, **kwargs) -> pd.DataFrame:
        """
        Get company profile data.

        Args:
            symbols: Stock symbols (list or single symbol)

        Returns:
            pd.DataFrame: Company profile data
        """
        return self._execute_api_mapped("get_company_profile", symbols=symbols, **kwargs)

    def get_company_indices(self, symbol: str, date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get indices that a stock belongs to.

        Args:
            symbol: Stock symbol
            date: Optional date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Indices data
        """
        return self._execute_api_mapped("get_company_indices", symbol=symbol, date=date, **kwargs)

    def get_company_industries(self, symbol: str, date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get industries that a stock belongs to.

        Args:
            symbol: Stock symbol
            date: Optional date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Industries data
        """
        return self._execute_api_mapped("get_company_industries", symbol=symbol, date=date, **kwargs)

    def get_company_mutual_market(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get mutual market (陆股通) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Mutual market data
        """
        return self._execute_api_mapped(
            "get_company_mutual_market", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_company_fundamental_financial(
        self,
        symbols: list[str] | str,
        metrics: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fundamental data for financial companies.

        Args:
            symbols: Stock symbols (list or single symbol)
            metrics: List of metrics to fetch
            date: Optional specific date (YYYY-MM-DD)
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Fundamental data
        """
        return self._execute_api_mapped(
            "get_company_fundamental_financial",
            symbols=symbols,
            metrics=metrics,
            date=date,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

    def get_company_allotment(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get allotment (配股) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Allotment data
        """
        return self._execute_api_mapped(
            "get_company_allotment", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_company_split(self, symbol: str, start_date: str, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get split (拆分) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Split data
        """
        return self._execute_api_mapped(
            "get_company_split", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_company_customers(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get customers (客户) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Customers data
        """
        return self._execute_api_mapped(
            "get_company_customers", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_company_suppliers(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get suppliers (供应商) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Suppliers data
        """
        return self._execute_api_mapped(
            "get_company_suppliers", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_company_equity_change(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get equity change (股本变动) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Equity change data
        """
        return self._execute_api_mapped(
            "get_company_equity_change", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_company_operating_data(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get operating data (经营数据) for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Operating data
        """
        return self._execute_api_mapped(
            "get_company_operating_data", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_company_operation_revenue_constitution(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get operation revenue constitution (营业收入构成) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Operation revenue constitution data
        """
        return self._execute_api_mapped(
            "get_company_operation_revenue_constitution",
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

    def get_company_fund_collection_shareholders(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund collection shareholders (基金持仓股东) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Fund collection shareholders data
        """
        return self._execute_api_mapped(
            "get_company_fund_collection_shareholders",
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

    def get_company_hot_tr_dri(self, symbols: list[str] | str, **kwargs) -> pd.DataFrame:
        """
        Get hot TR DRI (热门股票分红再投入收益率) data.

        Args:
            symbols: Stock symbols (list or single symbol)

        Returns:
            pd.DataFrame: Hot TR DRI data
        """
        return self._execute_api_mapped("get_company_hot_tr_dri", symbols=symbols, **kwargs)

    def get_company_inquiry(self, symbol: str, start_date: str, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get inquiry (问询函) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Inquiry data
        """
        return self._execute_api_mapped(
            "get_company_inquiry", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_company_measures(self, symbol: str, start_date: str, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get measures (监管措施) data for a stock.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Measures data
        """
        return self._execute_api_mapped(
            "get_company_measures", symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
        )


class CompanyFactory(BaseFactory["CompanyProvider"]):
    """
    Factory class for creating company data providers.
    """

    _providers: dict[str, type["CompanyProvider"]] = {}
