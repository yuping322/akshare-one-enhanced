"""
Test to verify the integration testing helpers work correctly.
"""

import pytest
import pandas as pd
import numpy as np
from tests.utils.integration_helpers import DataFrameValidator, MockDataGenerator


class TestDataFrameValidator:
    """Test the DataFrameValidator utility."""
    
    def test_validate_required_columns_success(self):
        """Test validating required columns succeeds."""
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000'],
            'close': [10.5]
        })
        
        validator = DataFrameValidator()
        validator.validate_required_columns(df, ['date', 'symbol', 'close'])
    
    def test_validate_required_columns_failure(self):
        """Test validating required columns detects missing columns."""
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000']
        })
        
        validator = DataFrameValidator()
        with pytest.raises(AssertionError, match="Missing required columns"):
            validator.validate_required_columns(df, ['date', 'symbol', 'close'])
    
    def test_validate_no_null_columns_success(self):
        """Test validating no null values succeeds."""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'close': [10.5, 11.0]
        })
        
        validator = DataFrameValidator()
        validator.validate_no_null_columns(df, ['date', 'close'])
    
    def test_validate_no_null_columns_failure(self):
        """Test validating no null values detects nulls."""
        df = pd.DataFrame({
            'close': [10.5, None]
        })
        
        validator = DataFrameValidator()
        with pytest.raises(AssertionError, match="has .* null values"):
            validator.validate_no_null_columns(df, ['close'])
    
    def test_validate_json_compatible_success(self):
        """Test JSON compatibility validation succeeds."""
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000'],
            'close': [10.5]
        })
        
        validator = DataFrameValidator()
        validator.validate_json_compatible(df)
    
    def test_validate_json_compatible_detects_nan(self):
        """Test JSON compatibility validation detects NaN."""
        df = pd.DataFrame({
            'close': [10.5, np.nan]
        })
        
        validator = DataFrameValidator()
        with pytest.raises(AssertionError, match="contains NaN"):
            validator.validate_json_compatible(df)
    
    def test_validate_json_compatible_detects_infinity(self):
        """Test JSON compatibility validation detects Infinity."""
        df = pd.DataFrame({
            'close': [10.5, np.inf]
        })
        
        validator = DataFrameValidator()
        with pytest.raises(AssertionError, match="contains Infinity"):
            validator.validate_json_compatible(df)


class TestMockDataGenerator:
    """Test the MockDataGenerator utility."""
    
    def test_generate_stock_symbols(self):
        """Test generating stock symbols."""
        generator = MockDataGenerator()
        symbols = generator.generate_stock_symbols(count=5)
        
        assert len(symbols) == 5
        assert all(len(s) == 6 for s in symbols)
        assert all(s.isdigit() for s in symbols)
        assert symbols[0] == '600000'
    
    def test_generate_date_range(self):
        """Test generating date range."""
        generator = MockDataGenerator()
        dates = generator.generate_date_range('2024-01-01', '2024-01-05')
        
        assert len(dates) == 5
        assert dates[0] == '2024-01-01'
        assert dates[4] == '2024-01-05'
    
    def test_generate_mock_dataframe(self):
        """Test generating mock DataFrame."""
        generator = MockDataGenerator()
        df = generator.generate_mock_dataframe(
            columns=['date', 'symbol', 'close', 'volume'],
            row_count=10,
            date_column='date',
            start_date='2024-01-01'
        )
        
        assert len(df) == 10
        assert list(df.columns) == ['date', 'symbol', 'close', 'volume']
        assert df['date'].dtype == 'object'
        assert df['date'][0] == '2024-01-01'
        assert all(len(s) == 6 for s in df['symbol'])


class TestFixtures:
    """Test pytest fixtures."""
    
    def test_df_validator_fixture(self, df_validator):
        """Test df_validator fixture."""
        assert isinstance(df_validator, DataFrameValidator)
    
    def test_mock_data_generator_fixture(self, mock_data_generator):
        """Test mock_data_generator fixture."""
        assert isinstance(mock_data_generator, MockDataGenerator)
    
    def test_sample_symbols_fixture(self, sample_symbols):
        """Test sample_symbols fixture."""
        assert len(sample_symbols) == 3
        assert '600000' in sample_symbols
    
    def test_sample_date_range_fixture(self, sample_date_range):
        """Test sample_date_range fixture."""
        assert 'start_date' in sample_date_range
        assert 'end_date' in sample_date_range
