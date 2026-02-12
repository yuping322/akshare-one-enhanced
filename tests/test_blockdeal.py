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
    
    @patch('akshare.stock_dzjy_mrmx')
    def test_get_block_deal_single_stock(self, mock_dzjy, provider):
        """Test getting block deal data for single stock."""
        mock_data = pd.DataFrame({
            '交易日期': ['2024-01-15', '2024-01-16'],
            '证券代码': ['600000', '600000'],
            '证券简称': ['浦发银行', '浦发银行'],
            '成交价': [10.50, 10.60],
            '成交量': [1000000, 1500000],
            '成交额': [10500000, 15900000],
            '买方营业部': ['机构专用', '机构专用'],
            '卖方营业部': ['某营业部', '某营业部'],
            '收盘价': [10.45, 10.55]
        })
        mock_dzjy.return_value = mock_data
        
        result = provider.get_block_deal('600000', '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'premium_rate' in result.columns
    
    @patch('akshare.stock_dzjy_sctj')
    def test_get_block_deal_all_stocks(self, mock_dzjy, provider):
        """Test getting block deal data for all stocks."""
        mock_data = pd.DataFrame({
            '交易日期': ['2024-01-15'],
            '证券代码': ['600000'],
            '证券简称': ['浦发银行'],
            '成交价': [10.50],
            '成交量': [1000000],
            '成交额': [10500000],
            '买方营业部': ['机构专用'],
            '卖方营业部': ['某营业部']
        })
        mock_dzjy.return_value = mock_data
        
        result = provider.get_block_deal(None, '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_dzjy_sctj')
    def test_get_block_deal_summary_by_stock(self, mock_dzjy, provider):
        """Test getting block deal summary grouped by stock."""
        mock_data = pd.DataFrame({
            '交易日期': ['2024-01-15', '2024-01-16', '2024-01-15'],
            '证券代码': ['600000', '600000', '600036'],
            '证券简称': ['浦发银行', '浦发银行', '招商银行'],
            '成交价': [10.50, 10.60, 35.20],
            '成交量': [1000000, 1500000, 500000],
            '成交额': [10500000, 15900000, 17600000],
            '买方营业部': ['机构专用', '机构专用', '机构专用'],
            '卖方营业部': ['某营业部', '某营业部', '某营业部'],
            '收盘价': [10.45, 10.55, 35.00]
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
    
    @patch('akshare.stock_dzjy_mrmx')
    def test_get_block_deal_api(self, mock_dzjy):
        """Test get_block_deal public API."""
        mock_data = pd.DataFrame({
            '交易日期': ['2024-01-15'],
            '证券代码': ['600000'],
            '证券简称': ['浦发银行'],
            '成交价': [10.50],
            '成交量': [1000000],
            '成交额': [10500000],
            '买方营业部': ['机构专用'],
            '卖方营业部': ['某营业部']
        })
        mock_dzjy.return_value = mock_data
        
        result = get_block_deal('600000', start_date='2024-01-01')
        assert not result.empty
