"""
Integration tests for macro economic data module.

These tests make real API calls to verify the module works end-to-end.
"""

import pytest
import pandas as pd

from akshare_one.modules.macro import (
    get_lpr_rate,
    get_pmi_index,
    get_cpi_data,
    get_ppi_data,
    get_m2_supply,
    get_shibor_rate,
    get_social_financing,
)


@pytest.mark.integration
class TestMacroIntegration:
    """Integration tests for macro data module."""
    
    def test_get_lpr_rate_integration(self):
        """Test getting real LPR rate data."""
        df = get_lpr_rate(start_date='2024-01-01', end_date='2024-12-31')
        
        # Verify structure
        assert isinstance(df, pd.DataFrame)
        assert 'date' in df.columns
        assert 'lpr_1y' in df.columns
        assert 'lpr_5y' in df.columns
        
        # Verify data types
        if not df.empty:
            assert df['date'].dtype in ['object', 'string']
            assert df['lpr_1y'].dtype in ['float64', 'float32']
    
    def test_get_pmi_index_integration(self):
        """Test getting real PMI index data."""
        df = get_pmi_index(start_date='2024-01-01', pmi_type='manufacturing')
        
        assert isinstance(df, pd.DataFrame)
        assert 'date' in df.columns
        assert 'pmi_value' in df.columns
    
    def test_get_cpi_data_integration(self):
        """Test getting real CPI data."""
        df = get_cpi_data(start_date='2024-01-01')
        
        assert isinstance(df, pd.DataFrame)
        assert 'date' in df.columns
        assert 'current' in df.columns
        assert 'yoy' in df.columns
    
    def test_get_m2_supply_integration(self):
        """Test getting real M2 supply data."""
        df = get_m2_supply(start_date='2024-01-01')
        
        assert isinstance(df, pd.DataFrame)
        assert 'date' in df.columns
        assert 'm2_balance' in df.columns
        assert 'yoy_growth_rate' in df.columns
    
    def test_get_shibor_rate_integration(self):
        """Test getting real Shibor rate data."""
        df = get_shibor_rate(start_date='2024-01-01', end_date='2024-12-31')
        
        assert isinstance(df, pd.DataFrame)
        assert 'date' in df.columns
        assert 'overnight' in df.columns
        assert 'year_1' in df.columns
