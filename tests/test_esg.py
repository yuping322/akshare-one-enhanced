"""
Unit tests for ESG (ESG 评级) data module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from akshare_one.modules.esg import (
    get_esg_rating,
    get_esg_rating_rank,
)
from akshare_one.modules.esg.factory import ESGFactory
from akshare_one.modules.esg.eastmoney import EastmoneyESGProvider


class TestESGFactory:
    """Test ESGFactory class."""
    
    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = ESGFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyESGProvider)
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            ESGFactory.get_provider('invalid')
    
    def test_list_sources(self):
        """Test listing available sources."""
        sources = ESGFactory.list_sources()
        assert 'eastmoney' in sources


class TestEastmoneyESGProvider:
    """Test EastmoneyESGProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyESGProvider()
    
    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == 'esg'
        assert provider.get_source_name() == 'eastmoney'
        assert provider.get_update_frequency() == 'irregular'
        assert provider.get_delay_minutes() == 43200
    
    @patch('akshare.stock_esg_rate_sina')
    def test_get_esg_rating_all_stocks(self, mock_esg, provider):
        """Test getting ESG rating for all stocks."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036'],
            '股票简称': ['浦发银行', '招商银行'],
            '评级日期': ['2024-09-30', '2024-09-30'],
            'ESG评分': [85.5, 90.2],
            'E评分': [80.0, 88.0],
            'S评分': [85.0, 90.0],
            'G评分': [90.0, 92.0],
            '评级机构': ['华证ESG', '华证ESG']
        })
        mock_esg.return_value = mock_data
        
        result = provider.get_esg_rating(None, '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert len(result) == 2
        assert 'symbol' in result.columns
        assert 'rating_date' in result.columns
        assert 'esg_score' in result.columns
        assert 'e_score' in result.columns
        assert 's_score' in result.columns
        assert 'g_score' in result.columns
        assert 'rating_agency' in result.columns
        assert result['symbol'].iloc[0] == '600000'
        assert result['esg_score'].iloc[0] == 85.5
        assert result['e_score'].iloc[0] == 80.0
    
    @patch('akshare.stock_esg_rate_sina')
    def test_get_esg_rating_single_stock(self, mock_esg, provider):
        """Test getting ESG rating for a single stock."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036'],
            '股票简称': ['浦发银行', '招商银行'],
            '评级日期': ['2024-09-30', '2024-09-30'],
            'ESG评分': [85.5, 90.2],
            'E评分': [80.0, 88.0],
            'S评分': [85.0, 90.0],
            'G评分': [90.0, 92.0],
            '评级机构': ['华证ESG', '华证ESG']
        })
        mock_esg.return_value = mock_data
        
        result = provider.get_esg_rating('600000', '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert len(result) == 1
        assert result['symbol'].iloc[0] == '600000'
        assert result['esg_score'].iloc[0] == 85.5
    
    @patch('akshare.stock_esg_rate_sina')
    def test_get_esg_rating_empty(self, mock_esg, provider):
        """Test getting ESG rating with no data."""
        mock_esg.return_value = pd.DataFrame()
        
        result = provider.get_esg_rating('600000', '2024-01-01', '2024-12-31')
        
        assert result.empty
        assert 'symbol' in result.columns
        assert 'rating_date' in result.columns
        assert 'esg_score' in result.columns
    
    @patch('akshare.stock_esg_rate_sina')
    def test_get_esg_rating_rank_all_industries(self, mock_esg, provider):
        """Test getting ESG rating rankings for all industries."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036', '000001', '000002'],
            '股票简称': ['浦发银行', '招商银行', '平安银行', '万科A'],
            'ESG评分': [85.5, 90.2, 88.0, 75.5],
            '所属行业': ['银行', '银行', '银行', '房地产']
        })
        mock_esg.return_value = mock_data
        
        result = provider.get_esg_rating_rank('2024-12-31', None, 100)
        
        assert not result.empty
        assert len(result) == 4
        assert 'rank' in result.columns
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert 'esg_score' in result.columns
        assert 'industry' in result.columns
        assert 'industry_rank' in result.columns
        
        # Check ranking order (descending by ESG score)
        assert result['rank'].iloc[0] == 1
        assert result['symbol'].iloc[0] == '600036'  # Highest score
        assert result['esg_score'].iloc[0] == 90.2
    
    @patch('akshare.stock_esg_rate_sina')
    def test_get_esg_rating_rank_industry_filter(self, mock_esg, provider):
        """Test getting ESG rating rankings with industry filter."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036', '000001', '000002'],
            '股票简称': ['浦发银行', '招商银行', '平安银行', '万科A'],
            'ESG评分': [85.5, 90.2, 88.0, 75.5],
            '所属行业': ['银行', '银行', '银行', '房地产']
        })
        mock_esg.return_value = mock_data
        
        result = provider.get_esg_rating_rank('2024-12-31', '银行', 100)
        
        assert not result.empty
        assert len(result) == 3
        assert all(result['industry'] == '银行')
        
        # Check ranking within banking industry
        assert result['rank'].iloc[0] == 1
        assert result['symbol'].iloc[0] == '600036'  # Highest score in banking
    
    @patch('akshare.stock_esg_rate_sina')
    def test_get_esg_rating_rank_top_n(self, mock_esg, provider):
        """Test getting top N ESG ratings."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036', '000001', '000002'],
            '股票简称': ['浦发银行', '招商银行', '平安银行', '万科A'],
            'ESG评分': [85.5, 90.2, 88.0, 75.5],
            '所属行业': ['银行', '银行', '银行', '房地产']
        })
        mock_esg.return_value = mock_data
        
        result = provider.get_esg_rating_rank('2024-12-31', None, 2)
        
        assert not result.empty
        assert len(result) == 2
        assert result['rank'].iloc[0] == 1
        assert result['rank'].iloc[1] == 2
    
    @patch('akshare.stock_esg_rate_sina')
    def test_get_esg_rating_rank_empty(self, mock_esg, provider):
        """Test getting ESG rating rankings with no data."""
        mock_esg.return_value = pd.DataFrame()
        
        result = provider.get_esg_rating_rank('2024-12-31', None, 100)
        
        assert result.empty
        assert 'rank' in result.columns
        assert 'symbol' in result.columns
    
    def test_invalid_date_format(self, provider):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            provider.get_esg_rating_rank('2024/12/31', None, 100)
    
    def test_invalid_top_n(self, provider):
        """Test with invalid top_n value."""
        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_esg_rating_rank('2024-12-31', None, 0)


class TestESGPublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_esg_rate_sina')
    def test_get_esg_rating_api(self, mock_esg):
        """Test get_esg_rating public API."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000'],
            '股票简称': ['浦发银行'],
            '评级日期': ['2024-09-30'],
            'ESG评分': [85.5],
            'E评分': [80.0],
            'S评分': [85.0],
            'G评分': [90.0],
            '评级机构': ['华证ESG']
        })
        mock_esg.return_value = mock_data
        
        result = get_esg_rating('600000', start_date='2024-01-01', end_date='2024-12-31')
        assert not result.empty
        assert 'symbol' in result.columns
        assert 'esg_score' in result.columns
    
    @patch('akshare.stock_esg_rate_sina')
    def test_get_esg_rating_rank_api(self, mock_esg):
        """Test get_esg_rating_rank public API."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036'],
            '股票简称': ['浦发银行', '招商银行'],
            'ESG评分': [85.5, 90.2],
            '所属行业': ['银行', '银行']
        })
        mock_esg.return_value = mock_data
        
        result = get_esg_rating_rank('2024-12-31')
        assert not result.empty
        assert 'rank' in result.columns
        assert 'esg_score' in result.columns


class TestESGJSONCompatibility:
    """Test JSON compatibility of ESG data."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyESGProvider()
    
    @patch('akshare.stock_esg_rate_sina')
    def test_json_compatibility(self, mock_esg, provider):
        """Test that output is JSON compatible."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000'],
            '股票简称': ['浦发银行'],
            '评级日期': ['2024-09-30'],
            'ESG评分': [85.5],
            'E评分': [80.0],
            'S评分': [85.0],
            'G评分': [90.0],
            '评级机构': ['华证ESG']
        })
        mock_esg.return_value = mock_data
        
        result = provider.get_esg_rating(None, '2024-01-01', '2024-12-31')
        
        # Test JSON serialization
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Check no NaN values
        assert not result.isnull().any().any()
        
        # Check symbol is string with leading zeros
        assert result['symbol'].dtype in ['object', 'string']
        assert result['symbol'].iloc[0] == '600000'
        
        # Check rating_date is string
        assert result['rating_date'].dtype in ['object', 'string']
