"""
Base provider class for all market data providers.

This module provides the foundation for implementing market data providers
with built-in JSON compatibility, parameter validation, and metadata support.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
import re

import pandas as pd
import numpy as np


class BaseProvider(ABC):
    """
    Abstract base class for all market data providers.
    
    Provides common functionality for:
    - Parameter validation (dates, symbols)
    - JSON compatibility (handling NaN/Infinity)
    - Metadata properties for data sources
    - Data standardization utilities
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the provider with configuration parameters.
        
        Args:
            **kwargs: Provider-specific configuration parameters
        """
        self.kwargs = kwargs
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Return metadata about the data source.
        
        Returns:
            dict: Metadata including source, data_type, update_frequency, delay_minutes
        """
        return {
            'source': self.get_source_name(),
            'data_type': self.get_data_type(),
            'update_frequency': self.get_update_frequency(),
            'delay_minutes': self.get_delay_minutes(),
        }
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of the data source (e.g., 'eastmoney', 'official')"""
        pass
    
    @abstractmethod
    def get_data_type(self) -> str:
        """Return the type of data (e.g., 'fundflow', 'disclosure', 'northbound')"""
        pass
    
    def get_update_frequency(self) -> str:
        """
        Return the update frequency of the data.
        
        Returns:
            str: One of 'realtime', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
        """
        return 'daily'
    
    def get_delay_minutes(self) -> int:
        """
        Return the data delay in minutes.
        
        Returns:
            int: Delay in minutes (0 for realtime)
        """
        return 0
    
    # Parameter Validation Methods
    
    @staticmethod
    def validate_symbol(symbol: str) -> None:
        """
        Validate stock symbol format.
        
        Args:
            symbol: Stock symbol (e.g., '600000', '000001')
            
        Raises:
            ValueError: If symbol format is invalid
        """
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        
        # Chinese A-share symbols are 6 digits
        if not re.match(r'^\d{6}$', symbol):
            raise ValueError(
                f"Invalid symbol format: {symbol}. "
                "Expected 6-digit stock code (e.g., '600000')"
            )
    
    @staticmethod
    def validate_date(date_str: str, param_name: str = "date") -> None:
        """
        Validate date format.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            param_name: Parameter name for error messages
            
        Raises:
            ValueError: If date format is invalid
        """
        if not date_str:
            raise ValueError(f"{param_name} cannot be empty")
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(
                f"Invalid {param_name} format: {date_str}. "
                f"Expected YYYY-MM-DD format. Error: {e}"
            ) from None
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> None:
        """
        Validate date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Raises:
            ValueError: If date range is invalid
        """
        BaseProvider.validate_date(start_date, "start_date")
        BaseProvider.validate_date(end_date, "end_date")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start > end:
            raise ValueError(
                f"start_date ({start_date}) must be <= end_date ({end_date})"
            )
    
    @staticmethod
    def validate_symbol_optional(symbol: Optional[str]) -> None:
        """
        Validate optional symbol parameter.
        
        Args:
            symbol: Stock symbol or None
            
        Raises:
            ValueError: If symbol format is invalid (when not None)
        """
        if symbol is not None:
            BaseProvider.validate_symbol(symbol)
    
    # JSON Compatibility Methods
    
    @staticmethod
    def ensure_json_compatible(df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure DataFrame is JSON-compatible by handling NaN/Infinity and data types.
        
        This method:
        1. Replaces NaN with None (JSON null)
        2. Replaces Infinity/-Infinity with None
        3. Converts datetime columns to string (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
        4. Ensures symbol columns are strings with leading zeros preserved
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: JSON-compatible DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # 1. Handle NaN and Infinity in numeric columns
        for col in df.select_dtypes(include=['float64', 'float32', 'float16']).columns:
            # Replace NaN with None
            df[col] = df[col].replace([np.nan], None)
            # Replace Infinity with None
            df[col] = df[col].replace([np.inf, -np.inf], None)
        
        # 2. Convert datetime columns to strings
        for col in df.select_dtypes(include=['datetime64']).columns:
            # Check if the datetime has non-zero time component
            has_time = (df[col].dt.hour != 0).any() or (df[col].dt.minute != 0).any() or (df[col].dt.second != 0).any()
            if has_time:
                # Has time component, use full format
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Date only, use date format
                df[col] = df[col].dt.strftime('%Y-%m-%d')
        
        # 3. Ensure symbol columns are strings with leading zeros
        symbol_columns = ['symbol', 'stock_code', 'code']
        for col in symbol_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.zfill(6)
        
        return df
    
    @staticmethod
    def replace_nan_with_none(value: Any) -> Any:
        """
        Replace NaN/Infinity values with None for JSON compatibility.
        
        Args:
            value: Any value that might be NaN or Infinity
            
        Returns:
            Original value or None if it was NaN/Infinity
        """
        if pd.isna(value):
            return None
        if isinstance(value, float) and (np.isinf(value) or np.isnan(value)):
            return None
        return value
    
    @staticmethod
    def create_empty_dataframe(columns: list) -> pd.DataFrame:
        """
        Create an empty DataFrame with specified columns.
        
        This is useful for returning consistent structure even when no data is available.
        
        Args:
            columns: List of column names
            
        Returns:
            pd.DataFrame: Empty DataFrame with specified columns
        """
        return pd.DataFrame(columns=columns)
    
    # Data Standardization Methods
    
    @staticmethod
    def standardize_symbol(symbol: str) -> str:
        """
        Standardize symbol format (ensure 6 digits with leading zeros).
        
        Args:
            symbol: Stock symbol
            
        Returns:
            str: Standardized symbol (6 digits)
        """
        return str(symbol).zfill(6)
    
    @staticmethod
    def standardize_date(date_value: Any) -> Optional[str]:
        """
        Standardize date to YYYY-MM-DD format.
        
        Args:
            date_value: Date value (string, datetime, or timestamp)
            
        Returns:
            str: Date in YYYY-MM-DD format, or None if invalid
        """
        if pd.isna(date_value):
            return None
        
        try:
            if isinstance(date_value, str):
                # Try to parse string date
                dt = pd.to_datetime(date_value)
            else:
                dt = pd.to_datetime(date_value)
            
            return dt.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def standardize_numeric(value: Any, default: Optional[float] = None) -> Optional[float]:
        """
        Standardize numeric value, handling NaN and Infinity.
        
        Args:
            value: Numeric value
            default: Default value to return if conversion fails
            
        Returns:
            float or None: Standardized numeric value
        """
        try:
            num_value = float(value)
            if np.isnan(num_value) or np.isinf(num_value):
                return default
            return num_value
        except (ValueError, TypeError):
            return default
    
    # Abstract Methods (to be implemented by subclasses)
    
    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from the data source.
        
        Returns:
            pd.DataFrame: Raw data from the source
        """
        pass
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize data format (field names, types, etc.).
        
        This method should be overridden by subclasses to implement
        specific standardization logic.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            pd.DataFrame: Standardized DataFrame
        """
        return self.ensure_json_compatible(df)
    
    def get_data(self) -> pd.DataFrame:
        """
        Main method to fetch and standardize data.
        
        This method orchestrates the data fetching and standardization process:
        1. Fetch raw data
        2. Standardize data format
        3. Ensure JSON compatibility
        
        Returns:
            pd.DataFrame: Standardized, JSON-compatible data
        """
        raw_df = self.fetch_data()
        standardized_df = self.standardize_data(raw_df)
        return self.ensure_json_compatible(standardized_df)
