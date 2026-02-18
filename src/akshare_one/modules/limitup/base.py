"""
Base provider class for limit up/down data.

This module defines the abstract interface for limit up/down data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class LimitUpDownProvider(BaseProvider):
    """
    Abstract base class for limit up/down data providers.
    
    Defines the interface for fetching various types of limit up/down data:
    - Limit up pool (涨停池)
    - Limit down pool (跌停池)
    - Limit up/down statistics
    """
    
    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return 'limitup'
    
    def get_update_frequency(self) -> str:
        """Limit up/down data is updated in realtime during trading hours."""
        return 'realtime'
    
    def get_delay_minutes(self) -> int:
        """Limit up/down data is realtime, minimal delay."""
        return 0
    
    @abstractmethod
    def get_limit_up_pool(self, date: str) -> pd.DataFrame:
        """
        Get limit up pool data.
        
        Args:
            date: Date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized limit up pool data
        """
        pass
    
    @abstractmethod
    def get_limit_down_pool(self, date: str) -> pd.DataFrame:
        """
        Get limit down pool data.
        
        Args:
            date: Date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized limit down pool data
        """
        pass
    
    @abstractmethod
    def get_limit_up_stats(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get limit up/down statistics.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Statistics data
        """
        pass
