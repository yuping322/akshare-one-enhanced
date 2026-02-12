"""
Base provider class for margin financing data.

This module defines the abstract interface for margin financing data providers.
"""

from abc import abstractmethod
from typing import Optional
import pandas as pd

from ..base import BaseProvider


class MarginProvider(BaseProvider):
    """
    Abstract base class for margin financing data providers.
    
    Defines the interface for fetching various types of margin financing data:
    - Margin financing data (individual stocks and market-wide)
    - Margin financing summary (market aggregation)
    """
    
    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return 'margin'
    
    def get_update_frequency(self) -> str:
        """Margin financing data is updated daily (T+1)."""
        return 'daily'
    
    def get_delay_minutes(self) -> int:
        """Margin financing data is T+1, updated next trading day."""
        return 1440  # 24 hours
    
    @abstractmethod
    def get_margin_data(
        self,
        symbol: Optional[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get margin financing data.
        
        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized margin financing data
        """
        pass
    
    @abstractmethod
    def get_margin_summary(
        self,
        start_date: str,
        end_date: str,
        market: str
    ) -> pd.DataFrame:
        """
        Get margin financing summary data.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            market: Market ('sh', 'sz', or 'all')
        
        Returns:
            pd.DataFrame: Summary data
        """
        pass
