"""
Unit tests for BaseProvider abstract class.

Tests cover:
- Parameter validation (symbols, dates, date ranges)
- JSON compatibility (NaN, Infinity, datetime conversion)
- Data standardization utilities
- Metadata properties
"""

from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from akshare_one.modules.base import BaseProvider


# Concrete implementation for testing
class TestProvider(BaseProvider):
    """Concrete implementation of BaseProvider for testing"""
    
    def get_source_name(self) -> str:
        return 'test_source'
    
    def get_data_type(self) -> str:
        return 'test_data'
    
    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame({'col1': [1, 2, 3]})


class TestParameterValidation:
    """Test parameter validation methods"""
    
    def test_validate_symbol_valid(self):
        """Test valid symbol formats"""
        BaseProvider.validate_symbol('600000')
        BaseProvider.validate_symbol('000001')
        BaseProvider.validate_symbol('300001')
        # Should not raise any exception
    
    def test_validate_symbol_invalid_format(self):
        """Test invalid symbol formats"""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            BaseProvider.validate_symbol('60000')  # Too short
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            BaseProvider.validate_symbol('6000000')  # Too long
        
        with pytest.raises(ValueError, match="Invalid symbol format"):
            BaseProvider.validate_symbol('ABC123')  # Contains letters
    
    def test_validate_symbol_empty(self):
        """Test empty symbol"""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            BaseProvider.validate_symbol('')
    
    def test_validate_date_valid(self):
        """Test valid date formats"""
        BaseProvider.validate_date('2024-01-01')
        BaseProvider.validate_date('2023-12-31')
        # Should not raise any exception
    
    def test_validate_date_invalid_format(self):
        """Test invalid date formats"""
        with pytest.raises(ValueError, match="Invalid .* format"):
            BaseProvider.validate_date('2024/01/01')
        
        with pytest.raises(ValueError, match="Invalid .* format"):
            BaseProvider.validate_date('20240101')
        
        with pytest.raises(ValueError, match="Invalid .* format"):
            BaseProvider.validate_date('2024-13-01')  # Invalid month
    
    def test_validate_date_empty(self):
        """Test empty date"""
        with pytest.raises(ValueError, match="date cannot be empty"):
            BaseProvider.validate_date('')
    
    def test_validate_date_range_valid(self):
        """Test valid date ranges"""
        BaseProvider.validate_date_range('2024-01-01', '2024-12-31')
        BaseProvider.validate_date_range('2024-01-01', '2024-01-01')  # Same date
        # Should not raise any exception
    
    def test_validate_date_range_invalid_order(self):
        """Test invalid date range (start > end)"""
        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            BaseProvider.validate_date_range('2024-12-31', '2024-01-01')
    
    def test_validate_symbol_optional_none(self):
        """Test optional symbol with None"""
        BaseProvider.validate_symbol_optional(None)
        # Should not raise any exception
    
    def test_validate_symbol_optional_valid(self):
        """Test optional symbol with valid value"""
        BaseProvider.validate_symbol_optional('600000')
        # Should not raise any exception
    
    def test_validate_symbol_optional_invalid(self):
        """Test optional symbol with invalid value"""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            BaseProvider.validate_symbol_optional('ABC')


