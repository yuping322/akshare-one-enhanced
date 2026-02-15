"""
Example test demonstrating the testing framework.

This file shows how to use the testing utilities and fixtures.
"""

import pytest
import pandas as pd
import numpy as np
from tests.utils.contract_test import GoldenSampleValidator
from tests.utils.integration_helpers import DataFrameValidator, MockDataGenerator


class TestContractTestingExample:
    """Example of contract testing with golden samples."""
    
    def test_create_and_validate_golden_sample(self, tmp_path):
        """Example: Create and validate against golden sample."""
        # Create mock data
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'symbol': ['600000', '600000', '600000'],
            'close': [10.5, 11.0, 10.8],
            'volume': [1000000, 1200000, 1100000]
        })
        
        # Create validator with temporary directory
        validator = GoldenSampleValidator('example', samples_dir=tmp_path)
        
        # Save golden sample
        validator.save_golden_sample(
            'example_data',
            df,
            metadata={'description': 'Example data for testing'}
        )
        
        # Validate against golden sample
        validator.assert_schema_matches('example_data', df)
        
        # Test with different data (same schema)
        df2 = pd.DataFrame({
            'date': ['2024-01-04', '2024-01-05'],
            'symbol': ['600001', '600001'],
            'close': [20.5, 21.0],
            'volume': [2000000, 2200000]
        })
        
        # Should pass (same schema)
        validator.assert_schema_matches('example_data', df2)
    
    def test_schema_validation_detects_changes(self, tmp_path):
        """Example: Schema validation detects column changes."""
        # Create original data
        df_original = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000'],
            'close': [10.5]
        })
        
        validator = GoldenSampleValidator('example', samples_dir=tmp_path)
        validator.save_golden_sample('test_schema', df_original)
        
        # Create data with missing column
        df_missing = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000']
            # 'close' is missing
        })
        
        # Should detect missing column
        with pytest.raises(AssertionError, match="Missing columns"):
            validator.assert_schema_matches('test_schema', df_missing)
        
        # Create data with extra column
        df_extra = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000'],
            'close': [10.5],
            'extra_column': [100]
        })
        
        # Should detect extra column
        with pytest.raises(AssertionError, match="Extra columns"):
            validator.assert_schema_matches('test_schema', df_extra)


class TestDataFrameValidatorExample:
    """Example of DataFrame validation."""
    
    def test_validate_required_columns(self):
        """Example: Validate required columns."""
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000'],
            'close': [10.5]
        })
        
        validator = DataFrameValidator()
        
        # Should pass
        validator.validate_required_columns(df, ['date', 'symbol', 'close'])
        
        # Should fail
        with pytest.raises(AssertionError, match="Missing required columns"):
            validator.validate_required_columns(df, ['date', 'symbol', 'close', 'volume'])
    
    def test_validate_no_null_columns(self):
        """Example: Validate no null values."""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'symbol': ['600000', '600000'],
            'close': [10.5, None]
        })
        
        validator = DataFrameValidator()
        
        # Should pass for date and symbol
        validator.validate_no_null_columns(df, ['date', 'symbol'])
        
        # Should fail for close
        with pytest.raises(AssertionError, match="has .* null values"):
            validator.validate_no_null_columns(df, ['close'])
    
    def test_validate_date_range(self):
        """Example: Validate date range."""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-15', '2024-01-31']
        })
        
        validator = DataFrameValidator()
        
        # Should pass
        validator.validate_date_range(df, 'date', '2024-01-01', '2024-01-31')
        
        # Should fail (date outside range)
        df_outside = pd.DataFrame({
            'date': ['2024-01-01', '2024-02-01']
        })
        
        with pytest.raises(AssertionError, match="is after expected end"):
            validator.validate_date_range(df_outside, 'date', '2024-01-01', '2024-01-31')
    
    def test_validate_numeric_range(self):
        """Example: Validate numeric range."""
        df = pd.DataFrame({
            'price': [10.0, 20.0, 30.0]
        })
        
        validator = DataFrameValidator()
        
        # Should pass
        validator.validate_numeric_range(df, 'price', min_value=0, max_value=100)
        
        # Should fail (negative price)
        df_negative = pd.DataFrame({
            'price': [10.0, -5.0, 30.0]
        })
        
        with pytest.raises(AssertionError, match="values below"):
            validator.validate_numeric_range(df_negative, 'price', min_value=0)
    
    def test_validate_json_compatible(self):
        """Example: Validate JSON compatibility."""
        # Valid DataFrame
        df_valid = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'symbol': ['600000', '600000'],
            'close': [10.5, 11.0]
        })
        
        validator = DataFrameValidator()
        validator.validate_json_compatible(df_valid)
        
        # Invalid: contains NaN
        df_nan = pd.DataFrame({
            'close': [10.5, np.nan]
        })
        
        with pytest.raises(AssertionError, match="contains NaN"):
            validator.validate_json_compatible(df_nan)
        
        # Invalid: contains Infinity
        df_inf = pd.DataFrame({
            'close': [10.5, np.inf]
        })
        
        with pytest.raises(AssertionError, match="contains Infinity"):
            validator.validate_json_compatible(df_inf)


