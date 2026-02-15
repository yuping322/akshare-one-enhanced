"""
Unit tests for FieldStandardizer methods.

Tests the standardize_field_name, standardize_dataframe, and validate_field_name methods.
"""

import pytest
import pandas as pd
from akshare_one.modules.field_naming import (
    FieldStandardizer,
    NamingRules,
    FieldType,
)


class TestValidateFieldName:
    """Test the validate_field_name method."""
    
    def test_validate_valid_date_field(self):
        """Test validation of valid date field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name('date', FieldType.DATE)
        
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_invalid_date_field(self):
        """Test validation of invalid date field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name('trading_date', FieldType.DATE)
        
        assert is_valid is False
        assert error_msg is not None
        assert 'date' in error_msg.lower()
    
    def test_validate_valid_event_date_field(self):
        """Test validation of valid event date fields."""
        standardizer = FieldStandardizer(NamingRules())
        
        for field_name in ['report_date', 'announcement_date', 'pledge_date']:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.EVENT_DATE)
            assert is_valid is True
            assert error_msg is None
    
    def test_validate_invalid_event_date_field(self):
        """Test validation of invalid event date field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name('date', FieldType.EVENT_DATE)
        
        assert is_valid is False
        assert error_msg is not None
    
    def test_validate_valid_amount_field(self):
        """Test validation of valid amount fields."""
        standardizer = FieldStandardizer(NamingRules())
        
        for field_name in ['buy_amount', 'sell_amount', 'total_amount']:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.AMOUNT)
            assert is_valid is True
            assert error_msg is None
    
    def test_validate_invalid_amount_field(self):
        """Test validation of invalid amount field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name('amount', FieldType.AMOUNT)
        
        assert is_valid is False
        assert 'pattern' in error_msg.lower()
    
    def test_validate_valid_net_flow_field(self):
        """Test validation of valid net flow fields."""
        standardizer = FieldStandardizer(NamingRules())
        
        for field_name in ['main_net_inflow', 'super_large_net_outflow', 'northbound_net_buy']:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.NET_FLOW)
            assert is_valid is True
            assert error_msg is None
    
    def test_validate_invalid_net_flow_field(self):
        """Test validation of invalid net flow field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name('net_inflow', FieldType.NET_FLOW)
        
        assert is_valid is False
        assert error_msg is not None
    
    def test_validate_valid_rate_field(self):
        """Test validation of valid rate fields."""
        standardizer = FieldStandardizer(NamingRules())
        
        for field_name in ['growth_rate', 'turnover_rate', 'pct_change']:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.RATE)
            assert is_valid is True
            assert error_msg is None
    
    def test_validate_valid_ratio_field(self):
        """Test validation of valid ratio fields."""
        standardizer = FieldStandardizer(NamingRules())
        
        for field_name in ['holdings_ratio', 'pledge_ratio']:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.RATIO)
            assert is_valid is True
            assert error_msg is None
    
    def test_validate_valid_symbol_field(self):
        """Test validation of valid symbol field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name('symbol', FieldType.SYMBOL)
        
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_invalid_symbol_field(self):
        """Test validation of invalid symbol field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name('stock_symbol', FieldType.SYMBOL)
        
        assert is_valid is False
        assert 'symbol' in error_msg.lower()
    
    def test_validate_valid_boolean_field(self):
        """Test validation of valid boolean fields."""
        standardizer = FieldStandardizer(NamingRules())
        
        for field_name in ['is_st', 'has_dividend', 'is_suspended']:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.BOOLEAN)
            assert is_valid is True
            assert error_msg is None
    
    def test_validate_invalid_boolean_field(self):
        """Test validation of invalid boolean field."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name('suspended', FieldType.BOOLEAN)
        
        assert is_valid is False
        assert error_msg is not None
    
    def test_validate_other_field_type(self):
        """Test validation of OTHER field type (accepts any pattern)."""
        standardizer = FieldStandardizer(NamingRules())
        
        # OTHER type should accept any field name
        for field_name in ['any_field', 'AnyField', '123']:
            is_valid, error_msg = standardizer.validate_field_name(field_name, FieldType.OTHER)
            assert is_valid is True
            assert error_msg is None
    
    def test_error_message_contains_suggestion(self):
        """Test that error messages contain helpful suggestions."""
        standardizer = FieldStandardizer(NamingRules())
        is_valid, error_msg = standardizer.validate_field_name('trading_date', FieldType.DATE)
        
        assert is_valid is False
        assert 'Expected pattern' in error_msg
        assert 'Suggestion' in error_msg


