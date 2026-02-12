"""
Unit tests for restricted stock release (限售解禁) data module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from akshare_one.modules.restricted import (
    get_restricted_release,
    get_restricted_release_calendar,
)
from akshare_one.modules.restricted.factory import RestrictedReleaseFactory
from akshare_one.modules.restricted.eastmoney import EastmoneyRestrictedReleaseProvider


class TestRestrictedReleaseFactory:
    """Test RestrictedReleaseFactory class."""
    
    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = RestrictedReleaseFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyRestrictedReleaseProvider)
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            RestrictedReleaseFactory.get_provider('invalid')
    
    def test_list_sources(self):
        """Test listing available sources."""
        sources = RestrictedReleaseFactory.list_sources()
        assert 'eastmoney' in sources


class TestEastmoneyRestrictedReleaseProvider:
    """Test EastmoneyRestrictedReleaseProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyRestrictedReleaseProvider()
    
    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == 'restricted'
        assert provider.get_source_name() == 'eastmoney'
        assert provider.get_update_frequency() == 'irregular'
        assert provider.get_delay_minutes() == 0
    
    @patch('akshare.stock_restricted_release_queue_em')
    def test_get_restricted_release_single_stock(self, mock_release, provider):
        """Test getting restricted release data for a single stock."""
        mock_data = pd.DataFrame({
            '解禁时间': ['2024-01-15', '2024-02-20'],
            '解禁数量': [10000000.0, 20000000.0],
            '解禁市值': [150000000.0, 300000000.0],
            '股份类型': ['首发原股东限售股份', '定向增发机构配售股份'],
            '股东名称': ['股东A', '股东B']
        })
        mock_release.return_value = mock_data
        
        result = provider.get_restricted_release('600000', '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert len(result) == 2
        assert 'symbol' in result.columns
        assert 'release_date' in result.columns
        assert 'release_shares' in result.columns
        assert 'release_value' in result.columns
        assert 'release_type' in result.columns
        assert 'shareholder_name' in result.columns
        assert result['symbol'].iloc[0] == '600000'
        assert result['release_date'].iloc[0] == '2024-01-15'
        assert result['release_shares'].iloc[0] == 10000000.0
        assert result['release_value'].iloc[0] == 150000000.0
        assert result['release_type'].iloc[0] == '首发原股东限售股份'
        assert result['shareholder_name'].iloc[0] == '股东A'
    
    @patch('akshare.stock_restricted_release_queue_em')
    def test_get_restricted_release_empty(self, mock_release, provider):
        """Test getting restricted release data with no data."""
        mock_release.return_value = pd.DataFrame()
        
        result = provider.get_restricted_release('600000', '2024-01-01', '2024-12-31')
        
        assert result.empty
        assert 'symbol' in result.columns
        assert 'release_date' in result.columns
    
    @patch('akshare.stock_restricted_release_detail_em')
    def test_get_restricted_release_all_stocks(self, mock_release, provider):
        """Test getting restricted release data for all stocks."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036'],
            '解禁时间': ['2024-01-15', '2024-02-20'],
            '解禁数量': [10000000.0, 20000000.0],
            '解禁市值': [150000000.0, 300000000.0],
            '股份类型': ['首发原股东限售股份', '定向增发机构配售股份'],
            '股东名称': ['股东A', '股东B']
        })
        mock_release.return_value = mock_data
        
        result = provider.get_restricted_release(None, '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert len(result) == 2
        assert 'symbol' in result.columns
        assert 'release_date' in result.columns
        assert result['symbol'].iloc[0] == '600000'
        assert result['symbol'].iloc[1] == '600036'
    
    @patch('akshare.stock_restricted_release_detail_em')
    def test_get_restricted_release_calendar(self, mock_release, provider):
        """Test getting restricted release calendar."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036', '000001', '600000'],
            '解禁时间': ['2024-01-15', '2024-01-15', '2024-02-20', '2024-02-20'],
            '解禁市值': [150000000.0, 200000000.0, 300000000.0, 100000000.0]
        })
        mock_release.return_value = mock_data
        
        result = provider.get_restricted_release_calendar('2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert len(result) == 2  # Two unique dates
        assert 'date' in result.columns
        assert 'release_stock_count' in result.columns
        assert 'total_release_value' in result.columns
        assert result['date'].iloc[0] == '2024-01-15'
        assert result['release_stock_count'].iloc[0] == 2  # Two stocks on 2024-01-15
        assert result['total_release_value'].iloc[0] == 350000000.0  # 150M + 200M
        assert result['date'].iloc[1] == '2024-02-20'
        assert result['release_stock_count'].iloc[1] == 2  # Two stocks on 2024-02-20
        assert result['total_release_value'].iloc[1] == 400000000.0  # 300M + 100M
    
    @patch('akshare.stock_restricted_release_detail_em')
    def test_get_restricted_release_calendar_empty(self, mock_release, provider):
        """Test getting restricted release calendar with no data."""
        mock_release.return_value = pd.DataFrame()
        
        result = provider.get_restricted_release_calendar('2024-01-01', '2024-12-31')
        
        assert result.empty
        assert 'date' in result.columns
        assert 'release_stock_count' in result.columns
        assert 'total_release_value' in result.columns
    
    @patch('akshare.stock_restricted_release_detail_em')
    def test_get_restricted_release_calendar_date_filter(self, mock_release, provider):
        """Test getting restricted release calendar with date filtering."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036', '000001'],
            '解禁时间': ['2024-01-15', '2024-02-20', '2024-03-25'],
            '解禁市值': [150000000.0, 200000000.0, 300000000.0]
        })
        mock_release.return_value = mock_data
        
        # Filter to only January and February
        result = provider.get_restricted_release_calendar('2024-01-01', '2024-02-29')
        
        assert not result.empty
        assert len(result) == 2  # Only two dates in range
        assert result['date'].iloc[0] == '2024-01-15'
        assert result['date'].iloc[1] == '2024-02-20'
        # March date should be filtered out
        assert '2024-03-25' not in result['date'].values


class TestRestrictedReleasePublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_restricted_release_queue_em')
    def test_get_restricted_release_api(self, mock_release):
        """Test get_restricted_release public API."""
        mock_data = pd.DataFrame({
            '解禁时间': ['2024-01-15'],
            '解禁数量': [10000000.0],
            '解禁市值': [150000000.0],
            '股份类型': ['首发原股东限售股份'],
            '股东名称': ['股东A']
        })
        mock_release.return_value = mock_data
        
        result = get_restricted_release('600000', start_date='2024-01-01', end_date='2024-12-31')
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_restricted_release_detail_em')
    def test_get_restricted_release_calendar_api(self, mock_release):
        """Test get_restricted_release_calendar public API."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036'],
            '解禁时间': ['2024-01-15', '2024-01-15'],
            '解禁市值': [150000000.0, 200000000.0]
        })
        mock_release.return_value = mock_data
        
        result = get_restricted_release_calendar('2024-01-01', '2024-12-31')
        assert not result.empty
        assert 'date' in result.columns
        assert 'release_stock_count' in result.columns


