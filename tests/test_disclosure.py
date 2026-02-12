"""
Unit tests for disclosure module.

Tests the disclosure data provider implementations including:
- Dividend data fetching and standardization
- Repurchase data fetching and standardization
- ST/delist risk data fetching and standardization
- Factory pattern
- JSON compatibility
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.akshare_one.modules.disclosure.factory import DisclosureFactory
from src.akshare_one.modules.disclosure.eastmoney import EastmoneyDisclosureProvider
from src.akshare_one.modules.disclosure import (
    get_dividend_data,
    get_repurchase_data,
    get_st_delist_data,
)


class TestDisclosureFactory:
    """Test DisclosureFactory class."""
    
    def test_get_provider_eastmoney(self):
        """Test getting Eastmoney provider."""
        provider = DisclosureFactory.get_provider(source='eastmoney')
        assert isinstance(provider, EastmoneyDisclosureProvider)
        assert provider.get_source_name() == 'eastmoney'
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            DisclosureFactory.get_provider(source='invalid')
    
    def test_get_available_sources(self):
        """Test getting available sources."""
        sources = DisclosureFactory.get_available_sources()
        assert isinstance(sources, list)
        assert 'eastmoney' in sources


class TestEastmoneyDisclosureProvider:
    """Test EastmoneyDisclosureProvider class."""
    
    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = EastmoneyDisclosureProvider()
        assert provider.get_source_name() == 'eastmoney'
        assert provider.get_data_type() == 'disclosure'
        assert provider.get_update_frequency() == 'realtime'
        assert provider.get_delay_minutes() == 60
    
    @patch('akshare.stock_dividend_cninfo')
    def test_get_dividend_data_single_stock(self, mock_ak):
        """Test getting dividend data for a single stock."""
        # Mock akshare response
        mock_df = pd.DataFrame({
            '报告时间': ['2023年报', '2022年报'],
            '派息比例': [1.5, 1.0],
            '股权登记日': ['2024-06-20', '2023-06-15'],
            '除权日': ['2024-06-21', '2023-06-16'],
            '派息日': ['2024-06-22', '2023-06-17'],
        })
        mock_ak.return_value = mock_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_dividend_data('600000', '2023-01-01', '2024-12-31')
        
        # Verify result structure
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == [
            'symbol', 'fiscal_year', 'dividend_per_share',
            'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio'
        ]
        
        # Verify data
        assert len(result) == 2
        assert result['symbol'].iloc[0] == '600000'
        assert result['dividend_per_share'].iloc[0] == 0.15  # 1.5 / 10
        assert result['ex_dividend_date'].iloc[0] == '2024-06-21'
    
    @patch('akshare.stock_dividend_cninfo')
    def test_get_dividend_data_empty_result(self, mock_ak):
        """Test getting dividend data with empty result."""
        mock_ak.return_value = pd.DataFrame()
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_dividend_data('600000', '2023-01-01', '2024-12-31')
        
        # Should return empty DataFrame with correct structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == [
            'symbol', 'fiscal_year', 'dividend_per_share',
            'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio'
        ]
    
    @patch('akshare.stock_dividend_cninfo')
    def test_get_dividend_data_json_compatibility(self, mock_ak):
        """Test dividend data JSON compatibility."""
        mock_df = pd.DataFrame({
            '报告时间': ['2023年报'],
            '派息比例': [1.5],
            '股权登记日': ['2024-06-20'],
            '除权日': ['2024-06-21'],
            '派息日': [pd.NaT],  # Test NaT handling
        })
        mock_ak.return_value = mock_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_dividend_data('600000', '2023-01-01', '2024-12-31')
        
        # Test JSON serialization
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Verify no NaN/Infinity
        assert not result.isnull().any().any() or result['payment_date'].isnull().all()
    
    @patch('akshare.stock_repurchase_em')
    def test_get_repurchase_data_all_stocks(self, mock_ak):
        """Test getting repurchase data for all stocks."""
        # Mock akshare response
        mock_df = pd.DataFrame({
            '股票代码': ['600000', '000001'],
            '最新公告日期': ['2024-01-15', '2024-01-10'],
            '实施进度': ['进行中', '已完成'],
            '已回购金额': [50000000.0, 100000000.0],
            '已回购股份数量': [1000000.0, 2000000.0],
            '计划回购价格区间': ['10-15元', '20-25元'],
            '计划回购金额区间-下限': [40000000.0, 80000000.0],
        })
        mock_ak.return_value = mock_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_repurchase_data(None, '2024-01-01', '2024-12-31')
        
        # Verify result structure
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == [
            'symbol', 'announcement_date', 'progress',
            'amount', 'quantity', 'price_range'
        ]
        
        # Verify data
        assert len(result) == 2
        assert result['symbol'].iloc[0] == '600000'
        assert result['announcement_date'].iloc[0] == '2024-01-15'
        assert result['progress'].iloc[0] == '进行中'
        assert result['amount'].iloc[0] == 50000000.0
    
    @patch('akshare.stock_repurchase_em')
    def test_get_repurchase_data_single_stock(self, mock_ak):
        """Test getting repurchase data for a single stock."""
        mock_df = pd.DataFrame({
            '股票代码': ['600000', '000001'],
            '最新公告日期': ['2024-01-15', '2024-01-10'],
            '实施进度': ['进行中', '已完成'],
            '已回购金额': [50000000.0, 100000000.0],
            '已回购股份数量': [1000000.0, 2000000.0],
            '计划回购价格区间': ['10-15元', '20-25元'],
            '计划回购金额区间-下限': [40000000.0, 80000000.0],
        })
        mock_ak.return_value = mock_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_repurchase_data('600000', '2024-01-01', '2024-12-31')
        
        # Should only return data for 600000
        assert len(result) == 1
        assert result['symbol'].iloc[0] == '600000'
    
    @patch('akshare.stock_repurchase_em')
    def test_get_repurchase_data_date_filter(self, mock_ak):
        """Test repurchase data date filtering."""
        mock_df = pd.DataFrame({
            '股票代码': ['600000', '000001'],
            '最新公告日期': ['2024-01-15', '2023-12-10'],
            '实施进度': ['进行中', '已完成'],
            '已回购金额': [50000000.0, 100000000.0],
            '已回购股份数量': [1000000.0, 2000000.0],
            '计划回购价格区间': ['10-15元', '20-25元'],
            '计划回购金额区间-下限': [40000000.0, 80000000.0],
        })
        mock_ak.return_value = mock_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_repurchase_data(None, '2024-01-01', '2024-12-31')
        
        # Should only return data within date range
        assert len(result) == 1
        assert result['announcement_date'].iloc[0] == '2024-01-15'
    
    @patch('akshare.stock_info_sh_delist')
    @patch('akshare.stock_info_sz_delist')
    def test_get_st_delist_data_all_stocks(self, mock_sz, mock_sh):
        """Test getting ST/delist data for all stocks."""
        # Mock SH data
        mock_sh_df = pd.DataFrame({
            '公司代码': ['600001', '600002'],
            '公司简称': ['*ST华谊', 'ST海润'],
            '暂停上市日期': ['2024-01-15', '2024-02-20'],
        })
        mock_sh.return_value = mock_sh_df
        
        # Mock SZ data
        mock_sz_df = pd.DataFrame({
            '证券代码': ['000001'],
            '证券简称': ['S*ST昌鱼'],
            '终止上市日期': ['2024-03-10'],
        })
        mock_sz.return_value = mock_sz_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_st_delist_data(None)
        
        # Verify result structure
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == [
            'symbol', 'name', 'st_type', 'risk_level', 'announcement_date'
        ]
        
        # Verify data
        assert len(result) == 3
        assert '600001' in result['symbol'].values
        assert '000001' in result['symbol'].values
    
    @patch('akshare.stock_info_sh_delist')
    @patch('akshare.stock_info_sz_delist')
    def test_get_st_delist_data_single_stock(self, mock_sz, mock_sh):
        """Test getting ST/delist data for a single stock."""
        mock_sh_df = pd.DataFrame({
            '公司代码': ['600001', '600002'],
            '公司简称': ['*ST华谊', 'ST海润'],
            '暂停上市日期': ['2024-01-15', '2024-02-20'],
        })
        mock_sh.return_value = mock_sh_df
        
        mock_sz_df = pd.DataFrame()
        mock_sz.return_value = mock_sz_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_st_delist_data('600001')
        
        # Should only return data for 600001
        assert len(result) == 1
        assert result['symbol'].iloc[0] == '600001'
        assert result['st_type'].iloc[0] == '*ST'
        assert result['risk_level'].iloc[0] == 'high'
    
    @patch('akshare.stock_info_sh_delist')
    @patch('akshare.stock_info_sz_delist')
    def test_get_st_delist_data_risk_levels(self, mock_sz, mock_sh):
        """Test ST/delist data risk level classification."""
        mock_sh_df = pd.DataFrame({
            '公司代码': ['600001', '600002', '600003'],
            '公司简称': ['*ST华谊', 'ST海润', '退市大控'],
            '暂停上市日期': ['2024-01-15', '2024-02-20', '2024-03-10'],
        })
        mock_sh.return_value = mock_sh_df
        
        mock_sz_df = pd.DataFrame()
        mock_sz.return_value = mock_sz_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_st_delist_data(None)
        
        # Verify risk levels
        assert result[result['symbol'] == '600001']['risk_level'].iloc[0] == 'high'  # *ST
        assert result[result['symbol'] == '600002']['risk_level'].iloc[0] == 'medium'  # ST
        assert result[result['symbol'] == '600003']['risk_level'].iloc[0] == 'critical'  # 退市


class TestDisclosurePublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_dividend_cninfo')
    def test_get_dividend_data_api(self, mock_ak):
        """Test get_dividend_data public API."""
        mock_df = pd.DataFrame({
            '报告时间': ['2023年报'],
            '派息比例': [1.5],
            '股权登记日': ['2024-06-20'],
            '除权日': ['2024-06-21'],
            '派息日': ['2024-06-22'],
        })
        mock_ak.return_value = mock_df
        
        result = get_dividend_data('600000', start_date='2023-01-01', end_date='2024-12-31')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'symbol' in result.columns
        assert 'dividend_per_share' in result.columns
    
    @patch('akshare.stock_repurchase_em')
    def test_get_repurchase_data_api(self, mock_ak):
        """Test get_repurchase_data public API."""
        mock_df = pd.DataFrame({
            '股票代码': ['600000'],
            '最新公告日期': ['2024-01-15'],
            '实施进度': ['进行中'],
            '已回购金额': [50000000.0],
            '已回购股份数量': [1000000.0],
            '计划回购价格区间': ['10-15元'],
            '计划回购金额区间-下限': [40000000.0],
        })
        mock_ak.return_value = mock_df
        
        result = get_repurchase_data('600000', start_date='2024-01-01', end_date='2024-12-31')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'symbol' in result.columns
        assert 'progress' in result.columns
    
    @patch('akshare.stock_info_sh_delist')
    @patch('akshare.stock_info_sz_delist')
    def test_get_st_delist_data_api(self, mock_sz, mock_sh):
        """Test get_st_delist_data public API."""
        mock_sh_df = pd.DataFrame({
            '公司代码': ['600001'],
            '公司简称': ['*ST华谊'],
            '暂停上市日期': ['2024-01-15'],
        })
        mock_sh.return_value = mock_sh_df
        mock_sz.return_value = pd.DataFrame()
        
        result = get_st_delist_data('600001')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'symbol' in result.columns
        assert 'st_type' in result.columns
        assert 'risk_level' in result.columns


class TestDisclosureDataValidation:
    """Test data validation in disclosure module."""
    
    def test_invalid_symbol_format(self):
        """Test validation with invalid symbol format."""
        provider = EastmoneyDisclosureProvider()
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.get_dividend_data('INVALID', '2024-01-01', '2024-12-31')
    
    def test_invalid_date_format(self):
        """Test validation with invalid date format."""
        provider = EastmoneyDisclosureProvider()
        
        with pytest.raises(ValueError, match="Invalid start_date format"):
            provider.get_dividend_data('600000', '2024/01/01', '2024-12-31')
    
    def test_invalid_date_range(self):
        """Test validation with invalid date range."""
        provider = EastmoneyDisclosureProvider()
        
        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            provider.get_dividend_data('600000', '2024-12-31', '2024-01-01')


class TestDisclosureJSONCompatibility:
    """Test JSON compatibility of disclosure data."""
    
    @patch('akshare.stock_dividend_cninfo')
    def test_dividend_data_json_serialization(self, mock_ak):
        """Test dividend data can be serialized to JSON."""
        mock_df = pd.DataFrame({
            '报告时间': ['2023年报'],
            '派息比例': [1.5],
            '股权登记日': ['2024-06-20'],
            '除权日': ['2024-06-21'],
            '派息日': ['2024-06-22'],
        })
        mock_ak.return_value = mock_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_dividend_data('600000', '2023-01-01', '2024-12-31')
        
        # Should be able to serialize to JSON
        json_str = result.to_json(orient='records')
        assert json_str is not None
        assert 'NaN' not in json_str
        assert 'Infinity' not in json_str
    
    @patch('akshare.stock_repurchase_em')
    def test_repurchase_data_json_serialization(self, mock_ak):
        """Test repurchase data can be serialized to JSON."""
        mock_df = pd.DataFrame({
            '股票代码': ['600000'],
            '最新公告日期': ['2024-01-15'],
            '实施进度': ['进行中'],
            '已回购金额': [50000000.0],
            '已回购股份数量': [1000000.0],
            '计划回购价格区间': ['10-15元'],
            '计划回购金额区间-下限': [40000000.0],
        })
        mock_ak.return_value = mock_df
        
        provider = EastmoneyDisclosureProvider()
        result = provider.get_repurchase_data('600000', '2024-01-01', '2024-12-31')
        
        # Should be able to serialize to JSON
        json_str = result.to_json(orient='records')
        assert json_str is not None
        assert 'NaN' not in json_str
        assert 'Infinity' not in json_str
