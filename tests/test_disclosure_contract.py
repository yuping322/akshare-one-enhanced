"""
Contract tests for disclosure module.

These tests validate that the data structure returned by disclosure interfaces
matches the expected schema (golden samples). This helps detect upstream API changes.
"""

import pytest
import pandas as pd
from unittest.mock import patch

from tests.utils.contract_test import GoldenSampleValidator, create_golden_sample_if_missing
from src.akshare_one.modules.disclosure import (
    get_dividend_data,
    get_repurchase_data,
    get_st_delist_data,
)


@pytest.fixture
def disclosure_validator():
    """Create a golden sample validator for disclosure module."""
    return GoldenSampleValidator('disclosure')


@pytest.fixture
def update_mode(request):
    """Check if we're in update mode."""
    return request.config.getoption("--update-golden-samples", default=False)


class TestDisclosureContractDividend:
    """Contract tests for dividend data."""
    
    @patch('akshare.stock_dividend_cninfo')
    def test_dividend_data_schema(self, mock_ak, disclosure_validator, update_mode):
        """Test dividend data schema matches golden sample."""
        # Mock akshare response with realistic data
        mock_df = pd.DataFrame({
            '报告时间': ['2023年报', '2022年报', '2021年报'],
            '派息比例': [1.5, 1.0, 0.8],
            '股权登记日': ['2024-06-20', '2023-06-15', '2022-06-10'],
            '除权日': ['2024-06-21', '2023-06-16', '2022-06-11'],
            '派息日': ['2024-06-22', '2023-06-17', '2022-06-12'],
        })
        mock_ak.return_value = mock_df
        
        # Get data
        df = get_dividend_data('600000', start_date='2020-01-01', end_date='2024-12-31')
        
        # Validate or create golden sample
        if update_mode:
            disclosure_validator.save_golden_sample(
                'dividend_data',
                df,
                metadata={
                    'description': 'Dividend data schema',
                    'source': 'eastmoney',
                    'interface': 'get_dividend_data'
                }
            )
        else:
            disclosure_validator.assert_schema_matches('dividend_data', df)
    
    @patch('akshare.stock_dividend_cninfo')
    def test_dividend_data_empty_schema(self, mock_ak, disclosure_validator, update_mode):
        """Test dividend data schema with empty result."""
        mock_ak.return_value = pd.DataFrame()
        
        # Get data
        df = get_dividend_data('600000', start_date='2020-01-01', end_date='2024-12-31')
        
        # Should still have correct columns even when empty
        expected_columns = [
            'symbol', 'fiscal_year', 'dividend_per_share',
            'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio'
        ]
        assert list(df.columns) == expected_columns
        assert len(df) == 0
    
    @patch('akshare.stock_dividend_cninfo')
    def test_dividend_data_types(self, mock_ak):
        """Test dividend data has correct data types."""
        mock_df = pd.DataFrame({
            '报告时间': ['2023年报'],
            '派息比例': [1.5],
            '股权登记日': ['2024-06-20'],
            '除权日': ['2024-06-21'],
            '派息日': ['2024-06-22'],
        })
        mock_ak.return_value = mock_df
        
        df = get_dividend_data('600000', start_date='2020-01-01', end_date='2024-12-31')
        
        # Check data types are string-like
        assert pd.api.types.is_string_dtype(df['symbol'])
        assert pd.api.types.is_string_dtype(df['fiscal_year'])
        assert pd.api.types.is_string_dtype(df['record_date'])
        assert pd.api.types.is_string_dtype(df['ex_dividend_date'])
        assert pd.api.types.is_string_dtype(df['payment_date'])


