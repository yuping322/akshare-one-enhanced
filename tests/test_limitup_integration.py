"""
Integration tests for limit up/down (涨停池) data module.

These tests make real API calls and are skipped by default.
Run with: pytest tests/test_limitup_integration.py --run-integration
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from akshare_one.modules.limitup import (
    get_limit_up_pool,
    get_limit_down_pool,
    get_limit_up_stats,
)


@pytest.mark.integration
class TestLimitUpDownIntegration:
    """Integration tests with real API calls."""
    
    def test_get_limit_up_pool_real(self):
        """Test getting real limit up pool data."""
        # Use a recent date
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = get_limit_up_pool(date)
        
        # Should return a DataFrame (may be empty if no limit ups)
        assert isinstance(result, pd.DataFrame)
        
        # Check columns exist
        expected_columns = [
            'date', 'symbol', 'name', 'close_price', 'limit_up_time',
            'open_count', 'seal_amount', 'consecutive_days', 'reason', 'turnover_rate'
        ]
        for col in expected_columns:
            assert col in result.columns
        
        # If data exists, validate format
        if not result.empty:
            # Check date format
            assert result['date'].iloc[0] == date
            
            # Check symbol format (6 digits)
            assert len(result['symbol'].iloc[0]) == 6
            assert result['symbol'].iloc[0].isdigit()
            
            # Check numeric columns
            assert result['close_price'].dtype in ['float64', 'float32']
            assert result['open_count'].dtype in ['int64', 'int32']
            assert result['turnover_rate'].dtype in ['float64', 'float32']
    
    def test_get_limit_down_pool_real(self):
        """Test getting real limit down pool data."""
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = get_limit_down_pool(date)
        
        assert isinstance(result, pd.DataFrame)
        
        expected_columns = [
            'date', 'symbol', 'name', 'close_price', 'limit_down_time',
            'open_count', 'turnover_rate'
        ]
        for col in expected_columns:
            assert col in result.columns
        
        if not result.empty:
            assert result['date'].iloc[0] == date
            assert len(result['symbol'].iloc[0]) == 6
    
    def test_get_limit_up_stats_real(self):
        """Test getting real limit up/down statistics."""
        end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        
        result = get_limit_up_stats(start_date, end_date)
        
        assert isinstance(result, pd.DataFrame)
        
        expected_columns = [
            'date', 'limit_up_count', 'limit_down_count', 'broken_rate'
        ]
        for col in expected_columns:
            assert col in result.columns
        
        if not result.empty:
            # Check data types
            assert result['limit_up_count'].dtype in ['int64', 'int32']
            assert result['limit_down_count'].dtype in ['int64', 'int32']
            assert result['broken_rate'].dtype in ['float64', 'float32']
            
            # Check broken_rate is percentage (0-100)
            assert (result['broken_rate'] >= 0).all()
            assert (result['broken_rate'] <= 100).all()
    
    def test_json_serialization_real(self):
        """Test JSON serialization with real data."""
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = get_limit_up_pool(date)
        
        # Should be able to serialize to JSON
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Should not contain NaN
        if not result.empty:
            assert not result.isnull().any().any()
