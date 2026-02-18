"""
Property-based tests for UnitConverter.

Tests the amount field unit conversion properties using Hypothesis for property-based testing.

Feature: field-naming-standardization
Task: 3.2 为 UnitConverter 编写属性测试
"""

import numpy as np
import pandas as pd
import pytest

try:
    from hypothesis import assume, given, settings
    from hypothesis import strategies as st
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    pytest.skip("Hypothesis not installed", allow_module_level=True)

from akshare_one.modules.field_naming.unit_converter import UnitConverter

# ============================================================================
# Test Data Generators (Hypothesis Strategies)
# ============================================================================

@st.composite
def valid_amount_values(draw):
    """Generate valid amount values (non-negative floats)."""
    # Use reasonable range for financial amounts
    # Avoid extremely small values that might cause underflow
    return draw(st.floats(
        min_value=1e-10,  # Avoid values smaller than 1e-10 to prevent underflow
        max_value=1e12,  # 1 trillion yuan
        allow_nan=False,
        allow_infinity=False
    ))


@st.composite
def valid_units(draw):
    """Generate valid unit names."""
    return draw(st.sampled_from(['yuan', 'wan_yuan', 'yi_yuan']))


@st.composite
def amount_dataframes(draw):
    """Generate DataFrames with amount fields in various units."""
    num_rows = draw(st.integers(min_value=1, max_value=10))
    num_fields = draw(st.integers(min_value=1, max_value=5))
    
    data = {}
    field_units = {}
    
    for i in range(num_fields):
        field_name = f'amount_{i}'
        unit = draw(valid_units())
        
        # Generate amount values
        values = [draw(valid_amount_values()) for _ in range(num_rows)]
        
        data[field_name] = values
        field_units[field_name] = unit
    
    return pd.DataFrame(data), field_units


# ============================================================================
# Property 5: 金额字段单位统一性
# **Validates: Requirements 2.1, 2.6**
# ============================================================================

class TestProperty5AmountFieldUnitUniformity:
    """
    Property 5: 金额字段单位统一性
    
    对于任何金额字段，经过标准化处理后，其存储单位应统一为元（元），
    无论源数据使用何种单位
    
    **Validates: Requirements 2.1, 2.6**
    """
    
    @given(
        amount=valid_amount_values(),
        from_unit=valid_units()
    )
    @settings(max_examples=100)
    def test_any_unit_converts_to_yuan(self, amount, from_unit):
        """
        Property: Any amount in any supported unit should convert to yuan.
        """
        converter = UnitConverter()
        
        # Convert to yuan
        result = converter.convert_amount(amount, from_unit, 'yuan')
        
        # Result should be a valid number
        assert isinstance(result, (int, float))
        assert not np.isnan(result)
        assert not np.isinf(result)
        
        # Result should be non-negative
        assert result >= 0
    
    @given(
        amount=valid_amount_values(),
        from_unit=valid_units()
    )
    @settings(max_examples=100)
    def test_conversion_to_yuan_is_deterministic(self, amount, from_unit):
        """
        Property: Converting the same amount from the same unit to yuan 
        should always produce the same result.
        """
        converter = UnitConverter()
        
        # Convert twice
        result1 = converter.convert_amount(amount, from_unit, 'yuan')
        result2 = converter.convert_amount(amount, from_unit, 'yuan')
        
        # Results should be identical
        assert result1 == result2
    
    @given(
        amount=valid_amount_values(),
        from_unit=valid_units()
    )
    @settings(max_examples=100)
    def test_conversion_roundtrip_preserves_value(self, amount, from_unit):
        """
        Property: Converting to yuan and back to the original unit 
        should preserve the original value (within floating point precision).
        """
        converter = UnitConverter()
        
        # Convert to yuan
        yuan_amount = converter.convert_amount(amount, from_unit, 'yuan')
        
        # Convert back to original unit
        back_amount = converter.convert_amount(yuan_amount, 'yuan', from_unit)
        
        # Should be equal within floating point precision
        # Use relative tolerance for large numbers
        if amount == 0:
            assert abs(back_amount - amount) < 1e-9
        else:
            relative_error = abs(back_amount - amount) / amount
            assert relative_error < 1e-9, f"Roundtrip conversion failed: {amount} -> {yuan_amount} -> {back_amount}"
    
    @given(df_and_units=amount_dataframes())
    @settings(max_examples=50)
    def test_dataframe_conversion_unifies_all_fields_to_yuan(self, df_and_units):
        """
        Property: Converting a DataFrame with amount fields in various units 
        should result in all fields being in yuan.
        """
        df, field_units = df_and_units
        converter = UnitConverter()
        
        # Convert all fields to yuan
        result_df = converter.convert_dataframe_amounts(df, field_units)
        
        # Result should have same shape
        assert result_df.shape == df.shape
        
        # All columns should be preserved
        assert list(result_df.columns) == list(df.columns)
        
        # All values should be converted (verify by checking they're different if unit != yuan)
        for field_name, unit in field_units.items():
            if unit != 'yuan':
                # Values should be different after conversion
                multiplier = UnitConverter.UNIT_MULTIPLIERS[unit]
                expected = df[field_name] * multiplier
                pd.testing.assert_series_equal(
                    result_df[field_name], 
                    expected,
                    check_names=False
                )
    
    def test_yuan_to_yuan_is_identity(self):
        """
        Property: Converting from yuan to yuan should be an identity operation.
        """
        converter = UnitConverter()
        
        test_values = [0, 1, 100, 1000, 1e6, 1e9]
        
        for value in test_values:
            result = converter.convert_amount(value, 'yuan', 'yuan')
            assert result == value
    
    @given(amount=valid_amount_values())
    @settings(max_examples=50)
    def test_wan_yuan_to_yuan_multiplies_by_10000(self, amount):
        """
        Property: Converting from wan_yuan to yuan should multiply by 10,000.
        """
        converter = UnitConverter()
        
        result = converter.convert_amount(amount, 'wan_yuan', 'yuan')
        expected = amount * 10000
        
        # Check within floating point precision
        if expected == 0:
            assert abs(result - expected) < 1e-9
        else:
            relative_error = abs(result - expected) / expected
            assert relative_error < 1e-9
    
    @given(amount=valid_amount_values())
    @settings(max_examples=50)
    def test_yi_yuan_to_yuan_multiplies_by_100000000(self, amount):
        """
        Property: Converting from yi_yuan to yuan should multiply by 100,000,000.
        """
        converter = UnitConverter()
        
        result = converter.convert_amount(amount, 'yi_yuan', 'yuan')
        expected = amount * 100000000
        
        # Check within floating point precision
        if expected == 0:
            assert abs(result - expected) < 1e-9
        else:
            relative_error = abs(result - expected) / expected
            assert relative_error < 1e-9


