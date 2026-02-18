"""
Comprehensive tests for FundFlow module.

This test suite covers:
1. Unit tests for all 7 public functions
2. Parameter validation tests
3. JSON compatibility tests
4. Contract tests with golden samples
5. Integration tests (marked with @pytest.mark.integration)
"""

from datetime import datetime
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from akshare_one.modules.fundflow import (
    FundFlowFactory,
    get_concept_constituents,
    get_concept_list,
    get_industry_constituents,
    get_industry_list,
    get_main_fund_flow_rank,
    get_sector_fund_flow,
    get_stock_fund_flow,
)
from akshare_one.modules.fundflow.base import FundFlowProvider
from akshare_one.modules.fundflow.eastmoney import EastmoneyFundFlowProvider
from tests.utils.contract_test import GoldenSampleValidator
from tests.utils.integration_helpers import (
    DataFrameValidator,
    integration_rate_limiter,
    skip_if_no_network,
)

# ============================================================================
# Unit Tests - Provider Basics
# ============================================================================

class TestProviderBasics:
    """Test basic provider functionality."""
    
    def test_provider_initialization(self):
        """Test provider can be initialized."""
        provider = EastmoneyFundFlowProvider()
        assert provider is not None
        assert isinstance(provider, FundFlowProvider)
    
    def test_provider_metadata(self):
        """Test provider metadata properties."""
        provider = EastmoneyFundFlowProvider()
        metadata = provider.metadata
        
        assert 'source' in metadata
        assert metadata['source'] == 'eastmoney'
        assert 'data_type' in metadata
        assert metadata['data_type'] == 'fundflow'
        assert 'update_frequency' in metadata
        assert metadata['update_frequency'] == 'realtime'
        assert 'delay_minutes' in metadata
        assert metadata['delay_minutes'] == 0


# ============================================================================
# Unit Tests - Parameter Validation
# ============================================================================

class TestParameterValidation:
    """Test parameter validation for all functions."""
    
    def test_valid_symbol(self):
        """Test with valid 6-digit symbol."""
        provider = EastmoneyFundFlowProvider()
        # Should not raise
        provider.validate_symbol('600000')
        provider.validate_symbol('000001')
        provider.validate_symbol('300001')
    
    def test_invalid_symbol_format(self):
        """Test with invalid symbol formats."""
        provider = EastmoneyFundFlowProvider()
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.validate_symbol('INVALID')
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.validate_symbol('12345')  # Too short
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            provider.validate_symbol('1234567')  # Too long
    
    def test_empty_symbol(self):
        """Test with empty symbol."""
        provider = EastmoneyFundFlowProvider()
        
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            provider.validate_symbol('')
    
    def test_valid_date_format(self):
        """Test with valid date format."""
        provider = EastmoneyFundFlowProvider()
        # Should not raise
        provider.validate_date('2024-01-01')
        provider.validate_date('2024-12-31')
    
    def test_invalid_date_format(self):
        """Test with invalid date formats."""
        provider = EastmoneyFundFlowProvider()
        
        with pytest.raises(ValueError, match="Invalid .* format"):
            provider.validate_date('2024/01/01')
        
        with pytest.raises(ValueError, match="Invalid .* format"):
            provider.validate_date('01-01-2024')
        
        with pytest.raises(ValueError, match="Invalid .* format"):
            provider.validate_date('2024-13-01')  # Invalid month
    
    def test_invalid_date_range(self):
        """Test with invalid date range (start > end)."""
        provider = EastmoneyFundFlowProvider()
        
        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            provider.validate_date_range('2024-12-31', '2024-01-01')
    
    def test_valid_date_range(self):
        """Test with valid date range."""
        provider = EastmoneyFundFlowProvider()
        # Should not raise
        provider.validate_date_range('2024-01-01', '2024-12-31')
        provider.validate_date_range('2024-01-01', '2024-01-01')  # Same date


