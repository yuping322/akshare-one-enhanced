"""
Base provider class for goodwill data.

This module defines the abstract interface for goodwill data providers.
"""

from abc import abstractmethod
from typing import Optional
import pandas as pd

from ..base import BaseProvider


class GoodwillProvider(BaseProvider):
    """
    Abstract base class for goodwill data providers.
    
    Defines the interface for fetching various types of goodwill data:
    - Goodwill data (balance and ratios)
    - Goodwill impairment expectations
    - Goodwill statistics by industry
    """
    
    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return 'goodwill'
    
    def get_update_frequency(self) -> str:
        """Goodwill data is updated quarterly."""
        return 'quarterly'
    
    def get_delay_minutes(self) -> int:
        """Goodwill data is updated quarterly, typically with a delay."""
        return 43200  # 30 days in minutes
    
    @abstractmethod
    def get_goodwill_data(
        self,
        symbol: Optional[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get goodwill data.
        
        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized goodwill data
        """
        pass
    
    @abstractmethod
    def get_goodwill_impairment(
        self,
        date: str
    ) -> pd.DataFrame:
        """
        Get goodwill impairment expectations.
        
        Args:
            date: Query date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Goodwill impairment expectations
        """
        pass
    
    @abstractmethod
    def get_goodwill_by_industry(
        self,
        date: str
    ) -> pd.DataFrame:
        """
        Get goodwill statistics by industry.
        
        Args:
            date: Query date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Industry goodwill statistics
        """
        pass
