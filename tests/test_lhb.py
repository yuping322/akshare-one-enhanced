"""
Unit tests for dragon tiger list (龙虎榜) data module.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.lhb import (
    get_dragon_tiger_broker_stats,
    get_dragon_tiger_list,
    get_dragon_tiger_summary,
)
from akshare_one.modules.lhb.eastmoney import EastmoneyDragonTigerProvider
from akshare_one.modules.lhb.factory import DragonTigerFactory


class TestDragonTigerFactory:
    """Test DragonTigerFactory class."""
    
    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = DragonTigerFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyDragonTigerProvider)
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            DragonTigerFactory.get_provider('invalid')
    
    def test_list_sources(self):
        """Test listing available sources."""
        sources = DragonTigerFactory.list_sources()
        assert 'eastmoney' in sources


class TestEastmoneyDragonTigerProvider:
    """Test EastmoneyDragonTigerProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()
    
    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == 'lhb'
        assert provider.get_source_name() == 'eastmoney'
        assert provider.get_update_frequency() == 'daily'
        assert provider.get_delay_minutes() == 1440
    
    @patch('akshare.stock_lhb_detail_em')
    def test_get_dragon_tiger_list_all_stocks(self, mock_lhb, provider):
        """Test getting dragon tiger list data for all stocks."""
        mock_data = pd.DataFrame({
            '序号': [1, 2],
            '代码': ['600000', '600036'],
            '名称': ['浦发银行', '招商银行'],
            '上榜日': ['2024-01-02', '2024-01-02'],
            '收盘价': [10.50, 35.20],
            '涨跌幅': [5.0, 3.5],
            '上榜原因': ['涨幅偏离值达7%', '换手率达20%'],
            '龙虎榜买入额': [50000000.0, 80000000.0],
            '龙虎榜卖出额': [30000000.0, 60000000.0],
            '龙虎榜净买额': [20000000.0, 20000000.0],
            '龙虎榜成交额': [80000000.0, 140000000.0],
            '换手率': [5.5, 8.2]
        })
        mock_lhb.return_value = mock_data
        
        result = provider.get_dragon_tiger_list('2024-01-02')
        
        assert not result.empty
        assert len(result) == 2
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert 'reason' in result.columns
        assert 'buy_amount' in result.columns
        assert 'sell_amount' in result.columns
        assert 'net_amount' in result.columns
        assert result['symbol'].iloc[0] == '600000'
    
    @patch('akshare.stock_lhb_detail_em')
    def test_get_dragon_tiger_list_single_stock(self, mock_lhb, provider):
        """Test getting dragon tiger list data for single stock."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '上榜日': ['2024-01-02'],
            '收盘价': [10.50],
            '涨跌幅': [5.0],
            '上榜原因': ['涨幅偏离值达7%'],
            '龙虎榜买入额': [50000000.0],
            '龙虎榜卖出额': [30000000.0],
            '龙虎榜净买额': [20000000.0],
            '龙虎榜成交额': [80000000.0],
            '换手率': [5.5]
        })
        mock_lhb.return_value = mock_data
        
        result = provider.get_dragon_tiger_list('2024-01-02', '600000')
        
        assert not result.empty
        assert len(result) == 1
        assert result['symbol'].iloc[0] == '600000'
    
    @patch('akshare.stock_lhb_detail_em')
    def test_get_dragon_tiger_list_empty(self, mock_lhb, provider):
        """Test getting dragon tiger list with no data."""
        mock_lhb.return_value = pd.DataFrame()
        
        result = provider.get_dragon_tiger_list('2024-01-02')
        
        assert result.empty
        assert 'date' in result.columns
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_lhb_stock_statistic_em')
    def test_get_dragon_tiger_summary_by_stock(self, mock_stat, provider):
        """Test getting dragon tiger summary grouped by stock."""
        mock_data = pd.DataFrame({
            '序号': [1, 2],
            '代码': ['600000', '600036'],
            '名称': ['浦发银行', '招商银行'],
            '上榜次数': [5, 3],
            '龙虎榜净买额': [100000000.0, 50000000.0],
            '龙虎榜买入额': [200000000.0, 100000000.0],
            '龙虎榜卖出额': [100000000.0, 50000000.0],
            '龙虎榜总成交额': [300000000.0, 150000000.0]
        })
        mock_stat.return_value = mock_data
        
        result = provider.get_dragon_tiger_summary('2024-01-01', '2024-01-31', 'stock')
        
        assert not result.empty
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert 'list_count' in result.columns
        assert 'net_buy_amount' in result.columns
        assert result['list_count'].iloc[0] == 5
    
    @patch('akshare.stock_lhb_traderstatistic_em')
    def test_get_dragon_tiger_summary_by_broker(self, mock_stat, provider):
        """Test getting dragon tiger summary grouped by broker."""
        mock_data = pd.DataFrame({
            '序号': [1, 2],
            '营业部名称': ['深股通专用', '机构专用'],
            '上榜次数': [100, 80],
            '买入额': [5000000000.0, 3000000000.0],
            '买入次数': [95, 75],
            '卖出额': [4000000000.0, 2500000000.0],
            '卖出次数': [90, 70],
            '龙虎榜成交金额': [9000000000.0, 5500000000.0]
        })
        mock_stat.return_value = mock_data
        
        result = provider.get_dragon_tiger_summary('2024-01-01', '2024-01-31', 'broker')
        
        assert not result.empty
        assert 'broker_name' in result.columns
        assert 'list_count' in result.columns
        assert 'buy_amount' in result.columns
        assert 'sell_amount' in result.columns
        assert result['list_count'].iloc[0] == 100
    
    @patch('akshare.stock_lhb_detail_em')
    def test_get_dragon_tiger_summary_by_reason(self, mock_detail, provider):
        """Test getting dragon tiger summary grouped by reason."""
        mock_data = pd.DataFrame({
            '序号': [1, 2, 3],
            '代码': ['600000', '600036', '600000'],
            '上榜原因': ['涨幅偏离值达7%', '涨幅偏离值达7%', '换手率达20%'],
            '龙虎榜净买额': [20000000.0, 30000000.0, 10000000.0],
            '龙虎榜买入额': [50000000.0, 70000000.0, 30000000.0],
            '龙虎榜卖出额': [30000000.0, 40000000.0, 20000000.0],
            '龙虎榜成交额': [80000000.0, 110000000.0, 50000000.0]
        })
        mock_detail.return_value = mock_data
        
        result = provider.get_dragon_tiger_summary('2024-01-01', '2024-01-31', 'reason')
        
        assert not result.empty
        assert 'reason' in result.columns
        assert 'list_count' in result.columns
        assert 'net_buy_amount' in result.columns
    
    def test_get_dragon_tiger_summary_invalid_group_by(self, provider):
        """Test invalid group_by parameter."""
        with pytest.raises(ValueError, match="Invalid group_by"):
            provider.get_dragon_tiger_summary('2024-01-01', '2024-01-31', 'invalid')
    
    @patch('akshare.stock_lhb_traderstatistic_em')
    def test_get_dragon_tiger_broker_stats(self, mock_stat, provider):
        """Test getting broker statistics."""
        mock_data = pd.DataFrame({
            '序号': [1, 2, 3],
            '营业部名称': ['深股通专用', '机构专用', '某营业部'],
            '上榜次数': [100, 80, 60],
            '买入额': [5000000000.0, 3000000000.0, 2000000000.0],
            '买入次数': [95, 75, 55],
            '卖出额': [4000000000.0, 2500000000.0, 1800000000.0],
            '卖出次数': [90, 70, 50],
            '龙虎榜成交金额': [9000000000.0, 5500000000.0, 3800000000.0]
        })
        mock_stat.return_value = mock_data
        
        result = provider.get_dragon_tiger_broker_stats('2024-01-01', '2024-01-31', 2)
        
        assert not result.empty
        assert len(result) == 2
        assert 'rank' in result.columns
        assert 'broker_name' in result.columns
        assert 'list_count' in result.columns
        assert 'buy_amount' in result.columns
        assert 'sell_amount' in result.columns
        assert 'net_amount' in result.columns
        assert result['rank'].iloc[0] == 1
    
    def test_get_dragon_tiger_broker_stats_invalid_top_n(self, provider):
        """Test invalid top_n parameter."""
        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_dragon_tiger_broker_stats('2024-01-01', '2024-01-31', 0)


class TestDragonTigerPublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_lhb_detail_em')
    def test_get_dragon_tiger_list_api(self, mock_lhb):
        """Test get_dragon_tiger_list public API."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '上榜日': ['2024-01-02'],
            '收盘价': [10.50],
            '涨跌幅': [5.0],
            '上榜原因': ['涨幅偏离值达7%'],
            '龙虎榜买入额': [50000000.0],
            '龙虎榜卖出额': [30000000.0],
            '龙虎榜净买额': [20000000.0],
            '龙虎榜成交额': [80000000.0],
            '换手率': [5.5]
        })
        mock_lhb.return_value = mock_data
        
        result = get_dragon_tiger_list('2024-01-02')
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_lhb_stock_statistic_em')
    def test_get_dragon_tiger_summary_api(self, mock_stat):
        """Test get_dragon_tiger_summary public API."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '上榜次数': [5],
            '龙虎榜净买额': [100000000.0],
            '龙虎榜买入额': [200000000.0],
            '龙虎榜卖出额': [100000000.0],
            '龙虎榜总成交额': [300000000.0]
        })
        mock_stat.return_value = mock_data
        
        result = get_dragon_tiger_summary('2024-01-01', '2024-01-31', 'stock')
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_lhb_traderstatistic_em')
    def test_get_dragon_tiger_broker_stats_api(self, mock_stat):
        """Test get_dragon_tiger_broker_stats public API."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '营业部名称': ['深股通专用'],
            '上榜次数': [100],
            '买入额': [5000000000.0],
            '买入次数': [95],
            '卖出额': [4000000000.0],
            '卖出次数': [90],
            '龙虎榜成交金额': [9000000000.0]
        })
        mock_stat.return_value = mock_data
        
        result = get_dragon_tiger_broker_stats('2024-01-01', '2024-01-31', 10)
        assert not result.empty
        assert 'broker_name' in result.columns


class TestDragonTigerJSONCompatibility:
    """Test JSON compatibility of dragon tiger data."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyDragonTigerProvider()
    
    @patch('akshare.stock_lhb_detail_em')
    def test_json_compatibility(self, mock_lhb, provider):
        """Test that output is JSON compatible."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '上榜日': ['2024-01-02'],
            '收盘价': [10.50],
            '涨跌幅': [5.0],
            '上榜原因': ['涨幅偏离值达7%'],
            '龙虎榜买入额': [50000000.0],
            '龙虎榜卖出额': [30000000.0],
            '龙虎榜净买额': [20000000.0],
            '龙虎榜成交额': [80000000.0],
            '换手率': [5.5]
        })
        mock_lhb.return_value = mock_data
        
        result = provider.get_dragon_tiger_list('2024-01-02')
        
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
