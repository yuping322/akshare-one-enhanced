"""
Base provider class for block deal data.

This module defines the abstract interface for block deal data providers.
"""

from abc import abstractmethod
import pandas as pd

from ..base import BaseProvider


class BlockDealProvider(BaseProvider):
    """
    Abstract base class for block deal data providers.
    
    Defines the interface for fetching block deal transaction data:
    - Block deal details (individual stock and market-wide)
    - Block deal summary statistics
    """
    
    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return 'blockdeal'
    
    def get_update_frequency(self) -> str:
        """Block deal data is updated daily (T+1)."""
        return 'daily'
    
    def get_delay_minutes(self) -> int:
        """Block deal data is T+1, no intraday delay."""
        return 0
    
    @abstractmethod
    def get_block_deal(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get block deal transaction details.
        
        Args:
            symbol: Stock symbol (6-digit code). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized block deal data
        """
        pass
    
    @abstractmethod
    def get_block_deal_summary(
        self,
        start_date: str,
        end_date: str,
        group_by: str
    ) -> pd.DataFrame:
        """
        Get block deal summary statistics.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            group_by: Grouping dimension ('stock', 'date', or 'broker')
        
        Returns:
            pd.DataFrame: Summary statistics
        """
        pass