# ============================================================================
# Property 10: 金额存储与展示分离
# **Validates: Requirements 2.1, 2.6, 2.7**
# ============================================================================

class TestProperty10AmountStorageAndDisplaySeparation:
    """
    Property 10: 金额存储与展示分离
    
    对于任何金额字段，存储层的值应始终使用元（元）作为单位，
    展示层可以转换为其他单位（如亿元），但转换不应影响存储值
    
    **Validates: Requirements 2.1, 2.6, 2.7**
    """
    
    @given(
        amount_in_yuan=valid_amount_values(),
        display_unit=valid_units()
    )
    @settings(max_examples=100)
    def test_display_conversion_does_not_affect_storage(self, amount_in_yuan, display_unit):
        """
        Property: Converting stored yuan values to display units should not 
        affect the original stored value.
        """
        converter = UnitConverter()
        
        # Store in yuan (this is our storage value)
        stored_value = amount_in_yuan
        
        # Convert to display unit
        display_value = converter.convert_amount(stored_value, 'yuan', display_unit)
        
        # Convert back to yuan (simulating reading from storage)
        retrieved_value = converter.convert_amount(display_value, display_unit, 'yuan')
        
        # Retrieved value should match stored value
        if stored_value == 0:
            assert abs(retrieved_value - stored_value) < 1e-9
        else:
            relative_error = abs(retrieved_value - stored_value) / stored_value
            assert relative_error < 1e-9
    
    @given(df_and_units=amount_dataframes())
    @settings(max_examples=50)
    def test_dataframe_storage_always_in_yuan(self, df_and_units):
        """
        Property: After standardization, DataFrame storage should always be in yuan,
        regardless of source units.
        """
        df, field_units = df_and_units
        converter = UnitConverter()
        
        # Standardize to yuan (storage layer)
        stored_df = converter.convert_dataframe_amounts(df, field_units)
        
        # Verify all values are in yuan by converting to display units and back
        for field_name, _source_unit in field_units.items():
            # Get the stored values (in yuan)
            stored_values = stored_df[field_name]
            
            # Convert to any display unit (e.g., yi_yuan)
            display_values = stored_values.apply(
                lambda x: converter.convert_amount(x, 'yuan', 'yi_yuan') if pd.notna(x) else x
            )
            
            # Convert back to yuan
            retrieved_values = display_values.apply(
                lambda x: converter.convert_amount(x, 'yi_yuan', 'yuan') if pd.notna(x) else x
            )
            
            # Retrieved values should match stored values
            pd.testing.assert_series_equal(
                stored_values,
                retrieved_values,
                check_names=False,
                rtol=1e-9
            )
    
    @given(
        amount=valid_amount_values(),
        intermediate_unit=valid_units()
    )
    @settings(max_examples=100)
    def test_multiple_display_conversions_preserve_storage(self, amount, intermediate_unit):
        """
        Property: Multiple conversions for display purposes should not 
        accumulate errors that affect storage value.
        """
        converter = UnitConverter()
        
        # Store in yuan
        stored_value = amount
        
        # Convert to intermediate display unit
        display1 = converter.convert_amount(stored_value, 'yuan', intermediate_unit)
        
        # Convert to another display unit (wan_yuan)
        display2 = converter.convert_amount(display1, intermediate_unit, 'wan_yuan')
        
        # Convert back to yuan (storage)
        retrieved_value = converter.convert_amount(display2, 'wan_yuan', 'yuan')
        
        # Retrieved value should match stored value
        if stored_value == 0:
            assert abs(retrieved_value - stored_value) < 1e-9
        else:
            relative_error = abs(retrieved_value - stored_value) / stored_value
            assert relative_error < 1e-9
    
    def test_storage_in_yuan_allows_any_display_unit(self):
        """
        Property: Storing in yuan should allow conversion to any display unit 
        without loss of precision.
        """
        converter = UnitConverter()
        
        # Test with various stored values
        test_values = [100, 10000, 100000000, 1.5e9]
        
        for stored_value in test_values:
            # Try converting to each display unit and back
            for display_unit in ['yuan', 'wan_yuan', 'yi_yuan']:
                display_value = converter.convert_amount(stored_value, 'yuan', display_unit)
                retrieved_value = converter.convert_amount(display_value, display_unit, 'yuan')
                
                # Should preserve value
                relative_error = abs(retrieved_value - stored_value) / stored_value
                assert relative_error < 1e-9, \
                    f"Failed for {stored_value} yuan -> {display_unit}: {retrieved_value}"
    
    @given(
        amounts=st.lists(
            valid_amount_values(),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=50)
    def test_batch_display_conversion_preserves_all_storage_values(self, amounts):
        """
        Property: Converting multiple amounts for display should preserve 
        all storage values when converted back.
        """
        converter = UnitConverter()
        
        # Create DataFrame with amounts in yuan (storage)
        df = pd.DataFrame({'amount': amounts})
        
        # Convert to display unit (yi_yuan)
        df_display = df.copy()
        df_display['amount'] = df_display['amount'].apply(
            lambda x: converter.convert_amount(x, 'yuan', 'yi_yuan')
        )
        
        # Convert back to storage unit (yuan)
        df_retrieved = df_display.copy()
        df_retrieved['amount'] = df_retrieved['amount'].apply(
            lambda x: converter.convert_amount(x, 'yi_yuan', 'yuan')
        )
        
        # All values should be preserved
        pd.testing.assert_series_equal(
            df['amount'],
            df_retrieved['amount'],
            check_names=False,
            rtol=1e-9
        )


# ============================================================================
# Error Handling and Edge Cases
# ============================================================================

class TestUnitConverterErrorHandling:
    """Test error handling and edge cases for UnitConverter."""
    
    def test_unsupported_source_unit_raises_error(self):
        """Property: Using an unsupported source unit should raise ValueError."""
        converter = UnitConverter()
        
        with pytest.raises(ValueError) as exc_info:
            converter.convert_amount(100, 'invalid_unit', 'yuan')
        
        assert 'Unsupported source unit' in str(exc_info.value)
        assert 'invalid_unit' in str(exc_info.value)
    
    def test_unsupported_target_unit_raises_error(self):
        """Property: Using an unsupported target unit should raise ValueError."""
        converter = UnitConverter()
        
        with pytest.raises(ValueError) as exc_info:
            converter.convert_amount(100, 'yuan', 'invalid_unit')
        
        assert 'Unsupported target unit' in str(exc_info.value)
        assert 'invalid_unit' in str(exc_info.value)
    
    def test_zero_amount_converts_correctly(self):
        """Property: Zero amounts should convert to zero in any unit."""
        converter = UnitConverter()
        
        for from_unit in ['yuan', 'wan_yuan', 'yi_yuan']:
            for to_unit in ['yuan', 'wan_yuan', 'yi_yuan']:
                result = converter.convert_amount(0, from_unit, to_unit)
                assert result == 0
    
    def test_dataframe_with_nan_values_preserves_nan(self):
        """Property: NaN values in DataFrames should be preserved during conversion."""
        converter = UnitConverter()
        
        df = pd.DataFrame({
            'amount1': [100, np.nan, 300],
            'amount2': [np.nan, 200, np.nan]
        })
        
        field_units = {
            'amount1': 'wan_yuan',
            'amount2': 'yi_yuan'
        }
        
        result = converter.convert_dataframe_amounts(df, field_units)
        
        # NaN positions should be preserved
        assert pd.isna(result.loc[1, 'amount1'])
        assert pd.isna(result.loc[0, 'amount2'])
        assert pd.isna(result.loc[2, 'amount2'])
        
        # Non-NaN values should be converted
        assert result.loc[0, 'amount1'] == 100 * 10000
        assert result.loc[2, 'amount1'] == 300 * 10000
        assert result.loc[1, 'amount2'] == 200 * 100000000
    
    def test_dataframe_with_missing_fields_ignores_them(self):
        """Property: Fields specified in amount_fields but not in DataFrame should be ignored."""
        converter = UnitConverter()
        
        df = pd.DataFrame({
            'amount1': [100, 200],
            'amount2': [300, 400]
        })
        
        field_units = {
            'amount1': 'wan_yuan',
            'amount2': 'yi_yuan',
            'amount3': 'yuan'  # This field doesn't exist in df
        }
        
        # Should not raise error
        result = converter.convert_dataframe_amounts(df, field_units)
        
        # Existing fields should be converted
        assert result.loc[0, 'amount1'] == 100 * 10000
        assert result.loc[0, 'amount2'] == 300 * 100000000
    
    @given(
        amount=st.floats(
            min_value=1e-10,
            max_value=1e-10,
            allow_nan=False,
            allow_infinity=False
        )
    )
    @settings(max_examples=20)
    def test_very_small_amounts_convert_correctly(self, amount):
        """Property: Very small amounts should convert without underflow."""
        converter = UnitConverter()
        
        # Convert to yuan
        result = converter.convert_amount(amount, 'yuan', 'yuan')
        
        # Should preserve the value
        assert abs(result - amount) < 1e-15
    
    @given(
        amount=st.floats(
            min_value=1e10,
            max_value=1e11,
            allow_nan=False,
            allow_infinity=False
        )
    )
    @settings(max_examples=20)
    def test_large_amounts_convert_correctly(self, amount):
        """Property: Large amounts should convert without overflow."""
        converter = UnitConverter()
        
        # Convert from yuan to wan_yuan
        result = converter.convert_amount(amount, 'yuan', 'wan_yuan')
        expected = amount / 10000
        
        # Should preserve relative precision
        relative_error = abs(result - expected) / expected
        assert relative_error < 1e-9


# ============================================================================
# Unit Conversion Consistency Tests
# ============================================================================

class TestUnitConversionConsistency:
    """Test consistency properties of unit conversions."""
    
    @given(
        amount=valid_amount_values(),
        unit1=valid_units(),
        unit2=valid_units()
    )
    @settings(max_examples=100)
    def test_conversion_is_transitive(self, amount, unit1, unit2):
        """
        Property: Converting A->B->C should equal converting A->C directly.
        """
        converter = UnitConverter()
        
        # Direct conversion
        direct = converter.convert_amount(
            converter.convert_amount(amount, unit1, unit2),
            unit2,
            'yuan'
        )
        
        # Should equal converting to yuan directly
        to_yuan = converter.convert_amount(amount, unit1, 'yuan')
        
        # Results should be equal within precision
        if to_yuan == 0:
            assert abs(direct - to_yuan) < 1e-9
        else:
            relative_error = abs(direct - to_yuan) / to_yuan
            assert relative_error < 1e-9
    
    @given(
        amount1=valid_amount_values(),
        amount2=valid_amount_values(),
        unit=valid_units()
    )
    @settings(max_examples=100)
    def test_conversion_preserves_ordering(self, amount1, amount2, unit):
        """
        Property: If amount1 < amount2, then converted amounts maintain the same ordering.
        """
        assume(amount1 != amount2)  # Skip if equal
        
        converter = UnitConverter()
        
        converted1 = converter.convert_amount(amount1, unit, 'yuan')
        converted2 = converter.convert_amount(amount2, unit, 'yuan')
        
        # Ordering should be preserved
        if amount1 < amount2:
            assert converted1 < converted2
        else:
            assert converted1 > converted2
    
    @given(
        amount=valid_amount_values(),
        unit=valid_units(),
        scale=st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_conversion_is_linear(self, amount, unit, scale):
        """
        Property: Converting (amount * scale) should equal (converted amount) * scale.
        """
        converter = UnitConverter()
        
        # Convert scaled amount
        scaled_then_converted = converter.convert_amount(amount * scale, unit, 'yuan')
        
        # Convert then scale
        converted_then_scaled = converter.convert_amount(amount, unit, 'yuan') * scale
        
        # Should be equal within precision
        if converted_then_scaled == 0:
            assert abs(scaled_then_converted - converted_then_scaled) < 1e-9
        else:
            relative_error = abs(scaled_then_converted - converted_then_scaled) / converted_then_scaled
            assert relative_error < 1e-6  # Slightly relaxed due to floating point