class TestMockDataGeneratorExample:
    """Example of mock data generation."""
    
    def test_generate_stock_symbols(self, mock_data_generator):
        """Example: Generate mock stock symbols."""
        symbols = mock_data_generator.generate_stock_symbols(count=5)
        
        assert len(symbols) == 5
        assert all(len(s) == 6 for s in symbols)
        assert all(s.isdigit() for s in symbols)
        assert symbols[0] == '600000'
        assert symbols[4] == '600004'
    
    def test_generate_date_range(self, mock_data_generator):
        """Example: Generate date range."""
        dates = mock_data_generator.generate_date_range('2024-01-01', '2024-01-05')
        
        assert len(dates) == 5
        assert dates[0] == '2024-01-01'
        assert dates[4] == '2024-01-05'
    
    def test_generate_mock_dataframe(self, mock_data_generator):
        """Example: Generate mock DataFrame."""
        df = mock_data_generator.generate_mock_dataframe(
            columns=['date', 'symbol', 'close', 'volume'],
            row_count=10,
            date_column='date',
            start_date='2024-01-01'
        )
        
        assert len(df) == 10
        assert list(df.columns) == ['date', 'symbol', 'close', 'volume']
        
        # Check date column
        assert df['date'].dtype == 'object'
        assert df['date'][0] == '2024-01-01'
        
        # Check symbol column
        assert all(len(s) == 6 for s in df['symbol'])
        
        # Check numeric columns
        assert df['close'].dtype == 'float64'
        assert df['volume'].dtype == 'int64'


class TestFixturesExample:
    """Example of using pytest fixtures."""
    
    def test_sample_symbols_fixture(self, sample_symbols):
        """Example: Use sample_symbols fixture."""
        assert len(sample_symbols) == 3
        assert '600000' in sample_symbols
        assert '000001' in sample_symbols
        assert '300001' in sample_symbols
    
    def test_sample_date_range_fixture(self, sample_date_range):
        """Example: Use sample_date_range fixture."""
        assert 'start_date' in sample_date_range
        assert 'end_date' in sample_date_range
        assert sample_date_range['start_date'] == '2024-01-01'
        assert sample_date_range['end_date'] == '2024-01-31'
    
    def test_multiple_fixtures(self, sample_symbols, sample_date_range, mock_data_generator):
        """Example: Use multiple fixtures together."""
        for symbol in sample_symbols:
            df = mock_data_generator.generate_mock_dataframe(
                columns=['date', 'symbol', 'close'],
                row_count=5,
                date_column='date',
                start_date=sample_date_range['start_date']
            )
            
            assert not df.empty
            assert 'date' in df.columns


@pytest.mark.integration
class TestIntegrationExample:
    """Example of integration tests (requires --run-integration flag)."""
    
    def test_integration_example(self, rate_limiter):
        """Example: Integration test with rate limiting."""
        # This test will be skipped unless --run-integration is specified
        
        # Rate limit to avoid overwhelming API
        rate_limiter.wait()
        
        # Simulate API call
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000'],
            'close': [10.5]
        })
        
        assert not df.empty


@pytest.mark.slow
class TestSlowExample:
    """Example of slow tests (requires --run-slow flag)."""
    
    def test_slow_example(self):
        """Example: Slow test."""
        # This test will be skipped unless --run-slow is specified
        import time
        time.sleep(0.1)  # Simulate slow operation
        assert True
