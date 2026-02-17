"""
Unit tests for block deal data module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from akshare_one.modules.blockdeal import (
    get_block_deal,
    get_block_deal_summary,
)
from akshare_one.modules.blockdeal.factory import BlockDealFactory
from akshare_one.modules.blockdeal.eastmoney import EastmoneyBlockDealProvider


class TestBlockDealFactory:
    """Test BlockDealFactory class."""
    
    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = BlockDealFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyBlockDealProvider)
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            BlockDealFactory.get_provider('invalid')


class TestEastmoneyBlockDealProvider:
    """Test EastmoneyBlockDealProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyBlockDealProvider()
    
    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == 'blockdeal'
        assert provider.get_source_name() == 'eastmoney'
        assert provider.get_update_frequency() == 'daily'
    
    @patch('akshare.stock_dzjy_mrtj')
    def test_get_block_deal_single_stock(self, mock_dzjy, provider):
        """Test getting block deal data for single stock."""
        mock_data = pd.DataFrame({
            '序号': [1, 2],
            '交易日期': ['2024-01-15', '2024-01-16'],
            '证券代码': ['600000', '600000'],
            '证券简称': ['浦发银行', '浦发银行'],
            '涨跌幅': [1.0, 1.5],
            '收盘价': [10.45, 10.55],
            '成交价': [10.50, 10.60],
            '折溢率': [0.48, 0.47],
            '成交笔数': [5, 6],
            '成交总量': [100.0, 150.0],
            '成交总额': [1050.0, 1590.0],
            '成交总额/流通市值': [0.1, 0.15]
        })
        mock_dzjy.return_value = mock_data
        
        result = provider.get_block_deal('600000', '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'premium_rate' in result.columns
    
    @patch('akshare.stock_dzjy_mrtj')
    def test_get_block_deal_all_stocks(self, mock_dzjy, provider):
        """Test getting block deal data for all stocks."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '交易日期': ['2024-01-15'],
            '证券代码': ['600000'],
            '证券简称': ['浦发银行'],
            '涨跌幅': [1.0],
            '收盘价': [10.45],
            '成交价': [10.50],
            '折溢率': [0.48],
            '成交笔数': [5],
            '成交总量': [100.0],
            '成交总额': [1050.0],
            '成交总额/流通市值': [0.1]
        })
        mock_dzjy.return_value = mock_data
        
        result = provider.get_block_deal(None, '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_dzjy_mrtj')
    def test_get_block_deal_summary_by_stock(self, mock_dzjy, provider):
        """Test getting block deal summary grouped by stock."""
        mock_data = pd.DataFrame({
            '序号': [1, 2, 3],
            '交易日期': ['2024-01-15', '2024-01-16', '2024-01-15'],
            '证券代码': ['600000', '600000', '600036'],
            '证券简称': ['浦发银行', '浦发银行', '招商银行'],
            '涨跌幅': [1.0, 1.5, 2.0],
            '收盘价': [10.45, 10.55, 35.00],
            '成交价': [10.50, 10.60, 35.20],
            '折溢率': [0.48, 0.47, 0.57],
            '成交笔数': [5, 6, 3],
            '成交总量': [100.0, 150.0, 50.0],
            '成交总额': [1050.0, 1590.0, 1760.0],
            '成交总额/流通市值': [0.1, 0.15, 0.05]
        })
        mock_dzjy.return_value = mock_data
        
        result = provider.get_block_deal_summary('2024-01-01', '2024-12-31', 'stock')
        
        assert not result.empty
        assert 'symbol' in result.columns
        assert 'deal_count' in result.columns
        assert 'total_amount' in result.columns
    
    def test_invalid_group_by(self, provider):
        """Test invalid group_by parameter."""
        with pytest.raises(ValueError, match="Invalid group_by"):
            provider.get_block_deal_summary('2024-01-01', '2024-12-31', 'invalid')


class TestBlockDealPublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_dzjy_mrtj')
    def test_get_block_deal_api(self, mock_dzjy):
        """Test get_block_deal public API."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '交易日期': ['2024-01-15'],
            '证券代码': ['600000'],
            '证券简称': ['浦发银行'],
            '涨跌幅': [1.0],
            '收盘价': [10.45],
            '成交价': [10.50],
            '折溢率': [0.48],
            '成交笔数': [5],
            '成交总量': [100.0],
            '成交总额': [1050.0],
            '成交总额/流通市值': [0.1]
        })
        mock_dzjy.return_value = mock_data
        
        result = get_block_deal('600000', start_date='2024-01-01')
        assert not result.empty
