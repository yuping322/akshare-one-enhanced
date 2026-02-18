"""
Integration tests for block deal data module.

These tests make real API calls to verify the module works end-to-end.
"""

import pandas as pd
import pytest

from akshare_one.modules.blockdeal import (
    get_block_deal,
    get_block_deal_summary,
)


@pytest.mark.integration
class TestBlockDealIntegration:
    """Integration tests for block deal data module."""
    
    def test_get_block_deal_single_stock_integration(self):
        """Test getting real block deal data for a single stock."""
        df = get_block_deal('600000', start_date='2024-01-01', end_date='2024-12-31')
        
        # Verify structure
        assert isinstance(df, pd.DataFrame)
        assert 'date' in df.columns
        assert 'symbol' in df.columns
        assert 'price' in df.columns
        assert 'volume' in df.columns
        assert 'amount' in df.columns
        
        # Verify data types if not empty
        if not df.empty:
            assert df['date'].dtype in ['object', 'string']
            assert df['symbol'].dtype in ['object', 'string']
            assert df['price'].dtype in ['float64', 'float32']
    
    def test_get_block_deal_all_stocks_integration(self):
        """Test getting real block deal data for all stocks."""
        df = get_block_deal(None, start_date='2024-01-01', end_date='2024-01-31')
        
        assert isinstance(df, pd.DataFrame)
        assert 'symbol' in df.columns
        assert 'amount' in df.columns
    
    def test_get_block_deal_summary_integration(self):
        """Test getting real block deal summary."""
        df = get_block_deal_summary(
            start_date='2024-01-01',
            end_date='2024-01-31',
            group_by='stock'
        )
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert 'symbol' in df.columns
            assert 'deal_count' in df.columns
            assert 'total_amount' in df.columns