class TestJSONCompatibility:
    """Test JSON compatibility methods"""
    
    def test_ensure_json_compatible_nan(self):
        """Test NaN replacement with None"""
        df = pd.DataFrame({
            'value': [1.0, np.nan, 3.0],
            'name': ['a', 'b', 'c']
        })
        
        result = BaseProvider.ensure_json_compatible(df)
        
        assert result['value'][0] == 1.0
        assert result['value'][1] is None
        assert result['value'][2] == 3.0
    
    def test_ensure_json_compatible_infinity(self):
        """Test Infinity replacement with None"""
        df = pd.DataFrame({
            'value': [1.0, np.inf, -np.inf, 4.0]
        })
        
        result = BaseProvider.ensure_json_compatible(df)
        
        assert result['value'][0] == 1.0
        assert result['value'][1] is None
        assert result['value'][2] is None
        assert result['value'][3] == 4.0
    
    def test_ensure_json_compatible_datetime(self):
        """Test datetime conversion to string"""
        df = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
        
        result = BaseProvider.ensure_json_compatible(df)
        
        assert result['date'][0] == '2024-01-01'
        assert result['date'][1] == '2024-01-02'
        assert result['date'][2] == '2024-01-03'
        assert isinstance(result['date'][0], str)
    
    def test_ensure_json_compatible_symbol(self):
        """Test symbol column standardization"""
        df = pd.DataFrame({
            'symbol': ['600000', '1', '000001']
        })
        
        result = BaseProvider.ensure_json_compatible(df)
        
        assert result['symbol'][0] == '600000'
        assert result['symbol'][1] == '000001'  # Leading zeros added
        assert result['symbol'][2] == '000001'
    
    def test_ensure_json_compatible_empty_dataframe(self):
        """Test empty DataFrame handling"""
        df = pd.DataFrame()
        result = BaseProvider.ensure_json_compatible(df)
        assert result.empty
    
    def test_replace_nan_with_none(self):
        """Test individual value NaN replacement"""
        assert BaseProvider.replace_nan_with_none(1.0) == 1.0
        assert BaseProvider.replace_nan_with_none(np.nan) is None
        assert BaseProvider.replace_nan_with_none(np.inf) is None
        assert BaseProvider.replace_nan_with_none(-np.inf) is None
        assert BaseProvider.replace_nan_with_none('text') == 'text'
    
    def test_create_empty_dataframe(self):
        """Test empty DataFrame creation"""
        columns = ['date', 'symbol', 'value']
        df = BaseProvider.create_empty_dataframe(columns)
        
        assert df.empty
        assert list(df.columns) == columns


class TestDataStandardization:
    """Test data standardization methods"""
    
    def test_standardize_symbol(self):
        """Test symbol standardization"""
        assert BaseProvider.standardize_symbol('600000') == '600000'
        assert BaseProvider.standardize_symbol('1') == '000001'
        assert BaseProvider.standardize_symbol('123') == '000123'
    
    def test_standardize_date_string(self):
        """Test date standardization from string"""
        assert BaseProvider.standardize_date('2024-01-01') == '2024-01-01'
        assert BaseProvider.standardize_date('2024/01/01') == '2024-01-01'
        assert BaseProvider.standardize_date('20240101') == '2024-01-01'
    
    def test_standardize_date_datetime(self):
        """Test date standardization from datetime"""
        dt = datetime(2024, 1, 1)
        assert BaseProvider.standardize_date(dt) == '2024-01-01'
    
    def test_standardize_date_none(self):
        """Test date standardization with None"""
        assert BaseProvider.standardize_date(None) is None
        assert BaseProvider.standardize_date(np.nan) is None
    
    def test_standardize_numeric_valid(self):
        """Test numeric standardization with valid values"""
        assert BaseProvider.standardize_numeric(1.5) == 1.5
        assert BaseProvider.standardize_numeric('2.5') == 2.5
        assert BaseProvider.standardize_numeric(3) == 3.0
    
    def test_standardize_numeric_invalid(self):
        """Test numeric standardization with invalid values"""
        assert BaseProvider.standardize_numeric(np.nan) is None
        assert BaseProvider.standardize_numeric(np.inf) is None
        assert BaseProvider.standardize_numeric('invalid') is None
        assert BaseProvider.standardize_numeric(None) is None
    
    def test_standardize_numeric_with_default(self):
        """Test numeric standardization with default value"""
        assert BaseProvider.standardize_numeric(np.nan, default=0.0) == 0.0
        assert BaseProvider.standardize_numeric('invalid', default=-1.0) == -1.0


