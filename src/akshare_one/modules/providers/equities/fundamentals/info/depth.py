"""
Company depth data provider - extended company information APIs.
"""

import pandas as pd

from .....core.base import BaseProvider
from .base import InfoDataFactory


class CompanyDepthProvider(BaseProvider):
    """Extended provider for company depth data."""

    def get_data_type(self) -> str:
        return "companydepth"

    def get_update_frequency(self) -> str:
        return "daily"

    def get_delay_minutes(self) -> int:
        return 0

    def get_security_status(self, symbol: str, date: str = "", **kwargs) -> pd.DataFrame:
        """Get security status (ST, suspended, etc.)."""
        return self._execute_api_mapped("get_security_status", symbol=symbol, date=date, **kwargs)

    def get_name_history(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get stock name history."""
        return self._execute_api_mapped("get_name_history", symbol=symbol, **kwargs)

    def get_management_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get management information."""
        return self._execute_api_mapped("get_management_info", symbol=symbol, **kwargs)

    def get_employee_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get employee information."""
        return self._execute_api_mapped("get_employee_info", symbol=symbol, **kwargs)

    def get_listing_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get listing information."""
        return self._execute_api_mapped("get_listing_info", symbol=symbol, **kwargs)

    def get_industry_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get industry classification information."""
        return self._execute_api_mapped("get_industry_info", symbol=symbol, **kwargs)


class CompanyDepthFactory(InfoDataFactory):
    """Factory for company depth data providers."""

    pass


@CompanyDepthFactory.register("eastmoney")
class EastMoneyCompanyDepthProvider(CompanyDepthProvider):
    """Company depth data provider using EastMoney."""

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_security_status(self, symbol: str, date: str = "", **kwargs) -> pd.DataFrame:
        """Get security status from EastMoney."""
        df = self.akshare_adapter.call("stock_zh_a_spot_em")
        if not df.empty and symbol:
            for col in ["代码", "symbol", "code"]:
                if col in df.columns:
                    return df[df[col] == symbol]
        return df

    def get_name_history(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get stock name history from EastMoney."""
        return self.akshare_adapter.call("stock_info_change_name_em", symbol=symbol)

    def get_management_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get management information from EastMoney."""
        return self.akshare_adapter.call("stock_management_change_em", symbol=symbol)

    def get_employee_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get employee information from EastMoney."""
        return self.akshare_adapter.call("stock_ipo_summary", symbol=symbol)

    def get_listing_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get listing information from EastMoney."""
        df = self.akshare_adapter.call("stock_info_a_code_name")
        if not df.empty and symbol:
            for col in ["code", "代码", "symbol"]:
                if col in df.columns:
                    return df[df[col] == symbol]
        return df

    def get_industry_info(self, symbol: str, **kwargs) -> pd.DataFrame:
        """Get industry classification information from EastMoney."""
        return self.akshare_adapter.call("stock_individual_info_em", symbol=symbol)
