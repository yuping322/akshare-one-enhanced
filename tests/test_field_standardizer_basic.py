"""
Basic unit tests for FieldStandardizer class structure.

Tests the initialization and basic structure of the FieldStandardizer class.
"""

import pytest
from akshare_one.modules.field_naming import (
    FieldStandardizer,
    NamingRules,
    FieldType,
)


class TestFieldStandardizerBasicStructure:
    """Test the basic structure of FieldStandardizer class."""
    
    def test_field_standardizer_initialization(self):
        """Test that FieldStandardizer can be initialized with NamingRules."""
        rules = NamingRules()
        standardizer = FieldStandardizer(rules)
        
        assert standardizer.naming_rules is rules
        assert hasattr(standardizer, '_field_type_patterns')
    
    def test_field_type_patterns_mapping_created(self):
        """Test that field type to pattern mapping is created during initialization."""
        rules = NamingRules()
        standardizer = FieldStandardizer(rules)
        
        # Should have mappings for all field types
        assert len(standardizer._field_type_patterns) == len(FieldType)
        
        # Verify some key mappings exist
        assert FieldType.DATE in standardizer._field_type_patterns
        assert FieldType.AMOUNT in standardizer._field_type_patterns
        assert FieldType.RATE in standardizer._field_type_patterns
        assert FieldType.SYMBOL in standardizer._field_type_patterns
    
    def test_field_type_patterns_match_naming_rules(self):
        """Test that field type patterns match the naming rules."""
        rules = NamingRules()
        standardizer = FieldStandardizer(rules)
        
        # Verify patterns match the rules
        assert standardizer._field_type_patterns[FieldType.DATE] == rules.date_field_pattern
        assert standardizer._field_type_patterns[FieldType.AMOUNT] == rules.amount_field_pattern
        assert standardizer._field_type_patterns[FieldType.RATE] == rules.rate_field_pattern
        assert standardizer._field_type_patterns[FieldType.RATIO] == rules.ratio_field_pattern
    
    def test_field_standardizer_with_custom_naming_rules(self):
        """Test FieldStandardizer with custom NamingRules."""
        custom_rules = NamingRules(
            date_field_pattern=r'^custom_date$',
            symbol_field_name='custom_symbol'
        )
        standardizer = FieldStandardizer(custom_rules)
        
        assert standardizer.naming_rules.date_field_pattern == r'^custom_date$'
        assert standardizer.naming_rules.symbol_field_name == 'custom_symbol'
        assert standardizer._field_type_patterns[FieldType.DATE] == r'^custom_date$'
        assert standardizer._field_type_patterns[FieldType.SYMBOL] == '^custom_symbol$'
    
    def test_standardize_field_name_method_exists(self):
        """Test that standardize_field_name method exists."""
        rules = NamingRules()
        standardizer = FieldStandardizer(rules)
        
        assert hasattr(standardizer, 'standardize_field_name')
        assert callable(standardizer.standardize_field_name)
    
    def test_standardize_dataframe_method_exists(self):
        """Test that standardize_dataframe method exists."""
        rules = NamingRules()
        standardizer = FieldStandardizer(rules)
        
        assert hasattr(standardizer, 'standardize_dataframe')
        assert callable(standardizer.standardize_dataframe)
    
    def test_validate_field_name_method_exists(self):
        """Test that validate_field_name method exists."""
        rules = NamingRules()
        standardizer = FieldStandardizer(rules)
        
        assert hasattr(standardizer, 'validate_field_name')
        assert callable(standardizer.validate_field_name)
