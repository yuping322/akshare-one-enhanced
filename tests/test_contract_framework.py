"""
Test to verify the contract testing framework works correctly.

This test demonstrates how to use the GoldenSampleValidator.
"""

import pytest
import pandas as pd
from tests.utils.contract_test import GoldenSampleValidator


class TestContractFramework:
    """Test the contract testing framework itself."""
    
    def test_golden_sample_creation_and_validation(self, tmp_path):
        """Test creating and validating golden samples."""
        # Create sample data
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'symbol': ['600000', '600000'],
            'close': [10.5, 11.0]
        })
        
        # Create validator with temporary directory
        validator = GoldenSampleValidator('test_module', samples_dir=tmp_path)
        
        # Save golden sample
        validator.save_golden_sample('test_sample', df)
        
        # Validate against golden sample (should pass)
        validator.assert_schema_matches('test_sample', df)
        
        # Create new data with same schema
        df2 = pd.DataFrame({
            'date': ['2024-01-03'],
            'symbol': ['600001'],
            'close': [20.5]
        })
        
        # Should pass (same schema, different data)
        validator.assert_schema_matches('test_sample', df2)
    
    def test_golden_sample_detects_missing_columns(self, tmp_path):
        """Test that golden sample validation detects missing columns."""
        # Create original data
        df_original = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000'],
            'close': [10.5]
        })
        
        validator = GoldenSampleValidator('test_module', samples_dir=tmp_path)
        validator.save_golden_sample('test_missing', df_original)
        
        # Create data with missing column
        df_missing = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000']
        })
        
        # Should detect missing column
        with pytest.raises(AssertionError, match="Missing columns"):
            validator.assert_schema_matches('test_missing', df_missing)
    
    def test_golden_sample_detects_extra_columns(self, tmp_path):
        """Test that golden sample validation detects extra columns."""
        # Create original data
        df_original = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000']
        })
        
        validator = GoldenSampleValidator('test_module', samples_dir=tmp_path)
        validator.save_golden_sample('test_extra', df_original)
        
        # Create data with extra column
        df_extra = pd.DataFrame({
            'date': ['2024-01-01'],
            'symbol': ['600000'],
            'extra': [100]
        })
        
        # Should detect extra column
        with pytest.raises(AssertionError, match="Extra columns"):
            validator.assert_schema_matches('test_extra', df_extra)
