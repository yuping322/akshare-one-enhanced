"""
Unit tests for equity pledge (股权质押) data module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from akshare_one.modules.pledge import (
    get_equity_pledge,
    get_equity_pledge_ratio_rank,
)
from akshare_one.modules.pledge.factory import EquityPledgeFactory
from akshare_one.modules.pledge.eastmoney import EastmoneyEquityPledgeProvider


class TestEquityPledgeFactory:
    """Test EquityPledgeFactory class."""
    
    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = EquityPledgeFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyEquityPledgeProvider)
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            EquityPledgeFactory.get_provider('invalid')
    
    def test_list_sources(self):
        """Test listing available sources."""
        sources = EquityPledgeFactory.list_sources()
        assert 'eastmoney' in sources


class TestEastmoneyEquityPledgeProvider:
    """Test EastmoneyEquityPledgeProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyEquityPledgeProvider()
    
    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == 'pledge'
        assert provider.get_source_name() == 'eastmoney'
        assert provider.get_update_frequency() == 'irregular'
        assert provider.get_delay_minutes() == 0
    
    @patch('akshare.stock_gpzy_pledge_ratio_detail_em')
    def test_get_equity_pledge_single_stock(self, mock_pledge, provider):
        """Test getting equity pledge data for a single stock."""
        mock_data = pd.DataFrame({
            '股东名称': ['股东A', '股东B'],
            '质押股数': [10000000.0, 20000000.0],
            '占所持股份比例': [50.0, 60.0],
            '质权人': ['银行A', '银行B'],
            '公告日期': ['2024-01-02', '2024-01-03']
        })
        mock_pledge.return_value = mock_data
        
        result = provider.get_equity_pledge('600000', '2024-01-01', '2024-01-31')
        
        assert not result.empty
        assert len(result) == 2
        assert 'symbol' in result.columns
        assert 'shareholder_name' in result.columns
        assert 'pledge_shares' in result.columns
        assert 'pledge_ratio' in result.columns
        assert 'pledgee' in result.columns
        assert 'pledge_date' in result.columns
        assert result['symbol'].iloc[0] == '600000'
        assert result['shareholder_name'].iloc[0] == '股东A'
        assert result['pledge_shares'].iloc[0] == 10000000.0
        assert result['pledge_ratio'].iloc[0] == 50.0
        assert result['pledgee'].iloc[0] == '银行A'
        assert result['pledge_date'].iloc[0] == '2024-01-02'
    
    @patch('akshare.stock_gpzy_pledge_ratio_detail_em')
    def test_get_equity_pledge_empty(self, mock_pledge, provider):
        """Test getting equity pledge data with no data."""
        mock_pledge.return_value = pd.DataFrame()
        
        result = provider.get_equity_pledge('600000', '2024-01-01', '2024-01-31')
        
        assert result.empty
        assert 'symbol' in result.columns
        assert 'shareholder_name' in result.columns
    
    @patch('akshare.stock_gpzy_pledge_ratio_em')
    def test_get_equity_pledge_all_stocks(self, mock_pledge, provider):
        """Test getting equity pledge data for all stocks."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036'],
            '股东名称': ['股东A', '股东B'],
            '质押股数': [10000000.0, 20000000.0],
            '占所持股份比例': [50.0, 60.0],
            '质权人': ['银行A', '银行B'],
            '公告日期': ['2024-01-02', '2024-01-03']
        })
        mock_pledge.return_value = mock_data
        
        result = provider.get_equity_pledge(None, '2024-01-01', '2024-01-31')
        
        assert not result.empty
        assert len(result) == 2
        assert 'symbol' in result.columns
        assert 'shareholder_name' in result.columns
        assert result['symbol'].iloc[0] == '600000'
        assert result['symbol'].iloc[1] == '600036'
    
    @patch('akshare.stock_gpzy_pledge_ratio_em')
    def test_get_equity_pledge_ratio_rank(self, mock_ratio, provider):
        """Test getting equity pledge ratio ranking."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036', '000001'],
            '股票简称': ['浦发银行', '招商银行', '平安银行'],
            '质押比例': [80.5, 75.3, 70.2],
            '质押市值': [5000000000.0, 4500000000.0, 4000000000.0]
        })
        mock_ratio.return_value = mock_data
        
        result = provider.get_equity_pledge_ratio_rank('2024-01-31', 100)
        
        assert not result.empty
        assert len(result) == 3
        assert 'rank' in result.columns
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert 'pledge_ratio' in result.columns
        assert 'pledge_value' in result.columns
        assert result['rank'].iloc[0] == 1
        assert result['symbol'].iloc[0] == '600000'
        assert result['name'].iloc[0] == '浦发银行'
        assert result['pledge_ratio'].iloc[0] == 80.5
        assert result['pledge_value'].iloc[0] == 5000000000.0
        # Check ranking is correct (sorted by pledge_ratio descending)
        assert result['pledge_ratio'].iloc[0] >= result['pledge_ratio'].iloc[1]
        assert result['pledge_ratio'].iloc[1] >= result['pledge_ratio'].iloc[2]
    
    @patch('akshare.stock_gpzy_pledge_ratio_em')
    def test_get_equity_pledge_ratio_rank_top_n(self, mock_ratio, provider):
        """Test getting top N equity pledge ratio ranking."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036', '000001', '000002', '000003'],
            '股票简称': ['股票A', '股票B', '股票C', '股票D', '股票E'],
            '质押比例': [80.5, 75.3, 70.2, 65.1, 60.0],
            '质押市值': [5000000000.0, 4500000000.0, 4000000000.0, 3500000000.0, 3000000000.0]
        })
        mock_ratio.return_value = mock_data
        
        result = provider.get_equity_pledge_ratio_rank('2024-01-31', 3)
        
        assert not result.empty
        assert len(result) == 3  # Should only return top 3
        assert result['rank'].iloc[0] == 1
        assert result['rank'].iloc[2] == 3
    
    @patch('akshare.stock_gpzy_pledge_ratio_em')
    def test_get_equity_pledge_ratio_rank_empty(self, mock_ratio, provider):
        """Test getting equity pledge ratio ranking with no data."""
        mock_ratio.return_value = pd.DataFrame()
        
        result = provider.get_equity_pledge_ratio_rank('2024-01-31', 100)
        
        assert result.empty
        assert 'rank' in result.columns
        assert 'symbol' in result.columns
    
    def test_get_equity_pledge_ratio_rank_invalid_date(self, provider):
        """Test getting equity pledge ratio ranking with invalid date."""
        with pytest.raises(ValueError, match="Invalid date format"):
            provider.get_equity_pledge_ratio_rank('2024/01/31', 100)
    
    def test_get_equity_pledge_ratio_rank_invalid_top_n(self, provider):
        """Test getting equity pledge ratio ranking with invalid top_n."""
        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_equity_pledge_ratio_rank('2024-01-31', 0)


class TestEquityPledgePublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_gpzy_pledge_ratio_detail_em')
    def test_get_equity_pledge_api(self, mock_pledge):
        """Test get_equity_pledge public API."""
        mock_data = pd.DataFrame({
            '股东名称': ['股东A'],
            '质押股数': [10000000.0],
            '占所持股份比例': [50.0],
            '质权人': ['银行A'],
            '公告日期': ['2024-01-02']
        })
        mock_pledge.return_value = mock_data
        
        result = get_equity_pledge('600000', start_date='2024-01-01', end_date='2024-01-31')
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_gpzy_pledge_ratio_em')
    def test_get_equity_pledge_ratio_rank_api(self, mock_ratio):
        """Test get_equity_pledge_ratio_rank public API."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000'],
            '股票简称': ['浦发银行'],
            '质押比例': [80.5],
            '质押市值': [5000000000.0]
        })
        mock_ratio.return_value = mock_data
        
        result = get_equity_pledge_ratio_rank('2024-01-31')
        assert not result.empty
        assert 'rank' in result.columns


