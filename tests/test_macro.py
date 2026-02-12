"""
Unit tests for macro economic data module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from akshare_one.modules.macro import (
    get_lpr_rate,
    get_pmi_index,
    get_cpi_data,
    get_ppi_data,
    get_m2_supply,
    get_shibor_rate,
    get_social_financing,
)
from akshare_one.modules.macro.factory import MacroFactory
from akshare_one.modules.macro.official import OfficialMacroProvider


class TestMacroFactory:
    """Test MacroFactory class."""
    
    def test_get_provider_official(self):
        """Test getting official provider."""
        provider = MacroFactory.get_provider('official')
        assert isinstance(provider, OfficialMacroProvider)
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            MacroFactory.get_provider('invalid')
    
    def test_list_sources(self):
        """Test listing available sources."""
        sources = MacroFactory.list_sources()
        assert 'official' in sources


class TestOfficialMacroProvider:
    """Test OfficialMacroProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return OfficialMacroProvider()
    
    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == 'macro'
        assert provider.get_source_name() == 'official'
        assert provider.get_update_frequency() == 'monthly'
        assert provider.get_delay_minutes() == 0
    
    @patch('akshare.macro_china_lpr')
    def test_get_lpr_rate(self, mock_lpr, provider):
        """Test getting LPR rate data."""
        # Mock data
        mock_data = pd.DataFrame({
            'TRADE_DATE': ['2024-01-20', '2024-02-20'],
            'LPR1Y': [3.45, 3.45],
            'LPR5Y': [4.20, 4.20]
        })
        mock_lpr.return_value = mock_data
        
        result = provider.get_lpr_rate('2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert 'date' in result.columns
        assert 'lpr_1y' in result.columns
        assert 'lpr_5y' in result.columns
        assert result['date'].dtype in ['object', 'string']
    
    @patch('akshare.macro_china_pmi')
    def test_get_pmi_manufacturing(self, mock_pmi, provider):
        """Test getting manufacturing PMI data."""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01', '2024-02-01'],
            '制造业-指数': [50.2, 50.5]
        })
        mock_pmi.return_value = mock_data
        
        result = provider.get_pmi_index('2024-01-01', '2024-12-31', 'manufacturing')
        
        assert not result.empty
        assert 'date' in result.columns
        assert 'pmi_value' in result.columns
    
    @patch('akshare.macro_china_cpi')
    def test_get_cpi_data(self, mock_cpi, provider):
        """Test getting CPI data."""
        mock_data = pd.DataFrame({
            '月份': ['2024-01-01', '2024-02-01'],
            '当月': [100.0, 100.5],
            '同比增长': [2.1, 2.2],
            '环比增长': [0.1, 0.2],
            '累计': [100.0, 100.5]
        })
        mock_cpi.return_value = mock_data
        
        result = provider.get_cpi_data('2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert 'date' in result.columns
        assert 'current' in result.columns
        assert 'yoy' in result.columns
        assert 'mom' in result.columns
    
    @patch('akshare.macro_china_m2_yearly')
    def test_get_m2_supply(self, mock_m2, provider):
        """Test getting M2 supply data."""
        mock_data = pd.DataFrame({
            '月份': ['2024-01-01', '2024-02-01'],
            'M2数量(亿元)': [2500000, 2510000],
            'M2同比增长': [8.5, 8.6]
        })
        mock_m2.return_value = mock_data
        
        result = provider.get_m2_supply('2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert 'date' in result.columns
        assert 'm2_balance' in result.columns
        assert 'yoy_growth_rate' in result.columns
    
    @patch('akshare.macro_china_shibor_all')
    def test_get_shibor_rate(self, mock_shibor, provider):
        """Test getting Shibor rate data."""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01', '2024-01-02'],
            '隔夜': [1.5, 1.6],
            '1周': [1.8, 1.9],
            '2周': [2.0, 2.1],
            '1月': [2.2, 2.3],
            '3月': [2.5, 2.6],
            '6月': [2.8, 2.9],
            '9月': [3.0, 3.1],
            '1年': [3.2, 3.3]
        })
        mock_shibor.return_value = mock_data
        
        result = provider.get_shibor_rate('2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert 'date' in result.columns
        assert 'overnight' in result.columns
        assert 'year_1' in result.columns
    
    def test_invalid_pmi_type(self, provider):
        """Test invalid PMI type."""
        with pytest.raises(ValueError, match="Invalid pmi_type"):
            provider.get_pmi_index('2024-01-01', '2024-12-31', 'invalid')


class TestMacroPublicAPI:
    """Test public API functions."""
    
    @patch('akshare.macro_china_lpr')
    def test_get_lpr_rate_api(self, mock_lpr):
        """Test get_lpr_rate public API."""
        mock_data = pd.DataFrame({
            'TRADE_DATE': ['2024-01-20'],
            'LPR1Y': [3.45],
            'LPR5Y': [4.20]
        })
        mock_lpr.return_value = mock_data
        
        result = get_lpr_rate(start_date='2024-01-01')
        assert not result.empty
    
    @patch('akshare.macro_china_pmi')
    def test_get_pmi_index_api(self, mock_pmi):
        """Test get_pmi_index public API."""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01'],
            '制造业-指数': [50.2]
        })
        mock_pmi.return_value = mock_data
        
        result = get_pmi_index(start_date='2024-01-01', pmi_type='manufacturing')
        assert not result.empty