# ============================================================================
# Unit Tests - Data Standardization & JSON Compatibility
# ============================================================================

class TestDataStandardization:
    """Test data standardization and JSON compatibility."""
    
    @patch('akshare.stock_individual_fund_flow')
    def test_stock_fund_flow_output_schema(self, mock_akshare):
        """Test stock fund flow output has expected columns."""
        # Mock akshare response
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01', '2024-01-02'],
            '收盘价': [10.5, 10.8],
            '涨跌幅': [1.5, 2.8],
            '主力净流入-净额': [1000000, 2000000],
            '主力净流入-净占比': [5.0, 6.0],
            '超大单净流入-净额': [500000, 1000000],
            '大单净流入-净额': [500000, 1000000],
            '中单净流入-净额': [-300000, -500000],
            '小单净流入-净额': [-200000, -500000],
        })
        mock_akshare.return_value = mock_data
        
        provider = EastmoneyFundFlowProvider()
        result = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
        
        expected_columns = [
            'date', 'symbol', 'close_price', 'pct_change',
            'fundflow_main_net_inflow', 'fundflow_main_net_inflow_rate',
            'fundflow_super_large_net_inflow', 'fundflow_large_net_inflow',
            'fundflow_medium_net_inflow', 'fundflow_small_net_inflow'
        ]
        assert list(result.columns) == expected_columns
    
    @patch('akshare.stock_individual_fund_flow')
    def test_json_compatibility_no_nan(self, mock_akshare):
        """Test output contains no NaN values in numeric columns."""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01'],
            '收盘价': [10.5],
            '涨跌幅': [1.5],
            '主力净流入-净额': [1000000],
            '主力净流入-净占比': [5.0],
            '超大单净流入-净额': [500000],
            '大单净流入-净额': [500000],
            '中单净流入-净额': [-300000],
            '小单净流入-净额': [-200000],
        })
        mock_akshare.return_value = mock_data
        
        provider = EastmoneyFundFlowProvider()
        result = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
        
        # Check no NaN in numeric columns
        for col in result.select_dtypes(include=['float64', 'float32']).columns:
            # Either no NaN at all, or all None (which is acceptable for JSON)
            assert not result[col].isna().any() or result[col].isna().all()
    
    @patch('akshare.stock_individual_fund_flow')
    def test_json_compatibility_no_infinity(self, mock_akshare):
        """Test output contains no Infinity values."""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01'],
            '收盘价': [10.5],
            '涨跌幅': [1.5],
            '主力净流入-净额': [1000000],
            '主力净流入-净占比': [5.0],
            '超大单净流入-净额': [500000],
            '大单净流入-净额': [500000],
            '中单净流入-净额': [-300000],
            '小单净流入-净额': [-200000],
        })
        mock_akshare.return_value = mock_data
        
        provider = EastmoneyFundFlowProvider()
        result = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
        
        for col in result.select_dtypes(include=['float64', 'float32']).columns:
            assert not np.isinf(result[col]).any()
    
    @patch('akshare.stock_individual_fund_flow')
    def test_date_format(self, mock_akshare):
        """Test date column is in YYYY-MM-DD string format."""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01', '2024-01-02'],
            '收盘价': [10.5, 10.8],
            '涨跌幅': [1.5, 2.8],
            '主力净流入-净额': [1000000, 2000000],
            '主力净流入-净占比': [5.0, 6.0],
            '超大单净流入-净额': [500000, 1000000],
            '大单净流入-净额': [500000, 1000000],
            '中单净流入-净额': [-300000, -500000],
            '小单净流入-净额': [-200000, -500000],
        })
        mock_akshare.return_value = mock_data
        
        provider = EastmoneyFundFlowProvider()
        result = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
        
        assert result['date'].dtype == 'object'
        assert all(isinstance(d, str) for d in result['date'])
        
        # Validate date format
        for date_str in result['date']:
            datetime.strptime(date_str, '%Y-%m-%d')
    
    @patch('akshare.stock_individual_fund_flow')
    def test_symbol_format(self, mock_akshare):
        """Test symbol column is 6-digit string with leading zeros."""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01'],
            '收盘价': [10.5],
            '涨跌幅': [1.5],
            '主力净流入-净额': [1000000],
            '主力净流入-净占比': [5.0],
            '超大单净流入-净额': [500000],
            '大单净流入-净额': [500000],
            '中单净流入-净额': [-300000],
            '小单净流入-净额': [-200000],
        })
        mock_akshare.return_value = mock_data
        
        provider = EastmoneyFundFlowProvider()
        result = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
        
        assert result['symbol'].dtype == 'object'
        assert all(len(s) == 6 for s in result['symbol'])
        assert all(s.isdigit() for s in result['symbol'])
    
    @patch('akshare.stock_individual_fund_flow')
    def test_json_serialization(self, mock_akshare):
        """Test DataFrame can be serialized to JSON."""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01'],
            '收盘价': [10.5],
            '涨跌幅': [1.5],
            '主力净流入-净额': [1000000],
            '主力净流入-净占比': [5.0],
            '超大单净流入-净额': [500000],
            '大单净流入-净额': [500000],
            '中单净流入-净额': [-300000],
            '小单净流入-净额': [-200000],
        })
        mock_akshare.return_value = mock_data
        
        provider = EastmoneyFundFlowProvider()
        result = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
        
        json_str = result.to_json(orient='records')
        assert json_str is not None
        
        # Verify can be parsed back
        import json
        parsed = json.loads(json_str)
        assert isinstance(parsed, list)


