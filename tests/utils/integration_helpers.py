"""
Integration test helpers for market data modules.

Provides utilities for:
- Real API testing with rate limiting
- Test data validation
- Common test fixtures
- Mock data generation
"""

import time
from typing import Any, Callable, Dict, List, Optional
import pandas as pd
import pytest
from functools import wraps


class RateLimiter:
    """Rate limiter for API calls during testing."""
    
    def __init__(self, calls_per_second: float = 1.0):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum number of calls per second
        """
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0.0
    
    def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_interval:
            time.sleep(self.min_interval - time_since_last_call)
        
        self.last_call_time = time.time()
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply rate limiting to a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper


# Global rate limiter for integration tests (1 call per second)
integration_rate_limiter = RateLimiter(calls_per_second=1.0)


def skip_if_no_network():
    """Pytest marker to skip tests if network is unavailable."""
    import socket
    
    def check_network():
        try:
            # Try to connect to a reliable host
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    return pytest.mark.skipif(
        not check_network(),
        reason="Network unavailable"
    )


def skip_if_rate_limited():
    """Pytest marker to skip tests if rate limited."""
    return pytest.mark.skipif(
        False,  # TODO: Implement rate limit detection
        reason="Rate limited by upstream API"
    )


class DataFrameValidator:
    """Validator for DataFrame structure and content."""
    
    @staticmethod
    def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
        """
        Validate DataFrame has required columns.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            
        Raises:
            AssertionError: If required columns are missing
        """
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise AssertionError(f"Missing required columns: {missing}")
    
    @staticmethod
    def validate_no_null_columns(df: pd.DataFrame, columns: List[str]) -> None:
        """
        Validate specified columns have no null values.
        
        Args:
            df: DataFrame to validate
            columns: List of column names that should not have nulls
            
        Raises:
            AssertionError: If null values found
        """
        for col in columns:
            if col in df.columns and df[col].isnull().any():
                null_count = df[col].isnull().sum()
                raise AssertionError(
                    f"Column '{col}' has {null_count} null values"
                )
    
    @staticmethod
    def validate_date_range(
        df: pd.DataFrame,
        date_column: str,
        start_date: str,
        end_date: str
    ) -> None:
        """
        Validate dates are within expected range.
        
        Args:
            df: DataFrame to validate
            date_column: Name of date column
            start_date: Expected start date (YYYY-MM-DD)
            end_date: Expected end date (YYYY-MM-DD)
            
        Raises:
            AssertionError: If dates are outside range
        """
        if df.empty:
            return
        
        dates = pd.to_datetime(df[date_column])
        min_date = dates.min()
        max_date = dates.max()
        
        expected_start = pd.to_datetime(start_date)
        expected_end = pd.to_datetime(end_date)
        
        if min_date < expected_start:
            raise AssertionError(
                f"Minimum date {min_date} is before expected start {expected_start}"
            )
        
        if max_date > expected_end:
            raise AssertionError(
                f"Maximum date {max_date} is after expected end {expected_end}"
            )
    
    @staticmethod
    def validate_numeric_range(
        df: pd.DataFrame,
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> None:
        """
        Validate numeric column values are within range.
        
        Args:
            df: DataFrame to validate
            column: Column name
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            
        Raises:
            AssertionError: If values are outside range
        """
        if column not in df.columns:
            return
        
        # Filter out None values
        values = df[column].dropna()
        
        if min_value is not None:
            below_min = values[values < min_value]
            if not below_min.empty:
                raise AssertionError(
                    f"Column '{column}' has {len(below_min)} values below {min_value}"
                )
        
        if max_value is not None:
            above_max = values[values > max_value]
            if not above_max.empty:
                raise AssertionError(
                    f"Column '{column}' has {len(above_max)} values above {max_value}"
                )
    
    @staticmethod
    def validate_json_compatible(df: pd.DataFrame) -> None:
        """
        Validate DataFrame is JSON compatible.
        
        Args:
            df: DataFrame to validate
            
        Raises:
            AssertionError: If DataFrame is not JSON compatible
        """
        import numpy as np
        
        # Check for NaN/Infinity in numeric columns
        for col in df.select_dtypes(include=['float64', 'float32']).columns:
            if df[col].isna().any():
                raise AssertionError(f"Column '{col}' contains NaN values")
            
            if np.isinf(df[col]).any():
                raise AssertionError(f"Column '{col}' contains Infinity values")
        
        # Check for datetime columns
        for col in df.select_dtypes(include=['datetime64']).columns:
            raise AssertionError(
                f"Column '{col}' is datetime type, should be string (YYYY-MM-DD)"
            )
        
        # Try JSON serialization
        try:
            df.to_json(orient='records')
        except Exception as e:
            raise AssertionError(f"DataFrame cannot be serialized to JSON: {e}")


class MockDataGenerator:
    """Generator for mock test data."""
    
    @staticmethod
    def generate_stock_symbols(count: int = 10) -> List[str]:
        """
        Generate mock stock symbols.
        
        Args:
            count: Number of symbols to generate
            
        Returns:
            List of 6-digit stock symbols
        """
        symbols = []
        for i in range(count):
            # Generate symbols starting from 600000
            symbol = f"{600000 + i:06d}"
            symbols.append(symbol)
        return symbols
    
    @staticmethod
    def generate_date_range(start_date: str, end_date: str) -> List[str]:
        """
        Generate list of dates in range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of date strings
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        return [d.strftime('%Y-%m-%d') for d in dates]
    
    @staticmethod
    def generate_mock_dataframe(
        columns: List[str],
        row_count: int = 10,
        date_column: Optional[str] = None,
        start_date: str = '2024-01-01'
    ) -> pd.DataFrame:
        """
        Generate mock DataFrame with specified structure.
        
        Args:
            columns: List of column names
            row_count: Number of rows to generate
            date_column: Name of date column (if any)
            start_date: Start date for date column
            
        Returns:
            Mock DataFrame
        """
        import numpy as np
        
        data = {}
        
        for col in columns:
            if col == date_column:
                # Generate date sequence
                dates = pd.date_range(start=start_date, periods=row_count, freq='D')
                data[col] = [d.strftime('%Y-%m-%d') for d in dates]
            elif 'symbol' in col.lower():
                # Generate stock symbols
                data[col] = [f"{600000 + i:06d}" for i in range(row_count)]
            elif 'price' in col.lower() or 'close' in col.lower():
                # Generate prices (10-100)
                data[col] = np.random.uniform(10, 100, row_count)
            elif 'volume' in col.lower():
                # Generate volumes (1000-100000)
                data[col] = np.random.randint(1000, 100000, row_count)
            elif 'pct' in col.lower() or 'rate' in col.lower():
                # Generate percentages (-10 to 10)
                data[col] = np.random.uniform(-10, 10, row_count)
            else:
                # Generate random floats
                data[col] = np.random.uniform(0, 100, row_count)
        
        return pd.DataFrame(data)