class TestDisclosureContractRepurchase:
    """Contract tests for repurchase data."""
    
    @patch('akshare.stock_repurchase_em')
    def test_repurchase_data_schema(self, mock_ak, disclosure_validator, update_mode):
        """Test repurchase data schema matches golden sample."""
        # Mock akshare response
        mock_df = pd.DataFrame({
            '股票代码': ['600000', '000001', '600036'],
            '最新公告日期': ['2024-01-15', '2024-01-10', '2024-01-05'],
            '实施进度': ['进行中', '已完成', '董事会预案'],
            '已回购金额': [50000000.0, 100000000.0, None],
            '已回购股份数量': [1000000.0, 2000000.0, None],
            '计划回购价格区间': ['10-15元', '20-25元', '30-35元'],
            '计划回购金额区间-下限': [40000000.0, 80000000.0, 60000000.0],
        })
        mock_ak.return_value = mock_df
        
        # Get data
        df = get_repurchase_data(None, start_date='2024-01-01', end_date='2024-12-31')
        
        # Validate or create golden sample
        if update_mode:
            disclosure_validator.save_golden_sample(
                'repurchase_data',
                df,
                metadata={
                    'description': 'Repurchase data schema',
                    'source': 'eastmoney',
                    'interface': 'get_repurchase_data'
                }
            )
        else:
            disclosure_validator.assert_schema_matches('repurchase_data', df)
    
    @patch('akshare.stock_repurchase_em')
    def test_repurchase_data_empty_schema(self, mock_ak):
        """Test repurchase data schema with empty result."""
        mock_ak.return_value = pd.DataFrame()
        
        # Get data
        df = get_repurchase_data('600000', start_date='2024-01-01', end_date='2024-12-31')
        
        # Should still have correct columns even when empty
        expected_columns = [
            'symbol', 'announcement_date', 'progress',
            'amount', 'quantity', 'price_range'
        ]
        assert list(df.columns) == expected_columns
        assert len(df) == 0
    
    @patch('akshare.stock_repurchase_em')
    def test_repurchase_data_types(self, mock_ak):
        """Test repurchase data has correct data types."""
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
        
        df = get_repurchase_data('600000', start_date='2024-01-01', end_date='2024-12-31')
        
        # Check data types are string-like
        assert pd.api.types.is_string_dtype(df['symbol'])
        assert pd.api.types.is_string_dtype(df['announcement_date'])
        assert pd.api.types.is_string_dtype(df['progress'])
        assert pd.api.types.is_string_dtype(df['price_range'])


class TestDisclosureContractSTDelist:
    """Contract tests for ST/delist data."""
    
    @patch('akshare.stock_info_sh_delist')
    @patch('akshare.stock_info_sz_delist')
    def test_st_delist_data_schema(self, mock_sz, mock_sh, disclosure_validator, update_mode):
        """Test ST/delist data schema matches golden sample."""
        # Mock SH data
        mock_sh_df = pd.DataFrame({
            '公司代码': ['600001', '600002', '600003'],
            '公司简称': ['*ST华谊', 'ST海润', '退市大控'],
            '暂停上市日期': ['2024-01-15', '2024-02-20', '2024-03-10'],
        })
        mock_sh.return_value = mock_sh_df
        
        # Mock SZ data
        mock_sz_df = pd.DataFrame({
            '证券代码': ['000001', '000002'],
            '证券简称': ['S*ST昌鱼', 'SST前锋'],
            '终止上市日期': ['2024-03-10', '2024-04-15'],
        })
        mock_sz.return_value = mock_sz_df
        
        # Get data
        df = get_st_delist_data(None)
        
        # Validate or create golden sample
        if update_mode:
            disclosure_validator.save_golden_sample(
                'st_delist_data',
                df,
                metadata={
                    'description': 'ST/delist risk data schema',
                    'source': 'eastmoney',
                    'interface': 'get_st_delist_data'
                }
            )
        else:
            disclosure_validator.assert_schema_matches('st_delist_data', df)
    
    @patch('akshare.stock_info_sh_delist')
    @patch('akshare.stock_info_sz_delist')
    def test_st_delist_data_empty_schema(self, mock_sz, mock_sh):
        """Test ST/delist data schema with empty result."""
        mock_sh.return_value = pd.DataFrame()
        mock_sz.return_value = pd.DataFrame()
        
        # Get data
        df = get_st_delist_data('600000')
        
        # Should still have correct columns even when empty
        expected_columns = [
            'symbol', 'name', 'st_type', 'risk_level', 'announcement_date'
        ]
        assert list(df.columns) == expected_columns
        assert len(df) == 0
    
    @patch('akshare.stock_info_sh_delist')
    @patch('akshare.stock_info_sz_delist')
    def test_st_delist_data_types(self, mock_sz, mock_sh):
        """Test ST/delist data has correct data types."""
        mock_sh_df = pd.DataFrame({
            '公司代码': ['600001'],
            '公司简称': ['*ST华谊'],
            '暂停上市日期': ['2024-01-15'],
        })
        mock_sh.return_value = mock_sh_df
        mock_sz.return_value = pd.DataFrame()
        
        df = get_st_delist_data(None)
        
        # Check data types are string-like
        assert pd.api.types.is_string_dtype(df['symbol'])
        assert pd.api.types.is_string_dtype(df['name'])
        assert pd.api.types.is_string_dtype(df['st_type'])
        assert pd.api.types.is_string_dtype(df['risk_level'])
        assert pd.api.types.is_string_dtype(df['announcement_date'])
    
    @patch('akshare.stock_info_sh_delist')
    @patch('akshare.stock_info_sz_delist')
    def test_st_delist_risk_level_values(self, mock_sz, mock_sh):
        """Test ST/delist data has valid risk level values."""
        mock_sh_df = pd.DataFrame({
            '公司代码': ['600001', '600002', '600003'],
            '公司简称': ['*ST华谊', 'ST海润', '退市大控'],
            '暂停上市日期': ['2024-01-15', '2024-02-20', '2024-03-10'],
        })
        mock_sh.return_value = mock_sh_df
        mock_sz.return_value = pd.DataFrame()
        
        df = get_st_delist_data(None)
        
        # Check risk levels are valid
        valid_risk_levels = {'low', 'medium', 'high', 'critical'}
        assert set(df['risk_level'].unique()).issubset(valid_risk_levels)
        
        # Check specific risk levels
        assert df[df['symbol'] == '600001']['risk_level'].iloc[0] == 'high'  # *ST
        assert df[df['symbol'] == '600002']['risk_level'].iloc[0] == 'medium'  # ST
        assert df[df['symbol'] == '600003']['risk_level'].iloc[0] == 'critical'  # 退市