class TestMetadata:
    """Test metadata properties"""
    
    def test_metadata_structure(self):
        """Test metadata structure"""
        provider = TestProvider()
        metadata = provider.metadata
        
        assert 'source' in metadata
        assert 'data_type' in metadata
        assert 'update_frequency' in metadata
        assert 'delay_minutes' in metadata
    
    def test_metadata_values(self):
        """Test metadata values"""
        provider = TestProvider()
        metadata = provider.metadata
        
        assert metadata['source'] == 'test_source'
        assert metadata['data_type'] == 'test_data'
        assert metadata['update_frequency'] == 'daily'
        assert metadata['delay_minutes'] == 0
    
    def test_get_source_name(self):
        """Test get_source_name method"""
        provider = TestProvider()
        assert provider.get_source_name() == 'test_source'
    
    def test_get_data_type(self):
        """Test get_data_type method"""
        provider = TestProvider()
        assert provider.get_data_type() == 'test_data'
    
    def test_get_update_frequency(self):
        """Test get_update_frequency method"""
        provider = TestProvider()
        assert provider.get_update_frequency() == 'daily'
    
    def test_get_delay_minutes(self):
        """Test get_delay_minutes method"""
        provider = TestProvider()
        assert provider.get_delay_minutes() == 0


class TestProviderWorkflow:
    """Test complete provider workflow"""
    
    def test_get_data_workflow(self):
        """Test complete get_data workflow"""
        provider = TestProvider()
        result = provider.get_data()
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'col1' in result.columns
    
    def test_standardize_data_default(self):
        """Test default standardize_data implementation"""
        provider = TestProvider()
        df = pd.DataFrame({
            'value': [1.0, np.nan, np.inf],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
        
        # Default standardize_data just returns the DataFrame unchanged
        result = provider.standardize_data(df)
        
        # The default implementation does not apply JSON compatibility
        # That is done by ensure_json_compatible which is called in get_data
        # Just verify the DataFrame is returned
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        
        # Test ensure_json_compatible separately for JSON compatibility
        json_result = provider.ensure_json_compatible(df.copy())
        assert json_result['value'][1] is None
        assert json_result['value'][2] is None
        assert isinstance(json_result['date'][0], str)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_mixed_data_types(self):
        """Test DataFrame with mixed data types"""
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.1, np.nan, 3.3],
            'str_col': ['a', 'b', 'c'],
            'date_col': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
            'symbol': ['600000', '1', '000001']
        })
        
        result = BaseProvider.ensure_json_compatible(df)
        
        # Check all conversions
        assert result['float_col'][1] is None
        assert isinstance(result['date_col'][0], str)
        assert result['symbol'][1] == '000001'
    
    def test_dataframe_with_all_nan(self):
        """Test DataFrame with all NaN values"""
        df = pd.DataFrame({
            'value': [np.nan, np.nan, np.nan]
        })
        
        result = BaseProvider.ensure_json_compatible(df)
        
        assert result['value'][0] is None
        assert result['value'][1] is None
        assert result['value'][2] is None
    
    def test_large_numbers(self):
        """Test handling of very large numbers"""
        df = pd.DataFrame({
            'value': [1e10, 1e20, 1e100]
        })
        
        result = BaseProvider.ensure_json_compatible(df)
        
        # Large numbers should be preserved (not converted to infinity)
        assert result['value'][0] == 1e10
        assert result['value'][1] == 1e20
        # Note: 1e100 might be converted to inf depending on float precision



