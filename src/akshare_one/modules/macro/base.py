"""
Base provider class for macro economic data.

This module defines the abstract interface for macro economic data providers.
"""

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class MacroProvider(BaseProvider):
    """
    Base class for macro economic data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "macro"

    def get_update_frequency(self) -> str:
        """Macro data is updated monthly or quarterly."""
        return "monthly"

    def get_delay_minutes(self) -> int:
        """Macro data has no real-time delay."""
        return 0

    def get_lpr_rate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get LPR (Loan Prime Rate) interest rate data.
        """
        return self._execute_api_mapped("get_lpr_rate", start_date=start_date, end_date=end_date, **kwargs)

    def get_pmi_index(self, start_date: str, end_date: str, pmi_type: str, **kwargs) -> pd.DataFrame:
        """
        Get PMI (Purchasing Managers' Index) data.
        """
        return self._execute_api_mapped("get_pmi_index", start_date=start_date, end_date=end_date, pmi_type=pmi_type, **kwargs)

    def get_cpi_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get CPI (Consumer Price Index) data.
        """
        return self._execute_api_mapped("get_cpi_data", start_date=start_date, end_date=end_date, **kwargs)

    def get_ppi_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get PPI (Producer Price Index) data.
        """
        return self._execute_api_mapped("get_ppi_data", start_date=start_date, end_date=end_date, **kwargs)

    def get_m2_supply(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get M2 money supply data.
        """
        return self._execute_api_mapped("get_m2_supply", start_date=start_date, end_date=end_date, **kwargs)

    def get_shibor_rate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get Shibor (Shanghai Interbank Offered Rate) data.
        """
        return self._execute_api_mapped("get_shibor_rate", start_date=start_date, end_date=end_date, **kwargs)

    def get_social_financing(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get social financing scale data.
        """
        return self._execute_api_mapped("get_social_financing", start_date=start_date, end_date=end_date, **kwargs)


class MacroFactory(BaseFactory["MacroProvider"]):
    """
    Factory class for creating macro economic data providers.
    """

    _providers: dict[str, type["MacroProvider"]] = {}
