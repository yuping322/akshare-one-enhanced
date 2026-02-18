"""
Unit tests for limit up/down (涨停池) data module.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.limitup import (
    get_limit_down_pool,
    get_limit_up_pool,
    get_limit_up_stats,
)
from akshare_one.modules.limitup.eastmoney import EastmoneyLimitUpDownProvider
from akshare_one.modules.limitup.factory import LimitUpDownFactory


class TestLimitUpDownFactory:
    """Test LimitUpDownFactory class."""
    
    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = LimitUpDownFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyLimitUpDownProvider)
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            LimitUpDownFactory.get_provider('invalid')
    
    def test_list_sources(self):
        """Test listing available sources."""
        sources = LimitUpDownFactory.list_sources()
        assert 'eastmoney' in sources


class TestEastmoneyLimitUpDownProvider:
    """Test EastmoneyLimitUpDownProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyLimitUpDownProvider()
    
    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == 'limitup'
        assert provider.get_source_name() == 'eastmoney'
        assert provider.get_update_frequency() == 'realtime'
        assert provider.get_delay_minutes() == 0
    
    @patch('akshare.stock_zt_pool_em')
    def test_get_limit_up_pool(self, mock_zt, provider):
        """Test getting limit up pool data."""
        mock_data = pd.DataFrame({
            '序号': [1, 2],
            '代码': ['600000', '600036'],
            '名称': ['浦发银行', '招商银行'],
            '最新价': [10.50, 35.20],
            '涨停时间': ['09:30:00', '09:35:00'],
            '打开次数': [0, 1],
            '封单金额': [50000000.0, 80000000.0],
            '连板数': [1, 2],
            '涨停原因': ['板块联动', '业绩预增'],
            '换手率': [5.5, 8.2]
        })
        mock_zt.return_value = mock_data
        
        result = provider.get_limit_up_pool('2024-01-02')
        
        assert not result.empty
        assert len(result) == 2
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert 'close_price' in result.columns
        assert 'limit_up_time' in result.columns
        assert 'open_count' in result.columns
        assert 'seal_amount' in result.columns
        assert 'consecutive_days' in result.columns
        assert 'reason' in result.columns
        assert 'turnover_rate' in result.columns
        assert result['symbol'].iloc[0] == '600000'
        assert result['date'].iloc[0] == '2024-01-02'
    
    @patch('akshare.stock_zt_pool_em')
    def test_get_limit_up_pool_empty(self, mock_zt, provider):
        """Test getting limit up pool with no data."""
        mock_zt.return_value = pd.DataFrame()
        
        result = provider.get_limit_up_pool('2024-01-02')
        
        assert result.empty
        assert 'date' in result.columns
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_zt_pool_dtgc_em')
    def test_get_limit_down_pool(self, mock_dt, provider):
        """Test getting limit down pool data."""
        mock_data = pd.DataFrame({
            '序号': [1, 2],
            '代码': ['600000', '600036'],
            '名称': ['浦发银行', '招商银行'],
            '最新价': [9.50, 31.80],
            '跌停时间': ['09:30:00', '09:35:00'],
            '打开次数': [0, 1],
            '换手率': [3.5, 6.2]
        })
        mock_dt.return_value = mock_data
        
        result = provider.get_limit_down_pool('2024-01-02')
        
        assert not result.empty
        assert len(result) == 2
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert 'close_price' in result.columns
        assert 'limit_down_time' in result.columns
        assert 'open_count' in result.columns
        assert 'turnover_rate' in result.columns
        assert result['symbol'].iloc[0] == '600000'
    
    @patch('akshare.stock_zt_pool_dtgc_em')
    def test_get_limit_down_pool_empty(self, mock_dt, provider):
        """Test getting limit down pool with no data."""
        mock_dt.return_value = pd.DataFrame()
        
        result = provider.get_limit_down_pool('2024-01-02')
        
        assert result.empty
        assert 'date' in result.columns
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_zt_pool_em')
    @patch('akshare.stock_zt_pool_dtgc_em')
    def test_get_limit_up_stats(self, mock_dt, mock_zt, provider):
        """Test getting limit up/down statistics."""
        # Mock limit up data
        mock_zt_data = pd.DataFrame({
            '序号': [1, 2, 3],
            '代码': ['600000', '600036', '600050'],
            '名称': ['浦发银行', '招商银行', '中国联通'],
            '最新价': [10.50, 35.20, 5.50],
            '涨停时间': ['09:30:00', '09:35:00', '10:00:00'],
            '打开次数': [0, 1, 0],
            '换手率': [5.5, 8.2, 3.0]
        })
        mock_zt.return_value = mock_zt_data
        
        # Mock limit down data
        mock_dt_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600001'],
            '名称': ['邯郸钢铁'],
            '最新价': [4.50],
            '跌停时间': ['09:30:00'],
            '打开次数': [0],
            '换手率': [2.5]
        })
        mock_dt.return_value = mock_dt_data
        
        result = provider.get_limit_up_stats('2024-01-02', '2024-01-02')
        
        assert not result.empty
        assert 'date' in result.columns
        assert 'limit_up_count' in result.columns
        assert 'limit_down_count' in result.columns
        assert 'broken_rate' in result.columns
        assert result['limit_up_count'].iloc[0] == 3
        assert result['limit_down_count'].iloc[0] == 1
        # Broken rate should be 1/3 * 100 = 33.33%
        assert result['broken_rate'].iloc[0] > 33.0
        assert result['broken_rate'].iloc[0] < 34.0


class TestLimitUpDownPublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_zt_pool_em')
    def test_get_limit_up_pool_api(self, mock_zt):
        """Test get_limit_up_pool public API."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '最新价': [10.50],
            '涨停时间': ['09:30:00'],
            '打开次数': [0],
            '封单金额': [50000000.0],
            '连板数': [1],
            '涨停原因': ['板块联动'],
            '换手率': [5.5]
        })
        mock_zt.return_value = mock_data
        
        result = get_limit_up_pool('2024-01-02')
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_zt_pool_dtgc_em')
    def test_get_limit_down_pool_api(self, mock_dt):
        """Test get_limit_down_pool public API."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '最新价': [9.50],
            '跌停时间': ['09:30:00'],
            '打开次数': [0],
            '换手率': [3.5]
        })
        mock_dt.return_value = mock_data
        
        result = get_limit_down_pool('2024-01-02')
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_zt_pool_em')
    @patch('akshare.stock_zt_pool_dtgc_em')
    def test_get_limit_up_stats_api(self, mock_dt, mock_zt):
        """Test get_limit_up_stats public API."""
        mock_zt_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '最新价': [10.50],
            '涨停时间': ['09:30:00'],
            '打开次数': [0],
            '换手率': [5.5]
        })
        mock_zt.return_value = mock_zt_data
        
        mock_dt_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600001'],
            '名称': ['邯郸钢铁'],
            '最新价': [4.50],
            '跌停时间': ['09:30:00'],
            '打开次数': [0],
            '换手率': [2.5]
        })
        mock_dt.return_value = mock_dt_data
        
        result = get_limit_up_stats('2024-01-02', '2024-01-02')
        assert not result.empty
        assert 'limit_up_count' in result.columns


class TestLimitUpDownJSONCompatibility:
    """Test JSON compatibility of limit up/down data."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyLimitUpDownProvider()
    
    @patch('akshare.stock_zt_pool_em')
    def test_json_compatibility(self, mock_zt, provider):
        """Test that output is JSON compatible."""
        mock_data = pd.DataFrame({
            '序号': [1],
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '最新价': [10.50],
            '涨停时间': ['09:30:00'],
            '打开次数': [0],
            '封单金额': [50000000.0],
            '连板数': [1],
            '涨停原因': ['板块联动'],
            '换手率': [5.5]
        })
        mock_zt.return_value = mock_data
        
        result = provider.get_limit_up_pool('2024-01-02')
        
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
