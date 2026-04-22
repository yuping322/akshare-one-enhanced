"""
EastMoney provider for company depth data.

This module implements company depth data provider using EastMoney API.
"""

import pandas as pd

from .base import CompanyDepthFactory, CompanyDepthProvider


@CompanyDepthFactory.register("eastmoney")
class EastMoneyCompanyDepthProvider(CompanyDepthProvider):
    """
    Company depth data provider using EastMoney.

    Provides security status, name history, management info, employee info,
    listing info, and industry info.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_security_status(self, symbol: str, date: str = "", **kwargs) -> pd.DataFrame:
        """
        Get security status (ST, suspended, etc.) from EastMoney.

        Args:
            symbol: Stock symbol (e.g., '600000')
            date: Optional date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Security status data
        """
        df = self.akshare_adapter.call("stock_zh_a_spot_em")
        if not df.empty and symbol:
            for col in ["代码", "symbol", "code"]:
                if col in df.columns:
                    return df[df[col] == symbol]
        return df

    def get_name_history(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get stock name history from EastMoney.

        Args:
            symbol: Stock symbol (e.g., '600000')

        Returns:
            pd.DataFrame: Name history data
        """
        return self.akshare_adapter.call("stock_info_change_name_em", symbol=symbol)

    def get_management_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get management information from EastMoney.

        Args:
            symbol: Stock symbol (e.g., '600000')

        Returns:
            pd.DataFrame: Management info data
        """
        return self.akshare_adapter.call("stock_management_change_em", symbol=symbol)

    def get_employee_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get employee information from EastMoney.

        Args:
            symbol: Stock symbol (e.g., '600000')

        Returns:
            pd.DataFrame: Employee info data
        """
        return self.akshare_adapter.call("stock_ipo_summary", symbol=symbol)

    def get_listing_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get listing information from EastMoney.

        Args:
            symbol: Stock symbol (e.g., '600000')

        Returns:
            pd.DataFrame: Listing info data
        """
        df = self.akshare_adapter.call("stock_info_a_code_name")
        if not df.empty and symbol:
            for col in ["code", "代码", "symbol"]:
                if col in df.columns:
                    return df[df[col] == symbol]
        return df

    def get_industry_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get industry classification information from EastMoney.

        Args:
            symbol: Stock symbol (e.g., '600000')

        Returns:
            pd.DataFrame: Industry info data
        """
        return self.akshare_adapter.call("stock_individual_info_em", symbol=symbol)