class TestRestrictedReleaseJSONCompatibility:
    """Test JSON compatibility of restricted release data."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyRestrictedReleaseProvider()
    
    @patch('akshare.stock_restricted_release_queue_em')
    def test_json_compatibility_release_data(self, mock_release, provider):
        """Test that restricted release data output is JSON compatible."""
        mock_data = pd.DataFrame({
            '解禁时间': ['2024-01-15'],
            '解禁数量': [10000000.0],
            '解禁市值': [150000000.0],
            '股份类型': ['首发原股东限售股份'],
            '股东名称': ['股东A']
        })
        mock_release.return_value = mock_data
        
        result = provider.get_restricted_release('600000', '2024-01-01', '2024-12-31')
        
        # Test JSON serialization
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Check no NaN values
        assert not result.isnull().any().any()
        
        # Check symbol is string with leading zeros
        assert result['symbol'].dtype in ['object', 'string']
        assert result['symbol'].iloc[0] == '600000'
        
        # Check date is string
        assert result['release_date'].dtype in ['object', 'string']
    
    @patch('akshare.stock_restricted_release_detail_em')
    def test_json_compatibility_calendar(self, mock_release, provider):
        """Test that restricted release calendar output is JSON compatible."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036'],
            '解禁时间': ['2024-01-15', '2024-01-15'],
            '解禁市值': [150000000.0, 200000000.0]
        })
        mock_release.return_value = mock_data
        
        result = provider.get_restricted_release_calendar('2024-01-01', '2024-12-31')
        
        # Test JSON serialization
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Check no NaN values
        assert not result.isnull().any().any()
        
        # Check date is string
        assert result['date'].dtype in ['object', 'string']


class TestRestrictedReleaseDataValidation:
    """Test data validation for restricted release module."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyRestrictedReleaseProvider()
    
    def test_invalid_symbol_format(self, provider):
        """Test validation of invalid symbol format."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.get_restricted_release('INVALID', '2024-01-01', '2024-12-31')
    
    def test_invalid_date_format(self, provider):
        """Test validation of invalid date format."""
        with pytest.raises(ValueError, match="Invalid start_date format"):
            provider.get_restricted_release('600000', '2024/01/01', '2024-12-31')
    
    def test_invalid_date_range(self, provider):
        """Test validation of invalid date range."""
        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            provider.get_restricted_release('600000', '2024-12-31', '2024-01-01')
    
    def test_calendar_invalid_date_format(self, provider):
        """Test calendar validation of invalid date format."""
        with pytest.raises(ValueError, match="Invalid start_date format"):
            provider.get_restricted_release_calendar('2024/01/01', '2024-12-31')
    
    def test_calendar_invalid_date_range(self, provider):
        """Test calendar validation of invalid date range."""
        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            provider.get_restricted_release_calendar('2024-12-31', '2024-01-01')
