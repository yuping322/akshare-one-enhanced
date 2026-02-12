"""
Base provider class for macro economic data.

This module defines the abstract interface for macro economic data providers.
"""

from abc import abstractmethod
import pandas as pd

from ..base import BaseProvider


class MacroProvider(BaseProvider):
    """
    Abstract base class for macro economic data providers.
    
    Defines the interface for fetching various types of macro economic data:
    - LPR interest rates
    - PMI indices
    - CPI/PPI data
    - M2 money supply
    - Shibor interest rates
    - Social financing scale
    """
    
    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return 'macro'
    
    def get_update_frequency(self) -> str:
        """Macro data is updated monthly or quarterly."""
        return 'monthly'
    
    def get_delay_minutes(self) -> int:
        """Macro data has no real-time delay."""
        return 0
    
    @abstractmethod
    def get_lpr_rate(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get LPR (Loan Prime Rate) interest rate data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized LPR rate data
        """
        pass
    
    @abstractmethod
    def get_pmi_index(
        self,
        start_date: str,
        end_date: str,
        pmi_type: str
    ) -> pd.DataFrame:
        """
        Get PMI (Purchasing Managers' Index) data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            pmi_type: PMI type ('manufacturing', 'non_manufacturing', or 'caixin')
        
        Returns:
            pd.DataFrame: Standardized PMI index data
        """
        pass
    
    @abstractmethod
    def get_cpi_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get CPI (Consumer Price Index) data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized CPI data
        """
        pass
    
    @abstractmethod
    def get_ppi_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get PPI (Producer Price Index) data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized PPI data
        """
        pass
    
    @abstractmethod
    def get_m2_supply(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get M2 money supply data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized M2 supply data
        """
        pass
    
    @abstractmethod
    def get_shibor_rate(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get Shibor (Shanghai Interbank Offered Rate) interest rate data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized Shibor rate data
        """
        pass
    
    @abstractmethod
    def get_social_financing(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get social financing scale data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized social financing data
        """
        pass
