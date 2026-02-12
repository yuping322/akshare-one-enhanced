"""
Base provider class for equity pledge data.

This module defines the abstract interface for equity pledge data providers.
"""

from abc import abstractmethod
from typing import Optional
import pandas as pd

from ..base import BaseProvider


class EquityPledgeProvider(BaseProvider):
    """
    Abstract base class for equity pledge data providers.
    
    Defines the interface for fetching various types of equity pledge data:
    - Equity pledge data (shareholder pledge information)
    - Equity pledge ratio ranking (stocks ranked by pledge ratio)
    """
    
    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return 'pledge'
    
    def get_update_frequency(self) -> str:
        """Equity pledge data is updated irregularly."""
        return 'irregular'
    
    def get_delay_minutes(self) -> int:
        """Equity pledge data is updated irregularly, no fixed delay."""
        return 0
    
    @abstractmethod
    def get_equity_pledge(
        self,
        symbol: Optional[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get equity pledge data.
        
        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized equity pledge data
        """
        pass
    
    @abstractmethod
    def get_equity_pledge_ratio_rank(
        self,
        date: str,
        top_n: int
    ) -> pd.DataFrame:
        """
        Get equity pledge ratio ranking.
        
        Args:
            date: Query date (YYYY-MM-DD)
            top_n: Number of top stocks to return
        
        Returns:
            pd.DataFrame: Ranking data
        """
        pass
