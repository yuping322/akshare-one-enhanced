"""
Unit tests for margin financing (融资融券) data module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from akshare_one.modules.margin import (
    get_margin_data,
    get_margin_summary,
)
from akshare_one.modules.margin.factory import MarginFactory
from akshare_one.modules.margin.eastmoney import EastmoneyMarginProvider


class TestMarginFactory:
    """Test MarginFactory class."""
    
    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = MarginFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyMarginProvider)
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            MarginFactory.get_provider('invalid')
    
    def test_list_sources(self):
        """Test listing available sources."""
        sources = MarginFactory.list_sources()
        assert 'eastmoney' in sources


class TestEastmoneyMarginProvider:
    """Test EastmoneyMarginProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyMarginProvider()
    
    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == 'margin'
        assert provider.get_source_name() == 'eastmoney'
        assert provider.get_update_frequency() == 'daily'
        assert provider.get_delay_minutes() == 1440
    
    @patch('akshare.stock_margin_detail_sse')
    def test_get_margin_data_single_stock(self, mock_margin, provider):
        """Test getting margin data for a single stock."""
        mock_data = pd.DataFrame({
            '信用交易日期': ['2024-01-02', '2024-01-03'],
            '股票简称': ['浦发银行', '浦发银行'],
            '融资余额': [1000000000.0, 1100000000.0],
            '融资买入额': [50000000.0, 60000000.0],
            '融券余额': [10000000.0, 12000000.0],
            '融券卖出量': [1000000.0, 1200000.0]
        })
        mock_margin.return_value = mock_data
        
        result = provider.get_margin_data('600000', '2024-01-01', '2024-01-31')
        
        assert not result.empty
        assert len(result) == 2
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert 'margin_balance' in result.columns
        assert 'margin_buy' in result.columns
        assert 'short_balance' in result.columns
        assert 'short_sell_volume' in result.columns
        assert 'total_balance' in result.columns
        assert result['symbol'].iloc[0] == '600000'
        assert result['date'].iloc[0] == '2024-01-02'
        assert result['margin_balance'].iloc[0] == 1000000000.0
        assert result['total_balance'].iloc[0] == 1010000000.0
    
    @patch('akshare.stock_margin_detail_sse')
    def test_get_margin_data_empty(self, mock_margin, provider):
        """Test getting margin data with no data."""
        mock_margin.return_value = pd.DataFrame()
        
        result = provider.get_margin_data('600000', '2024-01-01', '2024-01-31')
        
        assert result.empty
        assert 'date' in result.columns
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_margin_underlying_info_szse')
    def test_get_margin_data_all_stocks(self, mock_margin, provider):
        """Test getting margin data for all stocks."""
        mock_data = pd.DataFrame({
            '标的代码': ['600000', '600036'],
            '标的简称': ['浦发银行', '招商银行'],
            '融资余额': [1000000000.0, 2000000000.0],
            '融券余额': [10000000.0, 20000000.0]
        })
        mock_margin.return_value = mock_data
        
        result = provider.get_margin_data(None, '2024-01-01', '2024-01-31')
        
        assert not result.empty
        assert len(result) == 2
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert result['symbol'].iloc[0] == '600000'
        assert result['symbol'].iloc[1] == '600036'
    
    @patch('akshare.stock_margin_sse')
    @patch('akshare.stock_margin_szse')
    def test_get_margin_summary_all_markets(self, mock_sz, mock_sh, provider):
        """Test getting margin summary for all markets."""
        # Mock Shanghai data
        mock_sh_data = pd.DataFrame({
            '信用交易日期': ['2024-01-02', '2024-01-03'],
            '融资余额': [500000000000.0, 510000000000.0],
            '融券余额': [5000000000.0, 5100000000.0],
            '融资融券余额': [505000000000.0, 515100000000.0]
        })
        mock_sh.return_value = mock_sh_data
        
        # Mock Shenzhen data
        mock_sz_data = pd.DataFrame({
            '信用交易日期': ['2024-01-02', '2024-01-03'],
            '融资余额': [300000000000.0, 310000000000.0],
            '融券余额': [3000000000.0, 3100000000.0],
            '融资融券余额': [303000000000.0, 313100000000.0]
        })
        mock_sz.return_value = mock_sz_data
        
        result = provider.get_margin_summary('2024-01-02', '2024-01-03', 'all')
        
        assert not result.empty
        assert 'date' in result.columns
        assert 'market' in result.columns
        assert 'margin_balance' in result.columns
        assert 'short_balance' in result.columns
        assert 'total_balance' in result.columns
        
        # Should have data for sh, sz, and all
        markets = result['market'].unique()
        assert 'sh' in markets
        assert 'sz' in markets
        assert 'all' in markets
    
    @patch('akshare.stock_margin_sse')
    def test_get_margin_summary_shanghai_only(self, mock_sh, provider):
        """Test getting margin summary for Shanghai market only."""
        mock_sh_data = pd.DataFrame({
            '信用交易日期': ['2024-01-02'],
            '融资余额': [500000000000.0],
            '融券余额': [5000000000.0],
            '融资融券余额': [505000000000.0]
        })
        mock_sh.return_value = mock_sh_data
        
        result = provider.get_margin_summary('2024-01-02', '2024-01-02', 'sh')
        
        assert not result.empty
        assert len(result) == 1
        assert result['market'].iloc[0] == 'sh'
        assert result['margin_balance'].iloc[0] == 500000000000.0
    
    @patch('akshare.stock_margin_szse')
    def test_get_margin_summary_shenzhen_only(self, mock_sz, provider):
        """Test getting margin summary for Shenzhen market only."""
        mock_sz_data = pd.DataFrame({
            '信用交易日期': ['2024-01-02'],
            '融资余额': [300000000000.0],
            '融券余额': [3000000000.0],
            '融资融券余额': [303000000000.0]
        })
        mock_sz.return_value = mock_sz_data
        
        result = provider.get_margin_summary('2024-01-02', '2024-01-02', 'sz')
        
        assert not result.empty
        assert len(result) == 1
        assert result['market'].iloc[0] == 'sz'
        assert result['margin_balance'].iloc[0] == 300000000000.0
    
    def test_get_margin_summary_invalid_market(self, provider):
        """Test getting margin summary with invalid market."""
        with pytest.raises(ValueError, match="Invalid market"):
            provider.get_margin_summary('2024-01-02', '2024-01-02', 'invalid')


class TestMarginPublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_margin_detail_sse')
    def test_get_margin_data_api(self, mock_margin):
        """Test get_margin_data public API."""
        mock_data = pd.DataFrame({
            '信用交易日期': ['2024-01-02'],
            '股票简称': ['浦发银行'],
            '融资余额': [1000000000.0],
            '融资买入额': [50000000.0],
            '融券余额': [10000000.0],
            '融券卖出量': [1000000.0]
        })
        mock_margin.return_value = mock_data
        
        result = get_margin_data('600000', start_date='2024-01-01', end_date='2024-01-31')
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_margin_sse')
    @patch('akshare.stock_margin_szse')
    def test_get_margin_summary_api(self, mock_sz, mock_sh):
        """Test get_margin_summary public API."""
        mock_sh_data = pd.DataFrame({
            '信用交易日期': ['2024-01-02'],
            '融资余额': [500000000000.0],
            '融券余额': [5000000000.0],
            '融资融券余额': [505000000000.0]
        })
        mock_sh.return_value = mock_sh_data
        
        mock_sz_data = pd.DataFrame({
            '信用交易日期': ['2024-01-02'],
            '融资余额': [300000000000.0],
            '融券余额': [3000000000.0],
            '融资融券余额': [303000000000.0]
        })
        mock_sz.return_value = mock_sz_data
        
        result = get_margin_summary(start_date='2024-01-02', end_date='2024-01-02')
        assert not result.empty
        assert 'market' in result.columns


class TestMarginJSONCompatibility:
    """Test JSON compatibility of margin financing data."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyMarginProvider()
    
    @patch('akshare.stock_margin_detail_sse')
    def test_json_compatibility(self, mock_margin, provider):
        """Test that output is JSON compatible."""
        mock_data = pd.DataFrame({
            '信用交易日期': ['2024-01-02'],
            '股票简称': ['浦发银行'],
            '融资余额': [1000000000.0],
            '融资买入额': [50000000.0],
            '融券余额': [10000000.0],
            '融券卖出量': [1000000.0]
        })
        mock_margin.return_value = mock_data
        
        result = provider.get_margin_data('600000', '2024-01-01', '2024-01-31')
        
        # Test JSON serialization
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Check no NaN values
        assert not result.isnull().any().any()
        
        # Check date is string
        assert result['date'].dtype in ['object', 'string']
        
        # Check symbol is string with leading zeros
        assert result['symbol'].dtype in ['object', 'string']
        assert result['symbol'].iloc[0] == '600000'