# Pytest fixtures
@pytest.fixture
def rate_limiter():
    """Fixture providing rate limiter for integration tests."""
    return integration_rate_limiter


@pytest.fixture
def df_validator():
    """Fixture providing DataFrame validator."""
    return DataFrameValidator()


@pytest.fixture
def mock_data_generator():
    """Fixture providing mock data generator."""
    return MockDataGenerator()


@pytest.fixture
def sample_symbols():
    """Fixture providing sample stock symbols for testing."""
    return ['600000', '000001', '300001']


@pytest.fixture
def sample_date_range():
    """Fixture providing sample date range for testing."""
    return {
        'start_date': '2024-01-01',
        'end_date': '2024-01-31'
    }


# Example usage in tests:
"""
from tests.utils.integration_helpers import (
    skip_if_no_network,
    DataFrameValidator,
    integration_rate_limiter
)

@skip_if_no_network()
def test_real_api_call(rate_limiter):
    '''Test with real API call.'''
    from akshare_one.modules.fundflow import get_stock_fund_flow
    
    # Rate limit to avoid overwhelming API
    rate_limiter.wait()
    
    df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-31')
    
    # Validate result
    validator = DataFrameValidator()
    validator.validate_required_columns(df, ['date', 'symbol', 'close'])
    validator.validate_json_compatible(df)

def test_with_mock_data(mock_data_generator):
    '''Test with mock data.'''
    df = mock_data_generator.generate_mock_dataframe(
        columns=['date', 'symbol', 'close', 'volume'],
        row_count=20,
        date_column='date'
    )
    
    assert len(df) == 20
    assert 'date' in df.columns
"""