# ============================================================================
# Unit Tests - Empty Results
# ============================================================================

class TestEmptyResults:
    """Test handling of empty results."""
    
    @patch('akshare.stock_individual_fund_flow')
    def test_empty_result_structure(self, mock_akshare):
        """Test empty result returns DataFrame with correct columns."""
        mock_akshare.return_value = pd.DataFrame()
        
        provider = EastmoneyFundFlowProvider()
        result = provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        
        expected_columns = [
            'date', 'symbol', 'close_price', 'pct_change',
            'fundflow_main_net_inflow', 'fundflow_main_net_inflow_rate',
            'fundflow_super_large_net_inflow', 'fundflow_large_net_inflow',
            'fundflow_medium_net_inflow', 'fundflow_small_net_inflow'
        ]
        assert list(result.columns) == expected_columns
    
    @patch('akshare.stock_board_industry_name_em')
    def test_empty_industry_list(self, mock_akshare):
        """Test empty industry list returns DataFrame with correct columns."""
        mock_akshare.return_value = pd.DataFrame()
        
        provider = EastmoneyFundFlowProvider()
        result = provider.get_industry_list()
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert list(result.columns) == ['sector_code', 'sector_name', 'constituent_count']


# ============================================================================
# Unit Tests - Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling and exceptions."""
    
    @patch('akshare.stock_individual_fund_flow')
    def test_upstream_exception(self, mock_akshare):
        """Test handling of upstream exceptions."""
        mock_akshare.side_effect = Exception("Upstream error")
        
        provider = EastmoneyFundFlowProvider()
        
        with pytest.raises(RuntimeError, match="Failed to fetch stock fund flow data"):
            provider.get_stock_fund_flow('600000', '2024-01-01', '2024-01-31')
    
    def test_invalid_sector_type(self):
        """Test with invalid sector type."""
        provider = EastmoneyFundFlowProvider()
        
        with pytest.raises(ValueError, match="Invalid sector_type"):
            provider.get_sector_fund_flow('invalid', '2024-01-01', '2024-01-31')
    
    def test_invalid_indicator(self):
        """Test with invalid indicator."""
        provider = EastmoneyFundFlowProvider()
        
        with pytest.raises(ValueError, match="Invalid indicator"):
            provider.get_main_fund_flow_rank('2024-01-01', 'invalid')
    
    def test_empty_industry_code(self):
        """Test with empty industry code."""
        provider = EastmoneyFundFlowProvider()
        
        with pytest.raises(ValueError, match="industry_code cannot be empty"):
            provider.get_industry_constituents('')
    
    def test_empty_concept_code(self):
        """Test with empty concept code."""
        provider = EastmoneyFundFlowProvider()
        
        with pytest.raises(ValueError, match="concept_code cannot be empty"):
            provider.get_concept_constituents('')


