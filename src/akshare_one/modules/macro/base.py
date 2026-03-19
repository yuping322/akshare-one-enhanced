"""
Base provider class for macro economic data.

This module defines the abstract interface for macro economic data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider
from ..factory_base import BaseFactory


class MacroProvider(BaseProvider):
    """
    Abstract base class for macro economic data providers.
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

    @abstractmethod
    def get_lpr_rate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get LPR (Loan Prime Rate) interest rate data.
        """
        pass

    @abstractmethod
    def get_pmi_index(self, start_date: str, end_date: str, pmi_type: str, **kwargs) -> pd.DataFrame:
        """
        Get PMI (Purchasing Managers' Index) data.
        """
        pass

    @abstractmethod
    def get_cpi_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get CPI (Consumer Price Index) data.
        """
        pass

    @abstractmethod
    def get_ppi_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get PPI (Producer Price Index) data.
        """
        pass

    @abstractmethod
    def get_m2_supply(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get M2 money supply data.
        """
        pass

    @abstractmethod
    def get_shibor_rate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get Shibor (Shanghai Interbank Offered Rate) data.
        """
        pass


class MacroFactory(BaseFactory["MacroProvider"]):
    """
    Factory class for creating macro economic data providers.
    """

    _providers: dict[str, type["MacroProvider"]] = {}
