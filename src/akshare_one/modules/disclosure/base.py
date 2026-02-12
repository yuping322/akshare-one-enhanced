"""
Base provider class for disclosure news data.

This module defines the abstract interface for disclosure news data providers.
"""

from abc import abstractmethod
from typing import Optional
import pandas as pd

from ..base import BaseProvider


class DisclosureProvider(BaseProvider):
    """
    Abstract base class for disclosure news data providers.
    
    Defines the interface for fetching various types of disclosure data:
    - General disclosure news
    - Dividend data
    - Repurchase data
    - ST/Delist risk data
    
    Provides common data standardization methods for disclosure-specific data.
    """
    
    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return 'disclosure'
    
    def get_update_frequency(self) -> str:
        """Disclosure data is updated in realtime."""
        return 'realtime'
    
    def get_delay_minutes(self) -> int:
        """Disclosure data has minimal delay (typically < 1 hour)."""
        return 60
    
    # Data Standardization Methods for Disclosure Data
    
    @staticmethod
    def standardize_category(category: str) -> str:
        """
        Standardize disclosure category names.
        
        Args:
            category: Raw category name
            
        Returns:
            str: Standardized category ('all', 'dividend', 'repurchase', 'st', 'major_event')
        """
        category_lower = str(category).lower().strip()
        
        # Map common variations to standard categories
        category_map = {
            '分红': 'dividend',
            '派息': 'dividend',
            '红利': 'dividend',
            'dividend': 'dividend',
            '回购': 'repurchase',
            '股份回购': 'repurchase',
            'repurchase': 'repurchase',
            'buyback': 'repurchase',
            'st': 'st',
            '退市': 'st',
            '风险': 'st',
            'delist': 'st',
            '重大事项': 'major_event',
            '重大公告': 'major_event',
            'major': 'major_event',
            '全部': 'all',
            'all': 'all',
        }
        
        return category_map.get(category_lower, 'all')
    
    @staticmethod
    def standardize_dividend_ratio(dividend_per_share: Optional[float], 
                                   price: Optional[float]) -> Optional[float]:
        """
        Calculate dividend ratio (dividend yield).
        
        Args:
            dividend_per_share: Dividend per share
            price: Stock price
            
        Returns:
            float or None: Dividend ratio as percentage, or None if calculation not possible
        """
        if dividend_per_share is None or price is None or price == 0:
            return None
        
        try:
            ratio = (float(dividend_per_share) / float(price)) * 100
            return round(ratio, 4)
        except (ValueError, TypeError, ZeroDivisionError):
            return None
    
    @staticmethod
    def standardize_repurchase_progress(progress_text: str) -> str:
        """
        Standardize repurchase progress status.
        
        Args:
            progress_text: Raw progress text
            
        Returns:
            str: Standardized progress ('planned', 'in_progress', 'completed', 'cancelled')
        """
        progress_lower = str(progress_text).lower().strip()
        
        # Map common variations to standard statuses
        if any(keyword in progress_lower for keyword in ['计划', 'plan', '拟']):
            return 'planned'
        elif any(keyword in progress_lower for keyword in ['进行', 'progress', '实施']):
            return 'in_progress'
        elif any(keyword in progress_lower for keyword in ['完成', 'complete', '结束']):
            return 'completed'
        elif any(keyword in progress_lower for keyword in ['取消', 'cancel', '终止']):
            return 'cancelled'
        else:
            return 'unknown'
    
    @staticmethod
    def standardize_st_type(st_text: str) -> str:
        """
        Standardize ST type classification.
        
        Args:
            st_text: Raw ST type text
            
        Returns:
            str: Standardized ST type ('ST', '*ST', 'SST', 'S*ST', 'normal')
        """
        st_upper = str(st_text).upper().strip()
        
        # Check for specific ST types
        if 'S*ST' in st_upper:
            return 'S*ST'
        elif '*ST' in st_upper:
            return '*ST'
        elif 'SST' in st_upper:
            return 'SST'
        elif 'ST' in st_upper:
            return 'ST'
        else:
            return 'normal'
    
    @staticmethod
    def standardize_risk_level(risk_text: str) -> str:
        """
        Standardize risk level classification.
        
        Args:
            risk_text: Raw risk level text
            
        Returns:
            str: Standardized risk level ('low', 'medium', 'high', 'critical')
        """
        risk_lower = str(risk_text).lower().strip()
        
        # Map risk indicators to levels (check in priority order)
        if any(keyword in risk_lower for keyword in ['退市', 'delist', '终止', 'critical', '严重']):
            return 'critical'
        elif any(keyword in risk_lower for keyword in ['*st', 's*st', 'high', '高']):
            return 'high'
        elif any(keyword in risk_lower for keyword in ['sst', 'medium', '中']) or 'st' in risk_lower:
            return 'medium'
        else:
            return 'low'
    
    @abstractmethod
    def get_disclosure_news(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        category: str
    ) -> pd.DataFrame:
        """
        Get disclosure news data.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            category: News category ('all', 'dividend', 'repurchase', 'st', 'major_event')
        
        Returns:
            pd.DataFrame: Standardized disclosure news data
        """
        pass
    
    @abstractmethod
    def get_dividend_data(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get dividend data.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized dividend data
        """
        pass
    
    @abstractmethod
    def get_repurchase_data(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Get stock repurchase data.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Standardized repurchase data
        """
        pass
    
    @abstractmethod
    def get_st_delist_data(self, symbol: str | None) -> pd.DataFrame:
        """
        Get ST/delist risk data.
        
        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
        
        Returns:
            pd.DataFrame: Standardized ST/delist risk data
        """
        pass
