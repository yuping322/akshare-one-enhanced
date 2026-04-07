"""
Test northbound module using mock fixtures - no network required.

This demonstrates how to write tests that run offline using mock data.
"""

import pandas as pd
import pytest

from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks,
)


class TestNorthboundFlowWithMocks:
    """Test northbound flow data with mocked API responses."""

    def test_get_northbound_flow_all_market_mocked(self, mock_northbound_flow_api):
        """
        Test fetching northbound flow for all markets using mock data.

        This test runs without network access.
        """
        df = get_northbound_flow(
            start_date='2024-01-15',
            end_date='2024-01-17',
            market='all'
        )

        # Verify the mock was called
        mock_northbound_flow_api.assert_called_once()

        # Verify structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'date' in df.columns
        assert 'market' in df.columns
        assert 'net_buy' in df.columns

        # Verify data types
        # Note: Pandas 3.0+ uses StringDtype instead of object for strings
        assert pd.api.types.is_string_dtype(df['date'])
        assert pd.api.types.is_string_dtype(df['market'])

        # Verify all records have market='all'
        assert all(df['market'] == 'all')

        # Verify date range filtering
        assert all(df['date'] >= '2024-01-15')
        assert all(df['date'] <= '2024-01-17')

    def test_get_northbound_flow_data_conversion(self, mock_northbound_flow_api):
        """
        Test that data conversion from Chinese columns works correctly.

        Mock data has '当日成交净买额' in 亿元, should convert to 元.
        """
        df = get_northbound_flow(
            start_date='2024-01-15',
            end_date='2024-01-17',
            market='all'
        )

        # Check conversion: mock data has 50.25 亿元, should be 5025000000 元
        if not df.empty:
            expected_value = 50.25 * 100000000  # Convert from 亿元 to 元
            actual_value = df['net_buy'].iloc[0]
            # Allow small floating point difference
            assert abs(actual_value - expected_value) < 1

    def test_get_northbound_flow_empty_response(self, empty_dataframe_mock):
        """
        Test handling of empty DataFrame response.

        Verifies graceful handling when API returns no data.
        """
        df = get_northbound_flow(
            start_date='2024-01-01',
            end_date='2024-01-31',
            market='all'
        )

        # Should return empty DataFrame with expected columns
        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert 'date' in df.columns
        assert 'market' in df.columns


class TestNorthboundHoldingsWithMocks:
    """Test northbound holdings data with mocked API responses."""

    def test_get_northbound_holdings_specific_stock_mocked(
        self, mock_northbound_holdings_individual_api
    ):
        """
        Test fetching northbound holdings for a specific stock using mock data.
        """
        symbol = '600000'
        df = get_northbound_holdings(
            symbol=symbol,
            start_date='2024-01-15',
            end_date='2024-01-17'
        )

        # Verify the mock was called with correct symbol
        mock_northbound_holdings_individual_api.assert_called_once()

        # Verify structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'date' in df.columns
        assert 'symbol' in df.columns
        assert 'holdings_shares' in df.columns

        # Verify symbol is set correctly
        assert all(df['symbol'] == symbol)

        # Verify holdings_shares are numeric
        assert df['holdings_shares'].dtype in ['float64', 'int64']

    def test_get_northbound_holdings_all_stocks_mocked(
        self, mock_northbound_holdings_all_api
    ):
        """
        Test fetching northbound holdings for all stocks using mock data.
        """
        df = get_northbound_holdings(
            symbol=None,
            start_date='2024-01-01',
            end_date='2024-01-31'
        )

        # Verify structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'symbol' in df.columns
        assert 'holdings_shares' in df.columns

        # Verify multiple stocks are present
        assert len(df) > 1

        # Verify symbols are 6-digit strings
        assert all(len(str(s)) == 6 for s in df['symbol'])


class TestNorthboundTopStocksWithMocks:
    """Test northbound top stocks with mocked API responses."""

    def test_get_northbound_top_stocks_mocked(self, mock_northbound_top_stocks_api):
        """
        Test fetching top northbound stocks using mock data.
        """
        df = get_northbound_top_stocks(
            date='2024-01-17',
            market='all',
            top_n=10
        )

        # Verify structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'rank' in df.columns
        assert 'symbol' in df.columns
        assert 'name' in df.columns

        # Verify ranking starts at 1
        assert df['rank'].iloc[0] == 1

        # Verify symbols are 6-digit
        assert all(len(str(s)) == 6 for s in df['symbol'])

        # Verify limited to top_n
        assert len(df) <= 10

    def test_get_northbound_top_stocks_market_filter_sh(
        self, mock_northbound_top_stocks_api
    ):
        """
        Test filtering top stocks by Shanghai market.

        Shanghai stocks should start with '6'.
        """
        df = get_northbound_top_stocks(
            date='2024-01-17',
            market='sh',
            top_n=5
        )

        # Verify Shanghai stocks (start with 6)
        if not df.empty:
            assert all(str(s).startswith('6') for s in df['symbol'])


class TestNorthboundJSONCompatibility:
    """Test JSON serialization of mocked responses."""

    def test_northbound_flow_json_serializable_mocked(self, mock_northbound_flow_api):
        """
        Test that northbound flow data can be serialized to JSON.

        This ensures the standardized data format is JSON-compatible.
        """
        df = get_northbound_flow(
            start_date='2024-01-15',
            end_date='2024-01-17',
            market='all'
        )

        # Should not raise
        json_str = df.to_json(orient='records')
        assert json_str is not None
        assert len(json_str) > 0

        # Verify we can deserialize
        import json
        records = json.loads(json_str)
        assert isinstance(records, list)
        assert len(records) == len(df)

    def test_northbound_top_stocks_json_serializable_mocked(
        self, mock_northbound_top_stocks_api
    ):
        """
        Test that northbound top stocks data can be serialized to JSON.
        """
        df = get_northbound_top_stocks(
            date='2024-01-17',
            market='all',
            top_n=10
        )

        # Should not raise
        json_str = df.to_json(orient='records')
        assert json_str is not None
        assert len(json_str) > 0


class TestNorthboundErrorHandling:
    """Test error handling with mocked API errors."""

    def test_api_connection_error_handling(self, api_error_mock):
        """
        Test handling of API connection errors.

        Should return empty DataFrame instead of raising exception.
        """
        df = get_northbound_flow(
            start_date='2024-01-01',
            end_date='2024-01-31',
            market='all'
        )

        # Should return empty DataFrame with expected columns
        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert 'date' in df.columns


class TestNorthboundWithCustomMock:
    """Test using custom mock data."""

    def test_with_custom_mock_data(self, mock_api_response, mocker):
        """
        Test with custom mock data using MockAPIResponse helper.

        Demonstrates how to create custom test scenarios.
        """
        import pandas as pd

        # Create custom test data
        custom_data = pd.DataFrame({
            "日期": ["2024-02-01", "2024-02-02"],
            "当日成交净买额": [100.5, 200.8],
            "买入成交额": [300.0, 400.0],
            "卖出成交额": [199.5, 199.2],
            "当日余额": [1000.0, 1000.0],
        })

        # Setup custom mock
        mock_api_response.add_data('stock_hsgt_hist_em', custom_data)
        mocks = mock_api_response.apply_mocks(mocker)

        # Test with custom data
        df = get_northbound_flow(
            start_date='2024-02-01',
            end_date='2024-02-02',
            market='all'
        )

        # Verify custom data was used
        assert len(df) == 2
        assert 'date' in df.columns
        assert df['date'].iloc[0] == '2024-02-01'


# Demonstrate that tests can run without network
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])