class TestStandardizeFieldName:
    """Test the standardize_field_name method."""
    
    def test_standardize_valid_field_name(self):
        """Test standardizing a valid field name."""
        standardizer = FieldStandardizer(NamingRules())
        result = standardizer.standardize_field_name('date', FieldType.DATE)
        
        assert result == 'date'
    
    def test_standardize_valid_event_date_field(self):
        """Test standardizing valid event date fields."""
        standardizer = FieldStandardizer(NamingRules())
        
        for field_name in ['report_date', 'announcement_date', 'pledge_date']:
            result = standardizer.standardize_field_name(field_name, FieldType.EVENT_DATE)
            assert result == field_name
    
    def test_standardize_valid_amount_field(self):
        """Test standardizing valid amount fields."""
        standardizer = FieldStandardizer(NamingRules())
        
        for field_name in ['buy_amount', 'sell_amount', 'total_amount']:
            result = standardizer.standardize_field_name(field_name, FieldType.AMOUNT)
            assert result == field_name
    
    def test_standardize_invalid_field_name_raises_error(self):
        """Test that standardizing an invalid field name raises ValueError."""
        standardizer = FieldStandardizer(NamingRules())
        
        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_field_name('trading_date', FieldType.DATE)
        
        assert 'does not conform to naming rules' in str(exc_info.value)
        assert 'trading_date' in str(exc_info.value)
    
    def test_standardize_invalid_amount_field_raises_error(self):
        """Test that standardizing an invalid amount field raises ValueError."""
        standardizer = FieldStandardizer(NamingRules())
        
        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_field_name('amount', FieldType.AMOUNT)
        
        assert 'does not conform to naming rules' in str(exc_info.value)
    
    def test_standardize_invalid_symbol_field_raises_error(self):
        """Test that standardizing an invalid symbol field raises ValueError."""
        standardizer = FieldStandardizer(NamingRules())
        
        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_field_name('stock_symbol', FieldType.SYMBOL)
        
        assert 'does not conform to naming rules' in str(exc_info.value)
        assert 'symbol' in str(exc_info.value).lower()
    
    def test_error_message_includes_field_type(self):
        """Test that error message includes the field type."""
        standardizer = FieldStandardizer(NamingRules())
        
        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_field_name('invalid_date', FieldType.DATE)
        
        assert 'date' in str(exc_info.value).lower()


