"""
Integration tests for Northbound module.

These tests verify end-to-end functionality with real data sources.
Run with: pytest tests/test_northbound_integration.py -v -m integration
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks,
)
from tests.utils.integration_helpers import (
    DataFrameValidator,
    integration_rate_limiter,
    skip_if_no_network,
)


# ============================================================================
# Integration Tests - Real Data Fetching
# ============================================================================

@pytest.mark.integration
class TestNorthboundFlowIntegration:
    """Integration tests for northbound flow data."""
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_flow_all_market(self):
        """Test fetching northbound flow for all markets."""
        # Use recent date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        df = get_northbound_flow(start_date=start_date, end_date=end_date, market='all')
        
        # Validate structure
        validator = DataFrameValidator(df)
        validator.assert_not_empty()
        validator.assert_has_columns(['date', 'market', 'net_buy'])
        validator.assert_column_type('date', 'object')
        validator.assert_column_type('market', 'object')
        validator.assert_no_nan_in_column('date')
        validator.assert_no_nan_in_column('market')
        
        # Validate data
        assert all(df['market'] == 'all'), "All records should have market='all'"
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_flow_sh_market(self):
        """Test fetching northbound flow for Shanghai market."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        df = get_northbound_flow(start_date=start_date, end_date=end_date, market='sh')
        
        validator = DataFrameValidator(df)
        validator.assert_not_empty()
        validator.assert_has_columns(['date', 'market', 'net_buy'])
        
        # Validate market filter
        assert all(df['market'] == 'sh'), "All records should have market='sh'"
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_flow_sz_market(self):
        """Test fetching northbound flow for Shenzhen market."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        df = get_northbound_flow(start_date=start_date, end_date=end_date, market='sz')
        
        validator = DataFrameValidator(df)
        validator.assert_not_empty()
        validator.assert_has_columns(['date', 'market', 'net_buy'])
        
        # Validate market filter
        assert all(df['market'] == 'sz'), "All records should have market='sz'"


@pytest.mark.integration
class TestNorthboundHoldingsIntegration:
    """Integration tests for northbound holdings data."""
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_holdings_specific_stock(self):
        """Test fetching northbound holdings for a specific stock."""
        # Use a well-known stock with northbound holdings
        symbol = '600000'  # 浦发银行
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = get_northbound_holdings(symbol=symbol, start_date=start_date, end_date=end_date)
        
        # Validate structure
        validator = DataFrameValidator(df)
        validator.assert_has_columns(['date', 'symbol', 'holdings_shares'])
        
        # Validate symbol
        if not df.empty:
            assert all(df['symbol'] == symbol), f"All records should have symbol={symbol}"
            validator.assert_no_nan_in_column('symbol')
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_holdings_all_stocks(self):
        """Test fetching northbound holdings for all stocks."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        df = get_northbound_holdings(symbol=None, start_date=start_date, end_date=end_date)
        
        # Validate structure
        validator = DataFrameValidator(df)
        validator.assert_has_columns(['symbol', 'holdings_shares'])
        
        # Validate symbols are 6 digits
        if not df.empty and 'symbol' in df.columns:
            assert all(len(str(s)) == 6 for s in df['symbol']), "All symbols should be 6 digits"


@pytest.mark.integration
class TestNorthboundTopStocksIntegration:
    """Integration tests for northbound top stocks."""
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_top_stocks_all_market(self):
        """Test fetching top northbound stocks for all markets."""
        # Use a recent date
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        df = get_northbound_top_stocks(date=date, market='all', top_n=20)
        
        # Validate structure
        validator = DataFrameValidator(df)
        validator.assert_not_empty()
        validator.assert_has_columns(['rank', 'symbol', 'name'])
        validator.assert_no_nan_in_column('rank')
        validator.assert_no_nan_in_column('symbol')
        
        # Validate ranking
        assert df['rank'].iloc[0] == 1, "First rank should be 1"
        assert len(df) <= 20, "Should return at most 20 records"
        
        # Validate symbols are 6 digits
        assert all(len(str(s)) == 6 for s in df['symbol']), "All symbols should be 6 digits"
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_top_stocks_sh_market(self):
        """Test fetching top northbound stocks for Shanghai market."""
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        df = get_northbound_top_stocks(date=date, market='sh', top_n=10)
        
        validator = DataFrameValidator(df)
        validator.assert_not_empty()
        validator.assert_has_columns(['rank', 'symbol', 'name'])
        
        # Validate Shanghai stocks (start with 6)
        if not df.empty:
            assert all(str(s).startswith('6') for s in df['symbol']), "Shanghai stocks should start with 6"
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_get_northbound_top_stocks_sz_market(self):
        """Test fetching top northbound stocks for Shenzhen market."""
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        df = get_northbound_top_stocks(date=date, market='sz', top_n=10)
        
        validator = DataFrameValidator(df)
        validator.assert_not_empty()
        validator.assert_has_columns(['rank', 'symbol', 'name'])
        
        # Validate Shenzhen stocks (start with 0 or 3)
        if not df.empty:
            assert all(str(s).startswith(('0', '3')) for s in df['symbol']), "Shenzhen stocks should start with 0 or 3"


# ============================================================================
# Integration Tests - JSON Compatibility
# ============================================================================

@pytest.mark.integration
class TestJSONCompatibilityIntegration:
    """Test JSON compatibility with real data."""
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_northbound_flow_json_serializable(self):
        """Test that northbound flow data can be serialized to JSON."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        
        df = get_northbound_flow(start_date=start_date, end_date=end_date, market='all')
        
        # Should not raise
        json_str = df.to_json(orient='records')
        assert json_str is not None
        assert len(json_str) > 0
    
    @skip_if_no_network()
    @integration_rate_limiter
    def test_northbound_top_stocks_json_serializable(self):
        """Test that northbound top stocks data can be serialized to JSON."""
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        df = get_northbound_top_stocks(date=date, market='all', top_n=10)
        
        # Should not raise
        json_str = df.to_json(orient='records')
        assert json_str is not None
        assert len(json_str) > 0


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
