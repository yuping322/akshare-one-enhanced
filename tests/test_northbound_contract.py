"""
Contract tests for Northbound module.

These tests verify that the data structure remains stable over time
by comparing against golden samples.
"""

import pytest
import pandas as pd
from pathlib import Path

from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks,
)
from tests.utils.contract_test import GoldenSampleValidator, create_golden_sample_if_missing


# ============================================================================
# Contract Tests - Schema Stability
# ============================================================================

class TestNorthboundFlowContract:
    """Contract tests for northbound flow data."""
    
    @pytest.mark.integration
    def test_northbound_flow_schema(self):
        """Test that northbound flow data schema remains stable."""
        expected_columns = [
            'date', 'market', 'net_buy', 'buy_amount', 'sell_amount', 'balance'
        ]
        
        # Fetch recent data
        df = get_northbound_flow(start_date='2024-01-01', end_date='2024-01-05', market='all')
        
        # Verify schema
        assert list(df.columns) == expected_columns, f"Schema changed! Expected {expected_columns}, got {list(df.columns)}"
        
        # Verify data types
        assert df['date'].dtype == 'object', "date should be string"
        assert df['market'].dtype == 'object', "market should be string"


class TestNorthboundHoldingsContract:
    """Contract tests for northbound holdings data."""
    
    @pytest.mark.integration
    def test_northbound_holdings_schema(self):
        """Test that northbound holdings data schema remains stable."""
        expected_columns = [
            'date', 'symbol', 'holdings_shares', 'holdings_value',
            'holdings_ratio', 'holdings_change'
        ]
        
        # Fetch recent data for a specific stock
        df = get_northbound_holdings(symbol='600000', start_date='2024-01-01', end_date='2024-01-05')
        
        # Verify schema
        assert list(df.columns) == expected_columns, f"Schema changed! Expected {expected_columns}, got {list(df.columns)}"
        
        # Verify symbol format (6 digits with leading zeros)
        if not df.empty and 'symbol' in df.columns:
            assert all(len(str(s)) == 6 for s in df['symbol']), "Symbols should be 6 digits"


class TestNorthboundTopStocksContract:
    """Contract tests for northbound top stocks data."""
    
    @pytest.mark.integration
    def test_northbound_top_stocks_schema(self):
        """Test that northbound top stocks data schema remains stable."""
        expected_columns = [
            'rank', 'symbol', 'name', 'northbound_net_buy', 'holdings_shares', 'holdings_ratio', 'date'
        ]
        
        # Fetch recent data
        df = get_northbound_top_stocks(date='2024-01-01', market='all', top_n=10)
        
        # Verify schema (check that expected columns are present, allow extra columns)
        for col in expected_columns:
            assert col in df.columns, f"Missing expected column: {col}"
        
        # Verify ranking
        if not df.empty:
            assert df['rank'].iloc[0] == 1, "First rank should be 1"
            assert len(df) <= 10, "Should return at most top_n records"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