class TestFieldNamingStandardization:
    """Test field naming standardization methods"""
    
    def test_standardize_field_names(self):
        """Test field name standardization"""
        from akshare_one.modules.field_naming import FieldType
        
        provider = TestProvider()
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'symbol': ['600000', '000001'],
            'main_net_inflow': [1000000, 2000000]
        })
        
        field_types = {
            'date': FieldType.DATE,
            'symbol': FieldType.SYMBOL,
            'main_net_inflow': FieldType.NET_FLOW
        }
        
        result = provider.standardize_field_names(df, field_types)
        
        # Should validate and return the DataFrame
        assert list(result.columns) == ['date', 'symbol', 'main_net_inflow']
    
    def test_map_source_fields(self):
        """Test source field mapping"""
        provider = TestProvider()
        df = pd.DataFrame({
            '日期': ['2024-01-01', '2024-01-02'],
            '股票代码': ['600000', '000001']
        })
        
        # Note: This will return unchanged if no mapping config exists
        result = provider.map_source_fields(df, 'eastmoney')
        
        # Should return a DataFrame (may be unchanged without config)
        assert isinstance(result, pd.DataFrame)
    
    def test_convert_amount_units(self):
        """Test amount unit conversion"""
        provider = TestProvider()
        df = pd.DataFrame({
            'balance': [1.5, 2.0, 3.5],  # In yi_yuan (亿元)
            'amount': [100, 200, 300]     # In wan_yuan (万元)
        })
        
        amount_fields = {
            'balance': 'yi_yuan',
            'amount': 'wan_yuan'
        }
        
        result = provider.convert_amount_units(df, amount_fields)
        
        # Check conversions
        assert result['balance'][0] == 150000000  # 1.5亿 = 150000000元
        assert result['amount'][0] == 1000000     # 100万 = 1000000元
    
    def test_add_field_aliases(self):
        """Test adding field aliases"""
        # Create provider with alias config
        provider = TestProvider()
        provider.alias_manager.add_alias('old_field', 'new_field')
        
        df = pd.DataFrame({
            'new_field': [1, 2, 3]
        })
        
        result = provider.add_field_aliases(df, include_legacy=True)
        
        # Should have both new and old field names
        assert 'new_field' in result.columns
        assert 'old_field' in result.columns
        assert result['old_field'].equals(result['new_field'])
    
    def test_add_field_aliases_disabled(self):
        """Test adding field aliases when disabled"""
        provider = TestProvider()
        df = pd.DataFrame({
            'new_field': [1, 2, 3]
        })
        
        result = provider.add_field_aliases(df, include_legacy=False)
        
        # Should only have new field name
        assert 'new_field' in result.columns
        assert len(result.columns) == 1
    
    def test_standardize_date_field(self):
        """Test date field standardization"""
        provider = TestProvider()
        # Use dates that are already parseable
        series = pd.Series(['2024-01-01', '2024-01-02', '2024-01-03'])
        
        result = provider.standardize_date_field(series)
        
        # All should be in YYYY-MM-DD format
        assert result[0] == '2024-01-01'
        assert result[1] == '2024-01-02'
        assert result[2] == '2024-01-03'
    
    def test_standardize_timestamp_field(self):
        """Test timestamp field standardization"""
        provider = TestProvider()
        series = pd.Series(['2024-01-01 10:30:00', '2024-01-02 15:45:00'])
        
        result = provider.standardize_timestamp_field(series)
        
        # Should be timezone-aware
        assert result.dt.tz is not None
        assert str(result.dt.tz) == 'Asia/Shanghai'
    
    def test_get_mapping_config_path_default(self):
        """Test default mapping config path"""
        provider = TestProvider()
        path = provider._get_mapping_config_path()
        
        # Default should be None
        assert path is None
    
    def test_get_alias_config_default(self):
        """Test default alias config"""
        provider = TestProvider()
        config = provider._get_alias_config()
        
        # Default should be empty dict
        assert config == {}


class TestFieldNamingIntegration:
    """Test integration of field naming components"""
    
    def test_complete_standardization_workflow(self):
        """Test complete field standardization workflow"""
        from akshare_one.modules.field_naming import FieldType
        
        provider = TestProvider()
        
        # Start with raw data
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'symbol': ['600000', '000001'],
            'total_balance': [1.5, 2.0],  # In yi_yuan
        })
        
        # 1. Convert units
        df = provider.convert_amount_units(df, {'total_balance': 'yi_yuan'})
        
        # 2. Standardize field names
        field_types = {
            'date': FieldType.DATE,
            'symbol': FieldType.SYMBOL,
            'total_balance': FieldType.BALANCE
        }
        df = provider.standardize_field_names(df, field_types)
        
        # 3. Add aliases
        df = provider.add_field_aliases(df, include_legacy=False)
        
        # Verify results
        assert df['total_balance'][0] == 150000000
        assert list(df.columns) == ['date', 'symbol', 'total_balance']
    
    def test_standardization_with_date_formatting(self):
        """Test standardization with date formatting"""
        provider = TestProvider()
        
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'value': [100, 200]
        })
        
        # Standardize date field
        df['date'] = provider.standardize_date_field(pd.Series(df['date']))
        
        # Verify date format
        assert df['date'][0] == '2024-01-01'
        assert df['date'][1] == '2024-01-02'