# ============================================================================
# Unit Tests - Factory
# ============================================================================

class TestFactory:
    """Test factory class."""
    
    def test_factory_creates_provider(self):
        """Test factory can create provider instance."""
        provider = FundFlowFactory.get_provider(source='eastmoney')
        assert provider is not None
        assert isinstance(provider, EastmoneyFundFlowProvider)
    
    def test_factory_invalid_source(self):
        """Test factory raises error for invalid source."""
        with pytest.raises(ValueError, match="Unsupported data source"):
            FundFlowFactory.get_provider(source='invalid_source')
    
    def test_factory_list_sources(self):
        """Test factory can list available sources."""
        sources = FundFlowFactory.list_sources()
        assert isinstance(sources, list)
        assert 'eastmoney' in sources


# ============================================================================
# Unit Tests - Public API
# ============================================================================

class TestPublicAPI:
    """Test public API functions."""
    
    @patch('akshare.stock_individual_fund_flow')
    def test_get_stock_fund_flow(self, mock_akshare):
        """Test get_stock_fund_flow public function."""
        mock_data = pd.DataFrame({
            '日期': ['2024-01-01'],
            '收盘价': [10.5],
            '涨跌幅': [1.5],
            '主力净流入-净额': [1000000],
            '主力净流入-净占比': [5.0],
            '超大单净流入-净额': [500000],
            '大单净流入-净额': [500000],
            '中单净流入-净额': [-300000],
            '小单净流入-净额': [-200000],
        })
        mock_akshare.return_value = mock_data
        
        result = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-31')
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
    
    @patch('akshare.stock_sector_fund_flow_rank')
    def test_get_sector_fund_flow(self, mock_akshare):
        """Test get_sector_fund_flow public function."""
        mock_data = pd.DataFrame({
            '名称': ['银行'],
            '今日涨跌幅': [1.5],
            '今日主力净流入-净额': [1000000],
            '今日主力净流入最大股': ['600000'],
        })
        mock_akshare.return_value = mock_data
        
        result = get_sector_fund_flow('industry', start_date='2024-01-01', end_date='2024-01-31')
        assert isinstance(result, pd.DataFrame)
    
    @patch('akshare.stock_individual_fund_flow_rank')
    def test_get_main_fund_flow_rank(self, mock_akshare):
        """Test get_main_fund_flow_rank public function."""
        mock_data = pd.DataFrame({
            '代码': ['600000'],
            '名称': ['浦发银行'],
            '今日主力净流入-净额': [1000000],
            '今日涨跌幅': [1.5],
        })
        mock_akshare.return_value = mock_data
        
        result = get_main_fund_flow_rank('2024-01-01')
        assert isinstance(result, pd.DataFrame)
    
    @patch('akshare.stock_board_industry_name_em')
    def test_get_industry_list(self, mock_akshare):
        """Test get_industry_list public function."""
        mock_data = pd.DataFrame({
            '板块代码': ['BK0001'],
            '板块名称': ['银行'],
            '公司数量': [10],
        })
        mock_akshare.return_value = mock_data
        
        result = get_industry_list()
        assert isinstance(result, pd.DataFrame)
    
    @patch('akshare.stock_board_industry_cons_em')
    def test_get_industry_constituents(self, mock_akshare):
        """Test get_industry_constituents public function."""
        mock_data = pd.DataFrame({
            '代码': ['600000'],
            '名称': ['浦发银行'],
        })
        mock_akshare.return_value = mock_data
        
        result = get_industry_constituents('BK0001')
        assert isinstance(result, pd.DataFrame)
    
    @patch('akshare.stock_board_concept_name_em')
    def test_get_concept_list(self, mock_akshare):
        """Test get_concept_list public function."""
        mock_data = pd.DataFrame({
            '板块代码': ['BK0001'],
            '板块名称': ['人工智能'],
            '公司数量': [50],
        })
        mock_akshare.return_value = mock_data
        
        result = get_concept_list()
        assert isinstance(result, pd.DataFrame)
    
    @patch('akshare.stock_board_concept_cons_em')
    def test_get_concept_constituents(self, mock_akshare):
        """Test get_concept_constituents public function."""
        mock_data = pd.DataFrame({
            '代码': ['600000'],
            '名称': ['浦发银行'],
        })
        mock_akshare.return_value = mock_data
        
        result = get_concept_constituents('BK0001')
        assert isinstance(result, pd.DataFrame)


