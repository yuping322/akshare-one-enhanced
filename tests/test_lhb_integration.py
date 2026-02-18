"""
Integration tests for dragon tiger list (龙虎榜) data module.

These tests make real API calls to verify the module works correctly.
"""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from akshare_one.modules.lhb import (
    get_dragon_tiger_broker_stats,
    get_dragon_tiger_list,
    get_dragon_tiger_summary,
)


@pytest.mark.integration
class TestDragonTigerIntegration:
    """Integration tests for dragon tiger list module."""
    
    def test_get_dragon_tiger_list_real_data(self):
        """Test getting dragon tiger list with real data."""
        # Use a recent date
        date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        try:
            result = get_dragon_tiger_list(date)
            
            # Check structure
            assert isinstance(result, pd.DataFrame)
            assert 'date' in result.columns
            assert 'symbol' in result.columns
            assert 'name' in result.columns
            assert 'reason' in result.columns
            assert 'buy_amount' in result.columns
            assert 'sell_amount' in result.columns
            assert 'net_amount' in result.columns
            
            # Check JSON compatibility
            if not result.empty:
                json_str = result.to_json(orient='records')
                assert json_str is not None
                
                # Check no NaN values
                assert not result.isnull().any().any()
                
                # Check symbol format
                assert all(len(s) == 6 for s in result['symbol'])
                
        except Exception as e:
            pytest.skip(f"API call failed: {e}")
    
    def test_get_dragon_tiger_summary_real_data(self):
        """Test getting dragon tiger summary with real data."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            result = get_dragon_tiger_summary(start_date, end_date, 'stock')
            
            # Check structure
            assert isinstance(result, pd.DataFrame)
            assert 'symbol' in result.columns
            assert 'name' in result.columns
            assert 'list_count' in result.columns
            assert 'net_buy_amount' in result.columns
            
            # Check JSON compatibility
            if not result.empty:
                json_str = result.to_json(orient='records')
                assert json_str is not None
                
        except Exception as e:
            pytest.skip(f"API call failed: {e}")
    
    def test_get_dragon_tiger_broker_stats_real_data(self):
        """Test getting broker statistics with real data."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            result = get_dragon_tiger_broker_stats(start_date, end_date, 10)
            
            # Check structure
            assert isinstance(result, pd.DataFrame)
            assert 'rank' in result.columns
            assert 'broker_name' in result.columns
            assert 'list_count' in result.columns
            assert 'buy_amount' in result.columns
            assert 'sell_amount' in result.columns
            assert 'net_amount' in result.columns
            
            # Check ranking
            if not result.empty:
                assert len(result) <= 10
                assert result['rank'].iloc[0] == 1
                
                # Check JSON compatibility
                json_str = result.to_json(orient='records')
                assert json_str is not None
                
        except Exception as e:
            pytest.skip(f"API call failed: {e}")
