"""
Unit tests for Northbound module.

This test suite covers:
1. Unit tests for all 3 public functions
2. Parameter validation tests
3. JSON compatibility tests
4. Provider functionality tests
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks,
    NorthboundFactory,
)
from akshare_one.modules.northbound.base import NorthboundProvider
from akshare_one.modules.northbound.eastmoney import EastmoneyNorthboundProvider


# ============================================================================
# Unit Tests - Provider Basics
# ============================================================================

class TestProviderBasics:
    """Test basic provider functionality."""
    
    def test_provider_initialization(self):
        """Test provider can be initialized."""
        provider = EastmoneyNorthboundProvider()
        assert provider is not None
        assert isinstance(provider, NorthboundProvider)
    
    def test_provider_metadata(self):
        """Test provider metadata properties."""
        provider = EastmoneyNorthboundProvider()
        metadata = provider.metadata
        
        assert 'source' in metadata
        assert metadata['source'] == 'eastmoney'
        assert 'data_type' in metadata
        assert metadata['data_type'] == 'northbound'
        assert 'update_frequency' in metadata
        assert metadata['update_frequency'] == 'daily'
        assert 'delay_minutes' in metadata
        assert metadata['delay_minutes'] == 1440  # T+1


# ============================================================================
# Unit Tests - Parameter Validation
# ============================================================================

class TestParameterValidation:
    """Test parameter validation for all functions."""
    
    def test_valid_date_range(self):
        """Test with valid date range."""
        provider = EastmoneyNorthboundProvider()
        # Should not raise
        provider.validate_date_range('2024-01-01', '2024-01-31')
    
    def test_invalid_date_format(self):
        """Test with invalid date formats."""
        provider = EastmoneyNorthboundProvider()
        
        with pytest.raises(ValueError, match="Invalid.*format"):
            provider.validate_date_range('2024/01/01', '2024-01-31')
        
        with pytest.raises(ValueError, match="Invalid.*format"):
            provider.validate_date_range('2024-01-01', 'invalid')
    
    def test_invalid_date_range_order(self):
        """Test with start_date > end_date."""
        provider = EastmoneyNorthboundProvider()
        
        with pytest.raises(ValueError, match="start_date.*must be.*end_date"):
            provider.validate_date_range('2024-01-31', '2024-01-01')
    
    def test_valid_symbol(self):
        """Test with valid 6-digit symbol."""
        provider = EastmoneyNorthboundProvider()
        # Should not raise
        provider.validate_symbol('600000')
        provider.validate_symbol('000001')
    
    def test_invalid_symbol_format(self):
        """Test with invalid symbol formats."""
        provider = EastmoneyNorthboundProvider()
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.validate_symbol('INVALID')
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.validate_symbol('12345')
    
    def test_invalid_market_parameter(self):
        """Test with invalid market parameter."""
        provider = EastmoneyNorthboundProvider()
        
        with pytest.raises(ValueError, match="Invalid market"):
            provider.get_northbound_flow('2024-01-01', '2024-01-31', 'invalid')
    
    def test_invalid_top_n_parameter(self):
        """Test with invalid top_n parameter."""
        provider = EastmoneyNorthboundProvider()
        
        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_northbound_top_stocks('2024-01-01', 'all', -1)
        
        with pytest.raises(ValueError, match="top_n must be positive"):
            provider.get_northbound_top_stocks('2024-01-01', 'all', 0)


# ============================================================================
# Unit Tests - Factory Pattern
# ============================================================================

class TestFactory:
    """Test factory pattern implementation."""
    
    def test_factory_get_provider(self):
        """Test factory can create provider."""
        provider = NorthboundFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyNorthboundProvider)
    
    def test_factory_unsupported_source(self):
        """Test factory raises error for unsupported source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            NorthboundFactory.get_provider('unsupported')
    
    def test_factory_list_sources(self):
        """Test factory can list available sources."""
        sources = NorthboundFactory.list_sources()
        assert isinstance(sources, list)
        assert 'eastmoney' in sources
    
    def test_factory_register_provider(self):
        """Test factory can register new provider."""
        class CustomProvider(NorthboundProvider):
            def get_source_name(self):
                return 'custom'
            def get_data_type(self):
                return 'northbound'
            def fetch_data(self):
                return pd.DataFrame()
            def get_northbound_flow(self, start_date, end_date, market):
                return pd.DataFrame()
            def get_northbound_holdings(self, symbol, start_date, end_date):
                return pd.DataFrame()
            def get_northbound_top_stocks(self, date, market, top_n):
                return pd.DataFrame()
        
        NorthboundFactory.register_provider('custom', CustomProvider)
        assert 'custom' in NorthboundFactory.list_sources()
        
        provider = NorthboundFactory.get_provider('custom')
        assert isinstance(provider, CustomProvider)
    
    def test_factory_register_invalid_provider(self):
        """Test factory rejects invalid provider class."""
        class InvalidProvider:
            pass
        
        with pytest.raises(TypeError, match="must inherit from NorthboundProvider"):
            NorthboundFactory.register_provider('invalid', InvalidProvider)


