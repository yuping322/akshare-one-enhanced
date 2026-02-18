"""
Unit tests for goodwill (商誉) data module.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.goodwill import (
    get_goodwill_by_industry,
    get_goodwill_data,
    get_goodwill_impairment,
)
from akshare_one.modules.goodwill.eastmoney import EastmoneyGoodwillProvider
from akshare_one.modules.goodwill.factory import GoodwillFactory


class TestGoodwillFactory:
    """Test GoodwillFactory class."""
    
    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = GoodwillFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyGoodwillProvider)
    
    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            GoodwillFactory.get_provider('invalid')
    
    def test_list_sources(self):
        """Test listing available sources."""
        sources = GoodwillFactory.list_sources()
        assert 'eastmoney' in sources


class TestEastmoneyGoodwillProvider:
    """Test EastmoneyGoodwillProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyGoodwillProvider()
    
    def test_metadata(self, provider):
        """Test provider metadata."""
        assert provider.get_data_type() == 'goodwill'
        assert provider.get_source_name() == 'eastmoney'
        assert provider.get_update_frequency() == 'quarterly'
        assert provider.get_delay_minutes() == 43200
    
    @patch('akshare.stock_sy_profile_em')
    def test_get_goodwill_data_all_stocks(self, mock_goodwill, provider):
        """Test getting goodwill data for all stocks."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036'],
            '股票简称': ['浦发银行', '招商银行'],
            '报告期': ['2024-09-30', '2024-09-30'],
            '商誉': [1000000000.0, 2000000000.0],
            '商誉占净资产比例': [5.5, 8.2],
            '商誉减值': [10000000.0, 20000000.0]
        })
        mock_goodwill.return_value = mock_data
        
        result = provider.get_goodwill_data(None, '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert len(result) == 2
        assert 'symbol' in result.columns
        assert 'report_date' in result.columns
        assert 'goodwill_balance' in result.columns
        assert 'goodwill_ratio' in result.columns
        assert 'goodwill_impairment' in result.columns
        assert result['symbol'].iloc[0] == '600000'
        assert result['goodwill_balance'].iloc[0] == 1000000000.0
        assert result['goodwill_ratio'].iloc[0] == 5.5
    
    @patch('akshare.stock_financial_abstract_ths')
    def test_get_goodwill_data_single_stock(self, mock_goodwill, provider):
        """Test getting goodwill data for a single stock."""
        mock_data = pd.DataFrame({
            '报告期': ['2024-09-30', '2024-06-30'],
            '商誉': [1000000000.0, 1100000000.0],
            '商誉减值': [10000000.0, 5000000.0]
        })
        mock_goodwill.return_value = mock_data
        
        result = provider.get_goodwill_data('600000', '2024-01-01', '2024-12-31')
        
        assert not result.empty
        assert len(result) == 2
        assert 'symbol' in result.columns
        assert 'report_date' in result.columns
        assert 'goodwill_balance' in result.columns
        assert result['symbol'].iloc[0] == '600000'
    
    @patch('akshare.stock_financial_abstract_ths')
    def test_get_goodwill_data_empty(self, mock_goodwill, provider):
        """Test getting goodwill data with no data."""
        mock_goodwill.return_value = pd.DataFrame()
        
        result = provider.get_goodwill_data('600000', '2024-01-01', '2024-12-31')
        
        assert result.empty
        assert 'symbol' in result.columns
        assert 'report_date' in result.columns
    
    @patch('akshare.stock_sy_jz_em')
    def test_get_goodwill_impairment(self, mock_impairment, provider):
        """Test getting goodwill impairment expectations."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036', '000001'],
            '股票简称': ['浦发银行', '招商银行', '平安银行'],
            '商誉': [1000000000.0, 2000000000.0, 500000000.0],
            '预计商誉减值': [600000000.0, 500000000.0, 50000000.0]
        })
        mock_impairment.return_value = mock_data
        
        result = provider.get_goodwill_impairment('2024-12-31')
        
        assert not result.empty
        assert len(result) == 3
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert 'goodwill_balance' in result.columns
        assert 'expected_impairment' in result.columns
        assert 'risk_level' in result.columns
        
        # Check risk level calculation
        # 600000: 600M/1000M = 60% -> high
        # 600036: 500M/2000M = 25% -> medium
        # 000001: 50M/500M = 10% -> low
        assert result[result['symbol'] == '600000']['risk_level'].iloc[0] == 'high'
        assert result[result['symbol'] == '600036']['risk_level'].iloc[0] == 'medium'
        assert result[result['symbol'] == '000001']['risk_level'].iloc[0] == 'low'
    
    @patch('akshare.stock_sy_jz_em')
    def test_get_goodwill_impairment_empty(self, mock_impairment, provider):
        """Test getting goodwill impairment with no data."""
        mock_impairment.return_value = pd.DataFrame()
        
        result = provider.get_goodwill_impairment('2024-12-31')
        
        assert result.empty
        assert 'symbol' in result.columns
        assert 'risk_level' in result.columns
    
    @patch('akshare.stock_sy_profile_em')
    def test_get_goodwill_by_industry(self, mock_goodwill, provider):
        """Test getting goodwill statistics by industry."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036', '000001', '000002'],
            '商誉': [1000000000.0, 2000000000.0, 500000000.0, 800000000.0],
            '商誉占净资产比例': [5.5, 8.2, 3.0, 6.5],
            '商誉减值': [10000000.0, 20000000.0, 5000000.0, 8000000.0],
            '所属行业': ['银行', '银行', '银行', '证券']
        })
        mock_goodwill.return_value = mock_data
        
        result = provider.get_goodwill_by_industry('2024-12-31')
        
        assert not result.empty
        assert 'industry' in result.columns
        assert 'total_goodwill' in result.columns
        assert 'avg_ratio' in result.columns
        assert 'total_impairment' in result.columns
        assert 'company_count' in result.columns
        
        # Check banking industry stats
        banking = result[result['industry'] == '银行'].iloc[0]
        assert banking['company_count'] == 3
        assert banking['total_goodwill'] == 3500000000.0
        assert banking['total_impairment'] == 35000000.0
    
    @patch('akshare.stock_sy_profile_em')
    def test_get_goodwill_by_industry_empty(self, mock_goodwill, provider):
        """Test getting goodwill by industry with no data."""
        mock_goodwill.return_value = pd.DataFrame()
        
        result = provider.get_goodwill_by_industry('2024-12-31')
        
        assert result.empty
        assert 'industry' in result.columns
    
    def test_invalid_date_format(self, provider):
        """Test with invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            provider.get_goodwill_impairment('2024/12/31')


class TestGoodwillPublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_financial_abstract_ths')
    def test_get_goodwill_data_api(self, mock_goodwill):
        """Test get_goodwill_data public API."""
        mock_data = pd.DataFrame({
            '报告期': ['2024-09-30'],
            '商誉': [1000000000.0],
            '商誉减值': [10000000.0]
        })
        mock_goodwill.return_value = mock_data
        
        result = get_goodwill_data('600000', start_date='2024-01-01', end_date='2024-12-31')
        assert not result.empty
        assert 'symbol' in result.columns
    
    @patch('akshare.stock_sy_jz_em')
    def test_get_goodwill_impairment_api(self, mock_impairment):
        """Test get_goodwill_impairment public API."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000'],
            '股票简称': ['浦发银行'],
            '商誉': [1000000000.0],
            '预计商誉减值': [100000000.0]
        })
        mock_impairment.return_value = mock_data
        
        result = get_goodwill_impairment('2024-12-31')
        assert not result.empty
        assert 'risk_level' in result.columns
    
    @patch('akshare.stock_sy_profile_em')
    def test_get_goodwill_by_industry_api(self, mock_goodwill):
        """Test get_goodwill_by_industry public API."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000', '600036'],
            '商誉': [1000000000.0, 2000000000.0],
            '商誉占净资产比例': [5.5, 8.2],
            '商誉减值': [10000000.0, 20000000.0],
            '所属行业': ['银行', '银行']
        })
        mock_goodwill.return_value = mock_data
        
        result = get_goodwill_by_industry('2024-12-31')
        assert not result.empty
        assert 'industry' in result.columns


class TestGoodwillJSONCompatibility:
    """Test JSON compatibility of goodwill data."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return EastmoneyGoodwillProvider()
    
    @patch('akshare.stock_sy_profile_em')
    def test_json_compatibility(self, mock_goodwill, provider):
        """Test that output is JSON compatible."""
        mock_data = pd.DataFrame({
            '股票代码': ['600000'],
            '报告期': ['2024-09-30'],
            '商誉': [1000000000.0],
            '商誉占净资产比例': [5.5],
            '商誉减值': [10000000.0]
        })
        mock_goodwill.return_value = mock_data
        
        result = provider.get_goodwill_data(None, '2024-01-01', '2024-12-31')
        
        # Test JSON serialization
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Check no NaN values
        assert not result.isnull().any().any()
        
        # Check symbol is string with leading zeros
        assert result['symbol'].dtype in ['object', 'string']
        assert result['symbol'].iloc[0] == '600000'