class TestEquityPledgeJSONCompatibility:
    """Test JSON compatibility of equity pledge data."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyEquityPledgeProvider()
    
    @patch('akshare.stock_gpzy_pledge_ratio_detail_em')
    def test_json_compatibility_pledge_data(self, mock_pledge, provider):
        """Test that equity pledge data output is JSON compatible."""
        mock_data = pd.DataFrame({
            '股东名称': ['股东A'],
            '质押股数': [10000000.0],
            '占所持股份比例': [50.0],
            '质权人': ['银行A'],
            '公告日期': ['2024-01-02']
        })
        mock_pledge.return_value = mock_data
        
        result = provider.get_equity_pledge('600000', '2024-01-01', '2024-01-31')
        
        # Test JSON serialization
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Check no NaN values
        assert not result.isnull().any().any()
        
        # Check symbol is string with leading zeros
        assert result['symbol'].dtype in ['object', 'string']
        assert result['symbol'].iloc[0] == '600000'
    
    @patch('akshare.stock_gpzy_pledge_ratio_em')
    def test_json_compatibility_ratio_rank(self, mock_ratio, provider):
        """Test that equity pledge ratio ranking output is JSON compatible."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000'],
            '股票简称': ['浦发银行'],
            '质押比例': [80.5],
            '质押市值': [5000000000.0]
        })
        mock_ratio.return_value = mock_data
        
        result = provider.get_equity_pledge_ratio_rank('2024-01-31', 100)
        
        # Test JSON serialization
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Check no NaN values
        assert not result.isnull().any().any()
        
        # Check symbol is string with leading zeros
        assert result['symbol'].dtype in ['object', 'string']
        assert result['symbol'].iloc[0] == '600000'