# ============================================================================
# Unit Tests - JSON Compatibility
# ============================================================================

class TestJSONCompatibility:
    """Test JSON compatibility of returned data."""
    
    def test_ensure_json_compatible_handles_nan(self):
        """Test that NaN values are replaced with None."""
        provider = EastmoneyNorthboundProvider()
        
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'value': [np.nan]
        })
        
        result = provider.ensure_json_compatible(df)
        assert result['value'][0] is None
    
    def test_ensure_json_compatible_handles_infinity(self):
        """Test that Infinity values are replaced with None."""
        provider = EastmoneyNorthboundProvider()
        
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'value': [np.inf]
        })
        
        result = provider.ensure_json_compatible(df)
        assert result['value'][0] is None
    
    def test_ensure_json_compatible_handles_datetime(self):
        """Test that datetime columns are converted to strings."""
        provider = EastmoneyNorthboundProvider()
        
        df = pd.DataFrame({
            'date': [pd.Timestamp('2024-01-01')]
        })
        
        result = provider.ensure_json_compatible(df)
        assert result['date'][0] == '2024-01-01'
        assert isinstance(result['date'][0], str)
    
    def test_ensure_json_compatible_handles_symbol(self):
        """Test that symbol columns preserve leading zeros."""
        provider = EastmoneyNorthboundProvider()
        
        df = pd.DataFrame({
            'symbol': ['600000', '000001']
        })
        
        result = provider.ensure_json_compatible(df)
        assert result['symbol'][0] == '600000'
        assert result['symbol'][1] == '000001'
        assert isinstance(result['symbol'][0], str)


# ============================================================================
# Unit Tests - Empty Results
# ============================================================================

class TestEmptyResults:
    """Test handling of empty results."""
    
    def test_create_empty_dataframe(self):
        """Test creating empty DataFrame with correct columns."""
        provider = EastmoneyNorthboundProvider()
        
        columns = ['date', 'market', 'net_buy']
        df = provider.create_empty_dataframe(columns)
        
        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert list(df.columns) == columns
    
    @patch('akshare.stock_hsgt_hist_em')
    def test_get_northbound_flow_empty_result(self, mock_ak):
        """Test get_northbound_flow returns empty DataFrame with correct structure."""
        mock_ak.return_value = pd.DataFrame()
        
        provider = EastmoneyNorthboundProvider()
        result = provider.get_northbound_flow('2024-01-01', '2024-01-31', 'all')
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        expected_columns = ['date', 'market', 'net_buy', 'buy_amount', 'sell_amount', 'balance']
        assert list(result.columns) == expected_columns


# ============================================================================
# Unit Tests - Public Functions
# ============================================================================

class TestPublicFunctions:
    """Test public API functions."""
    
    @patch('akshare.stock_hsgt_hist_em')
    def test_get_northbound_flow(self, mock_ak):
        """Test get_northbound_flow function."""
        # Mock akshare response
        mock_df = pd.DataFrame({
            '日期': ['2024-01-01', '2024-01-02'],
            '沪股通(亿元)': [10.5, 20.3],
            '深股通(亿元)': [5.2, 8.7],
            '北向资金(亿元)': [15.7, 29.0]
        })
        mock_ak.return_value = mock_df
        
        result = get_northbound_flow(start_date='2024-01-01', end_date='2024-01-31', market='all')
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'date' in result.columns
        assert 'market' in result.columns
        assert 'net_buy' in result.columns
    
    @patch('akshare.stock_hsgt_individual_em')
    def test_get_northbound_holdings_with_symbol(self, mock_ak):
        """Test get_northbound_holdings with specific symbol."""
        # Mock akshare response
        mock_df = pd.DataFrame({
            '日期': ['2024-01-01'],
            '持股数量': [1000000],
            '持股市值': [50000000],
            '持股占比': [2.5]
        })
        mock_ak.return_value = mock_df
        
        result = get_northbound_holdings(symbol='600000', start_date='2024-01-01', end_date='2024-01-31')
        
        assert isinstance(result, pd.DataFrame)
        assert 'date' in result.columns
        assert 'symbol' in result.columns
        assert 'holdings_shares' in result.columns
    
    @patch('akshare.stock_hsgt_board_rank_em')
    def test_get_northbound_top_stocks(self, mock_ak):
        """Test get_northbound_top_stocks function."""
        # Mock akshare response
        mock_df = pd.DataFrame({
            '代码': ['600000', '000001'],
            '名称': ['浦发银行', '平安银行'],
            '今日持股': [1000000, 800000],
            '持股数量': [50000000, 40000000],
            '持股占比': [2.5, 2.0]
        })
        mock_ak.return_value = mock_df
        
        result = get_northbound_top_stocks(date='2024-01-01', market='all', top_n=10)
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'rank' in result.columns
        assert 'symbol' in result.columns
        assert 'name' in result.columns
        assert len(result) <= 10


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