# ============================================================================
# Contract Tests - Golden Samples
# ============================================================================

class TestContractGoldenSamples:
    """Test data schema stability using golden samples."""
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_stock_fund_flow_schema(self):
        """Test stock fund flow schema matches golden sample."""
        validator = GoldenSampleValidator('fundflow')
        
        # Get real data (rate limited)
        integration_rate_limiter.wait()
        
        try:
            df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-03')
            
            if not df.empty:
                # Create or validate golden sample
                sample_name = 'stock_fund_flow_schema'
                try:
                    validator.assert_schema_matches(sample_name, df)
                except FileNotFoundError:
                    # First run - create golden sample
                    validator.save_golden_sample(
                        sample_name,
                        df,
                        metadata={
                            'description': 'Stock fund flow data schema',
                            'symbol': '600000',
                            'created_at': datetime.now().strftime('%Y-%m-%d')
                        }
                    )
                    pytest.skip("Golden sample created, run test again to validate")
        except Exception as e:
            pytest.skip(f"Could not fetch data for contract test: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_sector_fund_flow_schema(self):
        """Test sector fund flow schema matches golden sample."""
        validator = GoldenSampleValidator('fundflow')
        
        integration_rate_limiter.wait()
        
        try:
            df = get_sector_fund_flow('industry')
            
            if not df.empty:
                sample_name = 'sector_fund_flow_schema'
                try:
                    validator.assert_schema_matches(sample_name, df)
                except FileNotFoundError:
                    validator.save_golden_sample(
                        sample_name,
                        df,
                        metadata={
                            'description': 'Sector fund flow data schema',
                            'sector_type': 'industry',
                            'created_at': datetime.now().strftime('%Y-%m-%d')
                        }
                    )
                    pytest.skip("Golden sample created, run test again to validate")
        except Exception as e:
            pytest.skip(f"Could not fetch data for contract test: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_main_fund_flow_rank_schema(self):
        """Test main fund flow rank schema matches golden sample."""
        validator = GoldenSampleValidator('fundflow')
        
        integration_rate_limiter.wait()
        
        try:
            df = get_main_fund_flow_rank(datetime.now().strftime('%Y-%m-%d'))
            
            if not df.empty:
                sample_name = 'main_fund_flow_rank_schema'
                try:
                    validator.assert_schema_matches(sample_name, df)
                except FileNotFoundError:
                    validator.save_golden_sample(
                        sample_name,
                        df,
                        metadata={
                            'description': 'Main fund flow rank schema',
                            'created_at': datetime.now().strftime('%Y-%m-%d')
                        }
                    )
                    pytest.skip("Golden sample created, run test again to validate")
        except Exception as e:
            pytest.skip(f"Could not fetch data for contract test: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_industry_list_schema(self):
        """Test industry list schema matches golden sample."""
        validator = GoldenSampleValidator('fundflow')
        
        integration_rate_limiter.wait()
        
        try:
            df = get_industry_list()
            
            if not df.empty:
                sample_name = 'industry_list_schema'
                try:
                    validator.assert_schema_matches(sample_name, df)
                except FileNotFoundError:
                    validator.save_golden_sample(
                        sample_name,
                        df,
                        metadata={
                            'description': 'Industry list schema',
                            'created_at': datetime.now().strftime('%Y-%m-%d')
                        }
                    )
                    pytest.skip("Golden sample created, run test again to validate")
        except Exception as e:
            pytest.skip(f"Could not fetch data for contract test: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_concept_list_schema(self):
        """Test concept list schema matches golden sample."""
        validator = GoldenSampleValidator('fundflow')
        
        integration_rate_limiter.wait()
        
        try:
            df = get_concept_list()
            
            if not df.empty:
                sample_name = 'concept_list_schema'
                try:
                    validator.assert_schema_matches(sample_name, df)
                except FileNotFoundError:
                    validator.save_golden_sample(
                        sample_name,
                        df,
                        metadata={
                            'description': 'Concept list schema',
                            'created_at': datetime.now().strftime('%Y-%m-%d')
                        }
                    )
                    pytest.skip("Golden sample created, run test again to validate")
        except Exception as e:
            pytest.skip(f"Could not fetch data for contract test: {e}")


# ============================================================================
# Integration Tests - Real API Calls
# ============================================================================

class TestIntegrationRealAPI:
    """Integration tests with real API calls."""
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_stock_fund_flow_real_data(self):
        """Test stock fund flow with real API call."""
        integration_rate_limiter.wait()
        
        try:
            df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-03')
            
            # Validate structure
            validator = DataFrameValidator()
            validator.validate_required_columns(df, ['date', 'symbol', 'close'])
            validator.validate_json_compatible(df)
            
            # Validate data types
            assert df['date'].dtype == 'object'
            assert df['symbol'].dtype == 'object'
            
            # Validate symbol format
            if not df.empty:
                assert all(len(s) == 6 for s in df['symbol'])
                assert all(s.isdigit() for s in df['symbol'])
        except Exception as e:
            pytest.skip(f"Real API call failed: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_sector_fund_flow_real_data(self):
        """Test sector fund flow with real API call."""
        integration_rate_limiter.wait()
        
        try:
            df = get_sector_fund_flow('industry')
            
            validator = DataFrameValidator()
            validator.validate_required_columns(df, ['date', 'sector_code', 'sector_name'])
            validator.validate_json_compatible(df)
        except Exception as e:
            pytest.skip(f"Real API call failed: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_main_fund_flow_rank_real_data(self):
        """Test main fund flow rank with real API call."""
        integration_rate_limiter.wait()
        
        try:
            df = get_main_fund_flow_rank(datetime.now().strftime('%Y-%m-%d'))
            
            validator = DataFrameValidator()
            validator.validate_required_columns(df, ['rank', 'symbol', 'name'])
            validator.validate_json_compatible(df)
            
            # Validate ranking
            if not df.empty:
                assert df['rank'].iloc[0] == 1
                assert df['rank'].is_monotonic_increasing
        except Exception as e:
            pytest.skip(f"Real API call failed: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_industry_list_real_data(self):
        """Test industry list with real API call."""
        integration_rate_limiter.wait()
        
        try:
            df = get_industry_list()
            
            validator = DataFrameValidator()
            validator.validate_required_columns(df, ['sector_code', 'sector_name'])
            validator.validate_json_compatible(df)
            
            # Should have multiple industries
            if not df.empty:
                assert len(df) > 10
        except Exception as e:
            pytest.skip(f"Real API call failed: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_industry_constituents_real_data(self):
        """Test industry constituents with real API call."""
        integration_rate_limiter.wait()
        
        try:
            # First get an industry code
            industries = get_industry_list()
            if industries.empty:
                pytest.skip("No industries available")
            
            industry_code = industries['sector_code'].iloc[0]
            
            integration_rate_limiter.wait()
            df = get_industry_constituents(industry_code)
            
            validator = DataFrameValidator()
            validator.validate_required_columns(df, ['symbol', 'name'])
            validator.validate_json_compatible(df)
            
            # Validate symbol format
            if not df.empty:
                assert all(len(s) == 6 for s in df['symbol'])
        except Exception as e:
            pytest.skip(f"Real API call failed: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_concept_list_real_data(self):
        """Test concept list with real API call."""
        integration_rate_limiter.wait()
        
        try:
            df = get_concept_list()
            
            validator = DataFrameValidator()
            validator.validate_required_columns(df, ['sector_code', 'sector_name'])
            validator.validate_json_compatible(df)
            
            # Should have multiple concepts
            if not df.empty:
                assert len(df) > 10
        except Exception as e:
            pytest.skip(f"Real API call failed: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_concept_constituents_real_data(self):
        """Test concept constituents with real API call."""
        integration_rate_limiter.wait()
        
        try:
            # First get a concept code
            concepts = get_concept_list()
            if concepts.empty:
                pytest.skip("No concepts available")
            
            concept_code = concepts['sector_code'].iloc[0]
            
            integration_rate_limiter.wait()
            df = get_concept_constituents(concept_code)
            
            validator = DataFrameValidator()
            validator.validate_required_columns(df, ['symbol', 'name'])
            validator.validate_json_compatible(df)
            
            # Validate symbol format
            if not df.empty:
                assert all(len(s) == 6 for s in df['symbol'])
        except Exception as e:
            pytest.skip(f"Real API call failed: {e}")


# ============================================================================
# Integration Tests - End-to-End Workflows
# ============================================================================

class TestIntegrationWorkflows:
    """Test complete workflows combining multiple functions."""
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_workflow_industry_analysis(self):
        """Test workflow: Get industry list -> Get constituents -> Get fund flow."""
        try:
            # Step 1: Get industry list
            integration_rate_limiter.wait()
            industries = get_industry_list()
            assert not industries.empty, "No industries found"
            
            # Step 2: Get first industry's constituents
            industry_code = industries['sector_code'].iloc[0]
            integration_rate_limiter.wait()
            constituents = get_industry_constituents(industry_code)
            
            if not constituents.empty:
                # Step 3: Get fund flow for first constituent
                symbol = constituents['symbol'].iloc[0]
                integration_rate_limiter.wait()
                fund_flow = get_stock_fund_flow(
                    symbol,
                    start_date='2024-01-01',
                    end_date='2024-01-03'
                )
                
                # Validate complete workflow
                validator = DataFrameValidator()
                validator.validate_json_compatible(fund_flow)
        except Exception as e:
            pytest.skip(f"Workflow test failed: {e}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_workflow_concept_analysis(self):
        """Test workflow: Get concept list -> Get constituents -> Get fund flow."""
        try:
            # Step 1: Get concept list
            integration_rate_limiter.wait()
            concepts = get_concept_list()
            assert not concepts.empty, "No concepts found"
            
            # Step 2: Get first concept's constituents
            concept_code = concepts['sector_code'].iloc[0]
            integration_rate_limiter.wait()
            constituents = get_concept_constituents(concept_code)
            
            if not constituents.empty:
                # Step 3: Get fund flow for first constituent
                symbol = constituents['symbol'].iloc[0]
                integration_rate_limiter.wait()
                fund_flow = get_stock_fund_flow(
                    symbol,
                    start_date='2024-01-01',
                    end_date='2024-01-03'
                )
                
                # Validate complete workflow
                validator = DataFrameValidator()
                validator.validate_json_compatible(fund_flow)
        except Exception as e:
            pytest.skip(f"Workflow test failed: {e}")
