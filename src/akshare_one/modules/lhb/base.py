"""
Base provider class for dragon tiger list data.

This module defines the abstract interface for dragon tiger list data providers.
"""

from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class DragonTigerProvider(BaseProvider):
    """
    Abstract base class for dragon tiger list data providers.
    
    Defines the interface for fetching various types of dragon tiger list data:
    - Dragon tiger list data (daily trading anomaly data)
    - Dragon tiger list summary statistics
    - Broker statistics from dragon tiger list
    """
    
    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return 'lhb'
    
    def get_update_frequency(self) -> str:
        """Dragon tiger list data is updated daily (T+1)."""
        return 'daily'
    
    def get_delay_minutes(self) -> int:
        """Dragon tiger list data is T+1, so delay is approximately 1 day."""
        return 1440  # 24 hours
    
    @abstractmethod
    def get_dragon_tiger_list(
        self,
        date: str,
        symbol: str | None
    ) -> pd.DataFrame:
        """
        Get dragon tiger list data.
        
        Args:
            date: Date (YYYY-MM-DD)
            symbol: Stock symbol (optional, if None returns all stocks)
        
        Returns:
            pd.DataFrame: Standardized dragon tiger list data
        """
        pass
    
    @abstractmethod
    def get_dragon_tiger_summary(
        self,
        start_date: str,
        end_date: str,
        group_by: str
    ) -> pd.DataFrame:
        """
        Get dragon tiger list summary statistics.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            group_by: Grouping dimension ('stock', 'broker', or 'reason')
        
        Returns:
            pd.DataFrame: Summary statistics grouped by specified dimension
        """
        pass
    
    @abstractmethod
    def get_dragon_tiger_broker_stats(
        self,
        start_date: str,
        end_date: str,
        top_n: int
    ) -> pd.DataFrame:
        """
        Get broker statistics from dragon tiger list.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            top_n: Number of top brokers to return
        
        Returns:
            pd.DataFrame: Broker statistics
        """
        pass
