"""
Base provider class for northbound capital data.

This module defines the abstract interface for northbound capital data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class NorthboundProvider(BaseProvider):
    """
    Abstract base class for northbound capital data providers.
    
    Defines the interface for fetching various types of northbound capital data:
    - Northbound capital flow (Shanghai/Shenzhen Connect)
    - Northbound holdings details
    - Northbound capital rankings
    """
    
    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return 'northbound'
    
    def get_update_frequency(self) -> str:
        """Northbound data is updated daily (T+1)."""
        return 'daily'
    
    def get_delay_minutes(self) -> int:
        """Northbound data has T+1 delay."""
        return 1440  # 24 hours
    
    @abstractmethod
    def get_northbound_flow(
        self,
        start_date: str,
        end_date: str,
        market: str
    ) -> pd.DataFrame:
        """
        Get northbound capital flow data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            market: Market type ('sh', 'sz', or 'all')
        
        Returns:
            pd.DataFrame: Standardized northbound flow data
        """
        pass
    
    @abstractmethod
    def get_northbound_holdings(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get northbound holdings details.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized northbound holdings data
        """
        pass
    
    @abstractmethod
    def get_northbound_top_stocks(
        self,
        date: str,
        market: str,
        top_n: int
    ) -> pd.DataFrame:
        """
        Get northbound capital top stocks ranking.
        
        Args:
            date: Date (YYYY-MM-DD)
            market: Market type ('sh', 'sz', or 'all')
            top_n: Number of top stocks to return
        
        Returns:
            pd.DataFrame: Ranked northbound holdings data
        """
        pass