class TestStandardizeDataFrame:
    """Test the standardize_dataframe method."""
    
    def test_standardize_dataframe_with_valid_fields(self):
        """Test standardizing a DataFrame with all valid field names."""
        standardizer = FieldStandardizer(NamingRules())
        
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'symbol': ['000001', '000002'],
            'buy_amount': [1000000, 2000000],
            'sell_amount': [800000, 1500000]
        })
        
        field_mapping = {
            'date': FieldType.DATE,
            'symbol': FieldType.SYMBOL,
            'buy_amount': FieldType.AMOUNT,
            'sell_amount': FieldType.AMOUNT
        }
        
        result = standardizer.standardize_dataframe(df, field_mapping)
        
        # Should return a DataFrame with the same columns
        assert list(result.columns) == list(df.columns)
        # Should not modify the original DataFrame
        assert result is not df
        # Data should be preserved
        pd.testing.assert_frame_equal(result, df)
    
    def test_standardize_dataframe_with_invalid_field_raises_error(self):
        """Test that standardizing a DataFrame with invalid field name raises ValueError."""
        standardizer = FieldStandardizer(NamingRules())
        
        df = pd.DataFrame({
            'trading_date': ['2024-01-01', '2024-01-02'],
            'symbol': ['000001', '000002']
        })
        
        field_mapping = {
            'trading_date': FieldType.DATE,
            'symbol': FieldType.SYMBOL
        }
        
        with pytest.raises(ValueError) as exc_info:
            standardizer.standardize_dataframe(df, field_mapping)
        
        assert 'trading_date' in str(exc_info.value)
        assert 'does not conform to naming rules' in str(exc_info.value)
    
    def test_standardize_dataframe_with_partial_mapping(self):
        """Test standardizing a DataFrame where only some fields are in the mapping."""
        standardizer = FieldStandardizer(NamingRules())
        
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'symbol': ['000001', '000002'],
            'unmapped_field': [100, 200]
        })
        
        # Only map some fields
        field_mapping = {
            'date': FieldType.DATE,
            'symbol': FieldType.SYMBOL
        }
        
        result = standardizer.standardize_dataframe(df, field_mapping)
        
        # Should succeed and return DataFrame with all columns
        assert list(result.columns) == list(df.columns)
        pd.testing.assert_frame_equal(result, df)
    
    def test_standardize_empty_dataframe(self):
        """Test standardizing an empty DataFrame."""
        standardizer = FieldStandardizer(NamingRules())
        
        df = pd.DataFrame()
        field_mapping = {}
        
        result = standardizer.standardize_dataframe(df, field_mapping)
        
        assert result.empty
        assert result is not df
    
    def test_standardize_dataframe_with_complex_field_types(self):
        """Test standardizing a DataFrame with various field types."""
        standardizer = FieldStandardizer(NamingRules())
        
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'report_date': ['2024-01-15'],
            'symbol': ['000001'],
            'name': ['Test Stock'],
            'buy_amount': [1000000],
            'main_net_inflow': [500000],
            'turnover_rate': [0.05],
            'holdings_ratio': [0.15],
            'is_st': [False],
            'volume': [10000000]
        })
        
        field_mapping = {
            'date': FieldType.DATE,
            'report_date': FieldType.EVENT_DATE,
            'symbol': FieldType.SYMBOL,
            'name': FieldType.NAME,
            'buy_amount': FieldType.AMOUNT,
            'main_net_inflow': FieldType.NET_FLOW,
            'turnover_rate': FieldType.RATE,
            'holdings_ratio': FieldType.RATIO,
            'is_st': FieldType.BOOLEAN,
            'volume': FieldType.VOLUME
        }
        
        result = standardizer.standardize_dataframe(df, field_mapping)
        
        # All fields should be valid
        assert list(result.columns) == list(df.columns)
        pd.testing.assert_frame_equal(result, df)
    
    def test_standardize_dataframe_does_not_modify_original(self):
        """Test that standardize_dataframe does not modify the original DataFrame."""
        standardizer = FieldStandardizer(NamingRules())
        
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'symbol': ['000001', '000002']
        })
        
        original_df = df.copy()
        
        field_mapping = {
            'date': FieldType.DATE,
            'symbol': FieldType.SYMBOL
        }
        
        result = standardizer.standardize_dataframe(df, field_mapping)
        
        # Original DataFrame should be unchanged
        pd.testing.assert_frame_equal(df, original_df)
        # Result should be a different object
        assert result is not df
    
    def test_standardize_dataframe_with_multiple_invalid_fields(self):
        """Test that the first invalid field causes an error."""
        standardizer = FieldStandardizer(NamingRules())
        
        df = pd.DataFrame({
            'trading_date': ['2024-01-01'],
            'stock_symbol': ['000001'],
            'amount': [1000000]
        })
        
        field_mapping = {
            'trading_date': FieldType.DATE,
            'stock_symbol': FieldType.SYMBOL,
            'amount': FieldType.AMOUNT
        }
        
        # Should raise error for one of the invalid fields
        with pytest.raises(ValueError):
            standardizer.standardize_dataframe(df, field_mapping)


class TestGenerateErrorMessage:
    """Test the _generate_error_message helper method."""
    
    def test_error_message_for_date_field(self):
        """Test error message generation for date field."""
        standardizer = FieldStandardizer(NamingRules())
        pattern = r'^date$'
        error_msg = standardizer._generate_error_message('trading_date', FieldType.DATE, pattern)
        
        assert 'Expected pattern' in error_msg
        assert 'Suggestion' in error_msg
        assert 'date' in error_msg.lower()
    
    def test_error_message_for_amount_field(self):
        """Test error message generation for amount field."""
        standardizer = FieldStandardizer(NamingRules())
        pattern = r'^[a-z_]+_amount$'
        error_msg = standardizer._generate_error_message('amount', FieldType.AMOUNT, pattern)
        
        assert 'Expected pattern' in error_msg
        assert 'Suggestion' in error_msg
        assert 'buy_amount' in error_msg or 'sell_amount' in error_msg
    
    def test_error_message_for_symbol_field(self):
        """Test error message generation for symbol field."""
        standardizer = FieldStandardizer(NamingRules())
        pattern = '^symbol$'
        error_msg = standardizer._generate_error_message('stock_symbol', FieldType.SYMBOL, pattern)
        
        assert 'Expected pattern' in error_msg
        assert 'Suggestion' in error_msg
        assert 'symbol' in error_msg.lower()
    
    def test_error_message_for_boolean_field(self):
        """Test error message generation for boolean field."""
        standardizer = FieldStandardizer(NamingRules())
        pattern = r'^(is|has)_[a-z_]+$'
        error_msg = standardizer._generate_error_message('suspended', FieldType.BOOLEAN, pattern)
        
        assert 'Expected pattern' in error_msg
        assert 'Suggestion' in error_msg
        assert 'is_' in error_msg or 'has_' in error_msg
