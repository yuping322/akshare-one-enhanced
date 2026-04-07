"""
Test block deal module using mock fixtures - no network required.

This demonstrates offline testing for block deal data.
"""

import pandas as pd
import pytest

from akshare_one.modules.blockdeal import get_block_deal


class TestBlockDealWithMocks:
    """Test block deal data with mocked API responses."""

    def test_get_block_deal_single_stock_mocked(self, mock_block_deal_api):
        """
        Test getting block deal data for a single stock using mock data.
        """
        df = get_block_deal(
            symbol='600000',
            start_date='2024-01-15',
            end_date='2024-01-17'
        )

        # Verify structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'date' in df.columns
        assert 'symbol' in df.columns
        assert 'price' in df.columns
        assert 'volume' in df.columns

        # Verify data types
        assert df['date'].dtype == 'object'
        assert df['price'].dtype in ['float64', 'float32']

    def test_get_block_deal_data_validation(self, mock_block_deal_api):
        """
        Test data validation for block deal data.
        """
        df = get_block_deal(
            symbol='600000',
            start_date='2024-01-15',
            end_date='2024-01-17'
        )

        # Check price is positive
        if not df.empty and 'price' in df.columns:
            assert all(df['price'] > 0)

        # Check volume is positive
        if not df.empty and 'volume' in df.columns:
            assert all(df['volume'] > 0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])