class TestDisclosureContractStability:
    """Test data structure stability across different scenarios."""
    
    @patch('akshare.stock_dividend_cninfo')
    def test_dividend_column_order_stability(self, mock_ak):
        """Test dividend data column order is stable."""
        mock_df = pd.DataFrame({
            '报告时间': ['2023年报'],
            '派息比例': [1.5],
            '股权登记日': ['2024-06-20'],
            '除权日': ['2024-06-21'],
            '派息日': ['2024-06-22'],
        })
        mock_ak.return_value = mock_df
        
        # Get data multiple times
        df1 = get_dividend_data('600000', start_date='2020-01-01', end_date='2024-12-31')
        df2 = get_dividend_data('600000', start_date='2020-01-01', end_date='2024-12-31')
        
        # Column order should be identical
        assert list(df1.columns) == list(df2.columns)
    
    @patch('akshare.stock_repurchase_em')
    def test_repurchase_column_order_stability(self, mock_ak):
        """Test repurchase data column order is stable."""
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
        
        # Get data multiple times
        df1 = get_repurchase_data('600000', start_date='2024-01-01', end_date='2024-12-31')
        df2 = get_repurchase_data('600000', start_date='2024-01-01', end_date='2024-12-31')
        
        # Column order should be identical
        assert list(df1.columns) == list(df2.columns)
    
    @patch('akshare.stock_info_sh_delist')
    @patch('akshare.stock_info_sz_delist')
    def test_st_delist_column_order_stability(self, mock_sz, mock_sh):
        """Test ST/delist data column order is stable."""
        mock_sh_df = pd.DataFrame({
            '公司代码': ['600001'],
            '公司简称': ['*ST华谊'],
            '暂停上市日期': ['2024-01-15'],
        })
        mock_sh.return_value = mock_sh_df
        mock_sz.return_value = pd.DataFrame()
        
        # Get data multiple times
        df1 = get_st_delist_data('600001')
        df2 = get_st_delist_data('600001')
        
        # Column order should be identical
        assert list(df1.columns) == list(df2.columns)
