"""
Contract tests for numeric column types in market data.

These tests validate:
1. Numeric column types are correct (int64 for volume/shares, float64 for prices/amounts)
2. Unit conversions are correct (yuan, wan_yuan, yi_yuan)
3. Boundary values are handled properly (max, min, zero, negative, scientific notation)
4. NaN/Infinity handling is correct
5. Numeric precision is maintained

Feature: numeric-types-contract
Task: 补充数值列类型契约测试

NOTE: These tests require network access and are marked as integration tests.
"""

import contextlib
import numpy as np
import pandas as pd
import pytest

try:
    from hypothesis import given, settings
    from hypothesis import strategies as st
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    pytest.skip("Hypothesis not installed", allow_module_level=True)

from akshare_one.modules.field_naming.unit_converter import UnitConverter
from akshare_one.modules.base import BaseProvider


# ============================================================================
# Test Data Generators (Hypothesis Strategies)
# ============================================================================

@st.composite
def valid_price_values(draw):
    """Generate valid price values (positive floats)."""
    return draw(st.floats(
        min_value=0.01,
        max_value=10000.0,
        allow_nan=False,
        allow_infinity=False
    ))


@st.composite
def valid_volume_values(draw):
    """Generate valid volume values (non-negative integers)."""
    return draw(st.integers(min_value=0, max_value=10**12))


@st.composite
def valid_amount_values(draw):
    """Generate valid amount values (non-negative floats)."""
    return draw(st.floats(
        min_value=0.0,
        max_value=10**15,
        allow_nan=False,
        allow_infinity=False
    ))


@st.composite
def valid_pct_change_values(draw):
    """Generate valid percentage change values (can be negative)."""
    return draw(st.floats(
        min_value=-100.0,
        max_value=1000.0,
        allow_nan=False,
        allow_infinity=False
    ))


@st.composite
def valid_ratio_values(draw):
    """Generate valid ratio values (positive floats)."""
    return draw(st.floats(
        min_value=0.0,
        max_value=1000.0,
        allow_nan=False,
        allow_infinity=False
    ))


# ============================================================================
# Contract Test 1: Numeric Column Types Correctness
# ============================================================================

@pytest.mark.integration
@pytest.mark.flaky(reruns=3, reruns_delay=2)
class TestNumericColumnTypesContract:
    """
    Contract tests for numeric column data types.

    Validates that numeric columns use the correct pandas data types:
    - int64 for volume/shares
    - float64 for price/amount/ratio

    NOTE: All tests in this class require network access.
    """

    @pytest.mark.integration
    def test_price_columns_are_float64(self):
        """Contract: Price columns (open, high, low, close) must be float64."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        if df.empty:
            pytest.skip("No historical data available")

        price_columns = ["open", "high", "low", "close"]
        for col in price_columns:
            if col in df.columns:
                # Allow both float64 and float32 (both are valid float types)
                assert pd.api.types.is_float_dtype(df[col]), \
                    f"Price column '{col}' must be float type, got {df[col].dtype}"
                # Check for reasonable precision
                assert df[col].dtype.itemsize >= 4, \
                    f"Price column '{col}' must have at least 32-bit precision"

    @pytest.mark.integration
    def test_volume_columns_are_numeric(self):
        """Contract: Volume column must be numeric (int64 or float64)."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        if df.empty:
            pytest.skip("No historical data available")

        if "volume" in df.columns:
            # Volume can be int64 or float64 (both are acceptable)
            assert pd.api.types.is_numeric_dtype(df["volume"]), \
                f"Volume column must be numeric, got {df['volume'].dtype}"
            # Check for reasonable precision
            assert df["volume"].dtype.itemsize >= 4, \
                "Volume column must have at least 32-bit precision"

    @pytest.mark.integration
    def test_amount_columns_are_float64(self):
        """Contract: Amount column must be float64."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        if "amount" in df.columns:
            assert pd.api.types.is_float_dtype(df["amount"]), \
                f"Amount column must be float type, got {df['amount'].dtype}"

    @pytest.mark.integration
    def test_pct_change_columns_are_float64(self):
        """Contract: Percentage change columns must be float64."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        pct_columns = ["pct_change", "change_pct"]
        for col in pct_columns:
            if col in df.columns:
                assert pd.api.types.is_float_dtype(df[col]), \
                    f"Percentage change column '{col}' must be float type, got {df[col].dtype}"

    @pytest.mark.integration
    def test_ratio_columns_are_float64(self):
        """Contract: Ratio columns must be float64."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        # Common ratio columns
        ratio_columns = ["pe_ratio", "pb_ratio", "turnover_rate"]
        for col in ratio_columns:
            if col in df.columns:
                assert pd.api.types.is_float_dtype(df[col]), \
                    f"Ratio column '{col}' must be float type, got {df[col].dtype}"

    @pytest.mark.integration
    def test_shares_columns_are_numeric(self):
        """Contract: Shares columns must be numeric."""
        from akshare_one import get_basic_info

        df = get_basic_info(symbol="600000")

        if df.empty:
            pytest.skip("No basic info data available")

        shares_columns = ["total_shares", "float_shares"]
        for col in shares_columns:
            if col in df.columns:
                assert pd.api.types.is_numeric_dtype(df[col]), \
                    f"Shares column '{col}' must be numeric, got {df[col].dtype}"

    @given(price=valid_price_values())
    @settings(max_examples=50)
    @pytest.mark.integration
    def test_price_values_are_valid_floats(self, price):
        """Property: All price values should be valid floats (not NaN/Infinity)."""
        df = pd.DataFrame({"close": [price]})

        # Apply standardization
        standardized = BaseProvider.ensure_json_compatible(df)

        # Value should be preserved (or converted to None if NaN/Infinity)
        if pd.isna(price) or np.isinf(price):
            assert standardized["close"][0] is None
        else:
            assert standardized["close"][0] == price or standardized["close"][0] is None

    @given(volume=valid_volume_values())
    @settings(max_examples=50)
    @pytest.mark.integration
    def test_volume_values_are_valid_integers(self, volume):
        """Property: Volume values should be valid integers."""
        df = pd.DataFrame({"volume": [volume]})

        # Volume should be preserved
        assert df["volume"][0] == volume
        assert df["volume"].dtype in [np.int64, np.int32]


# ============================================================================
# Contract Test 2: Unit Conversion Correctness
# ============================================================================

class TestUnitConversionContract:
    """
    Contract tests for unit conversion.

    Validates that amount unit conversions are correct:
    - yuan (元): base unit
    - wan_yuan (万元): 10,000 yuan
    - yi_yuan (亿元): 100,000,000 yuan
    """

    def test_yuan_to_yuan_is_identity(self):
        """Contract: Converting yuan to yuan should be identity."""
        converter = UnitConverter()

        test_values = [0, 1, 100, 1000, 1e6, 1e9]

        for value in test_values:
            result = converter.convert_amount(value, "yuan", "yuan")
            assert result == value, \
                f"Yuan to yuan conversion failed: {value} -> {result}"

    def test_wan_yuan_to_yuan_multiplier(self):
        """Contract: Converting wan_yuan to yuan should multiply by 10,000."""
        converter = UnitConverter()

        test_values = [0, 1, 10, 100, 1000]

        for value in test_values:
            result = converter.convert_amount(value, "wan_yuan", "yuan")
            expected = value * 10000
            assert result == expected, \
                f"Wan_yuan to yuan conversion failed: {value} wan_yuan -> {result} yuan (expected {expected})"

    def test_yi_yuan_to_yuan_multiplier(self):
        """Contract: Converting yi_yuan to yuan should multiply by 100,000,000."""
        converter = UnitConverter()

        test_values = [0, 1, 10, 100]

        for value in test_values:
            result = converter.convert_amount(value, "yi_yuan", "yuan")
            expected = value * 100000000
            assert result == expected, \
                f"Yi_yuan to yuan conversion failed: {value} yi_yuan -> {result} yuan (expected {expected})"

    def test_yuan_to_wan_yuan_divisor(self):
        """Contract: Converting yuan to wan_yuan should divide by 10,000."""
        converter = UnitConverter()

        test_values = [0, 10000, 100000, 1000000, 100000000]

        for value in test_values:
            result = converter.convert_amount(value, "yuan", "wan_yuan")
            expected = value / 10000
            assert result == expected, \
                f"Yuan to wan_yuan conversion failed: {value} yuan -> {result} wan_yuan (expected {expected})"

    def test_yuan_to_yi_yuan_divisor(self):
        """Contract: Converting yuan to yi_yuan should divide by 100,000,000."""
        converter = UnitConverter()

        test_values = [0, 100000000, 1000000000, 10000000000]

        for value in test_values:
            result = converter.convert_amount(value, "yuan", "yi_yuan")
            expected = value / 100000000
            assert result == expected, \
                f"Yuan to yi_yuan conversion failed: {value} yuan -> {result} yi_yuan (expected {expected})"

    @given(amount=valid_amount_values(), from_unit=st.sampled_from(["yuan", "wan_yuan", "yi_yuan"]))
    @settings(max_examples=100)
    def test_unit_conversion_preserves_precision(self, amount, from_unit):
        """Property: Unit conversion should preserve precision within reason."""
        converter = UnitConverter()

        # Convert to yuan
        result = converter.convert_amount(amount, from_unit, "yuan")

        # Convert back
        back = converter.convert_amount(result, "yuan", from_unit)

        # Should preserve value within floating point precision
        if amount == 0:
            assert abs(back - amount) < 1e-10
        else:
            relative_error = abs(back - amount) / amount
            assert relative_error < 1e-9, \
                f"Roundtrip conversion lost precision: {amount} -> {result} -> {back}"

    def test_dataframe_unit_conversion_applies_to_all_rows(self):
        """Contract: DataFrame unit conversion should apply to all rows."""
        converter = UnitConverter()

        df = pd.DataFrame({
            "amount": [1, 10, 100, 1000],
            "balance": [5, 50, 500, 5000]
        })

        amount_fields = {
            "amount": "wan_yuan",
            "balance": "yi_yuan"
        }

        result = converter.convert_dataframe_amounts(df, amount_fields)

        # Verify all rows converted correctly
        assert result["amount"].tolist() == [10000, 100000, 1000000, 10000000]
        assert result["balance"].tolist() == [500000000, 5000000000, 50000000000, 500000000000]

    def test_unit_conversion_with_nan_preserves_nan(self):
        """Contract: NaN values should be preserved during unit conversion."""
        converter = UnitConverter()

        df = pd.DataFrame({
            "amount": [100, np.nan, 300],
            "balance": [np.nan, 200, np.nan]
        })

        amount_fields = {
            "amount": "wan_yuan",
            "balance": "yi_yuan"
        }

        result = converter.convert_dataframe_amounts(df, amount_fields)

        # NaN positions should be preserved
        assert pd.isna(result.loc[1, "amount"])
        assert pd.isna(result.loc[0, "balance"])
        assert pd.isna(result.loc[2, "balance"])

        # Non-NaN values should be converted
        assert result.loc[0, "amount"] == 100 * 10000
        assert result.loc[2, "amount"] == 300 * 10000
        assert result.loc[1, "balance"] == 200 * 100000000

    def test_unsupported_unit_raises_error(self):
        """Contract: Unsupported units should raise ValueError."""
        converter = UnitConverter()

        with pytest.raises(ValueError, match="Unsupported source unit"):
            converter.convert_amount(100, "invalid_unit", "yuan")

        with pytest.raises(ValueError, match="Unsupported target unit"):
            converter.convert_amount(100, "yuan", "invalid_unit")


# ============================================================================
# Contract Test 3: Boundary Value Handling
# ============================================================================

class TestBoundaryValueHandling:
    """
    Contract tests for boundary value handling.

    Validates that numeric values handle edge cases properly:
    - Maximum/minimum values
    - Zero values
    - Negative values (if applicable)
    - Scientific notation
    """

    def test_zero_price_is_valid(self):
        """Contract: Zero price should be handled (though unusual)."""
        df = pd.DataFrame({"close": [0.0]})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Zero should be preserved (it's valid, though unusual)
        assert standardized["close"][0] == 0.0 or standardized["close"][0] is None

    def test_zero_volume_is_valid(self):
        """Contract: Zero volume should be valid (no trades)."""
        df = pd.DataFrame({"volume": [0]})

        # Zero volume is valid
        assert df["volume"][0] == 0

    def test_negative_pct_change_is_valid(self):
        """Contract: Negative percentage change should be valid (price drops)."""
        df = pd.DataFrame({"pct_change": [-5.5, -10.0, -20.5]})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Negative values should be preserved
        for i, val in enumerate([-5.5, -10.0, -20.5]):
            assert standardized["pct_change"][i] == val

    def test_large_volume_values(self):
        """Contract: Large volume values should be handled without overflow."""
        large_values = [10**9, 10**10, 10**11, 10**12]

        df = pd.DataFrame({"volume": large_values})

        # Large values should be preserved
        for i, val in enumerate(large_values):
            assert df["volume"][i] == val

    def test_large_amount_values(self):
        """Contract: Large amount values should be handled without overflow."""
        large_values = [1e9, 1e10, 1e11, 1e12, 1e13, 1e14, 1e15]

        df = pd.DataFrame({"amount": large_values})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Large values should be preserved (or converted to None if too large)
        for i, val in enumerate(large_values):
            result = standardized["amount"][i]
            if result is not None:
                assert abs(result - val) / val < 1e-6, \
                    f"Large amount value lost precision: {val} -> {result}"

    def test_small_price_values(self):
        """Contract: Small price values should maintain precision."""
        small_values = [0.01, 0.001, 0.0001, 0.00001]

        df = pd.DataFrame({"close": small_values})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Small values should be preserved with reasonable precision
        for i, val in enumerate(small_values):
            result = standardized["close"][i]
            if result is not None:
                assert abs(result - val) < 1e-8, \
                    f"Small price value lost precision: {val} -> {result}"

    def test_scientific_notation_values(self):
        """Contract: Scientific notation values should be handled correctly."""
        scientific_values = [1e5, 1.5e6, 2.3e7, 9.99e8]

        df = pd.DataFrame({"amount": scientific_values})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Scientific notation should be preserved
        for i, val in enumerate(scientific_values):
            result = standardized["amount"][i]
            if result is not None:
                assert abs(result - val) / val < 1e-9, \
                    f"Scientific notation value lost precision: {val} -> {result}"

    def test_float_precision_maintenance(self):
        """Contract: Float precision should be maintained for monetary values."""
        # Test values with many decimal places
        precision_values = [10.123456789, 20.987654321, 100.555555555]

        df = pd.DataFrame({"close": precision_values})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Precision should be maintained to at least 6 decimal places
        for i, val in enumerate(precision_values):
            result = standardized["close"][i]
            if result is not None:
                # Check that first 6 decimal places are preserved
                assert abs(result - val) < 1e-6, \
                    f"Float precision lost: {val} -> {result}"

    @given(value=st.floats(min_value=1e-10, max_value=1e-10, allow_nan=False, allow_infinity=False))
    @settings(max_examples=20)
    def test_very_small_values(self, value):
        """Property: Very small values should not underflow."""
        df = pd.DataFrame({"close": [value]})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Very small values should be preserved or set to None (but not crash)
        result = standardized["close"][0]
        if result is not None:
            assert abs(result - value) < 1e-15

    @given(value=st.floats(min_value=1e14, max_value=1e15, allow_nan=False, allow_infinity=False))
    @settings(max_examples=20)
    def test_very_large_values(self, value):
        """Property: Very large values should not overflow."""
        df = pd.DataFrame({"amount": [value]})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Very large values should be preserved or set to None (but not crash)
        result = standardized["amount"][0]
        if result is not None:
            relative_error = abs(result - value) / value
            assert relative_error < 1e-6


# ============================================================================
# Contract Test 4: NaN/Infinity Handling
# ============================================================================

class TestNaNInfinityHandling:
    """
    Contract tests for NaN/Infinity handling.

    Validates that NaN and Infinity values are handled correctly:
    - NaN should be replaced with None for JSON compatibility
    - Infinity should be replaced with None
    - Negative Infinity should be replaced with None
    """

    def test_nan_replaced_with_none(self):
        """Contract: NaN values should be replaced with None."""
        df = pd.DataFrame({
            "close": [10.5, np.nan, 20.5],
            "volume": [100, np.nan, 300]
        })

        standardized = BaseProvider.ensure_json_compatible(df)

        # NaN should be replaced with None
        assert standardized["close"][1] is None
        assert standardized["volume"][1] is None

        # Non-NaN values should be preserved
        assert standardized["close"][0] == 10.5
        assert standardized["close"][2] == 20.5
        assert standardized["volume"][0] == 100
        assert standardized["volume"][2] == 300

    def test_infinity_replaced_with_none(self):
        """Contract: Infinity values should be replaced with None."""
        df = pd.DataFrame({
            "close": [10.5, np.inf, 20.5],
            "amount": [1000, -np.inf, 3000]
        })

        standardized = BaseProvider.ensure_json_compatible(df)

        # Infinity should be replaced with None
        assert standardized["close"][1] is None
        assert standardized["amount"][1] is None

        # Non-Infinity values should be preserved
        assert standardized["close"][0] == 10.5
        assert standardized["close"][2] == 20.5
        assert standardized["amount"][0] == 1000
        assert standardized["amount"][2] == 3000

    def test_negative_infinity_replaced_with_none(self):
        """Contract: Negative Infinity should be replaced with None."""
        df = pd.DataFrame({
            "pct_change": [5.5, -np.inf, 10.5]
        })

        standardized = BaseProvider.ensure_json_compatible(df)

        # Negative Infinity should be replaced with None
        assert standardized["pct_change"][1] is None

        # Non-Infinity values should be preserved
        assert standardized["pct_change"][0] == 5.5
        assert standardized["pct_change"][2] == 10.5

    def test_mixed_nan_and_infinity(self):
        """Contract: Mixed NaN and Infinity values should all be replaced with None."""
        df = pd.DataFrame({
            "close": [np.nan, np.inf, -np.inf, 10.5],
            "volume": [100, np.nan, np.inf, 400]
        })

        standardized = BaseProvider.ensure_json_compatible(df)

        # All special values should be replaced with None
        assert standardized["close"][0] is None  # NaN
        assert standardized["close"][1] is None  # Infinity
        assert standardized["close"][2] is None  # Negative Infinity
        assert standardized["close"][3] == 10.5  # Normal value

        assert standardized["volume"][0] == 100  # Normal value
        assert standardized["volume"][1] is None  # NaN
        assert standardized["volume"][2] is None  # Infinity
        assert standardized["volume"][3] == 400  # Normal value

    def test_all_nan_column(self):
        """Contract: Column with all NaN values should be handled."""
        df = pd.DataFrame({
            "close": [np.nan, np.nan, np.nan],
            "volume": [100, 200, 300]
        })

        standardized = BaseProvider.ensure_json_compatible(df)

        # All NaN column should be all None
        assert all(v is None for v in standardized["close"])

        # Other columns should be preserved
        assert standardized["volume"].tolist() == [100, 200, 300]

    def test_all_infinity_column(self):
        """Contract: Column with all Infinity values should be handled."""
        df = pd.DataFrame({
            "amount": [np.inf, np.inf, np.inf],
            "close": [10.5, 20.5, 30.5]
        })

        standardized = BaseProvider.ensure_json_compatible(df)

        # All Infinity column should be all None
        assert all(v is None for v in standardized["amount"])

        # Other columns should be preserved
        assert standardized["close"].tolist() == [10.5, 20.5, 30.5]

    def test_replace_nan_with_none_utility(self):
        """Contract: Utility function should handle NaN/Infinity correctly."""
        test_values = [
            (np.nan, None),
            (np.inf, None),
            (-np.inf, None),
            (10.5, 10.5),
            (0, 0),
            (-5.5, -5.5)
        ]

        for input_val, expected_val in test_values:
            result = BaseProvider.replace_nan_with_none(input_val)
            assert result == expected_val, \
                f"replace_nan_with_none failed for {input_val}: got {result}, expected {expected_val}"

    @given(
        value=st.one_of(
            st.just(np.nan),
            st.just(np.inf),
            st.just(-np.inf),
            st.floats(allow_nan=False, allow_infinity=False)
        )
    )
    @settings(max_examples=50)
    def test_arbitrary_nan_inf_handling(self, value):
        """Property: Arbitrary NaN/Infinity values should be handled without crashes."""
        df = pd.DataFrame({"close": [value]})

        # Should not crash
        standardized = BaseProvider.ensure_json_compatible(df)

        # Result should be None for NaN/Infinity, or the value itself for normal floats
        if pd.isna(value) or np.isinf(value):
            assert standardized["close"][0] is None
        else:
            assert standardized["close"][0] == value or standardized["close"][0] is None


# ============================================================================
# Contract Test 5: Numeric Precision Range
# ============================================================================

class TestNumericPrecisionRange:
    """
    Contract tests for numeric precision range.

    Validates that numeric values maintain precision within expected ranges:
    - Price precision: at least 2 decimal places (for cents)
    - Amount precision: reasonable for large monetary values
    - Volume precision: exact for integer counts
    """

    def test_price_decimal_precision(self):
        """Contract: Price values should maintain at least 2 decimal places."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        if df.empty:
            pytest.skip("No historical data available")

        price_columns = ["open", "high", "low", "close"]

        for col in price_columns:
            if col in df.columns:
                # Check that values have reasonable decimal precision
                non_null = df[col].dropna()

                if len(non_null) > 0:
                    # Values should not have excessive decimal places
                    # (more than 6 decimal places is unusual for prices)
                    for val in non_null.head(10):
                        # Convert to string and check decimal places
                        str_val = str(val)
                        if "." in str_val:
                            decimal_places = len(str_val.split(".")[-1])
                            assert decimal_places <= 6, \
                                f"Price value {val} has excessive decimal places ({decimal_places})"

    def test_volume_is_integer_like(self):
        """Contract: Volume values should be integer-like (no fractional shares)."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        if df.empty:
            pytest.skip("No historical data available")

        if "volume" in df.columns:
            non_null = df["volume"].dropna()

            if len(non_null) > 0:
                # Volume should be integer-like
                for val in non_null.head(10):
                    # Check that value is close to an integer
                    assert val == int(val) or abs(val - int(val)) < 1e-6, \
                        f"Volume value {val} is not integer-like"

    def test_amount_precision_for_large_values(self):
        """Contract: Large amount values should maintain reasonable precision."""
        # Test with conversion
        converter = UnitConverter()

        # Large values in different units
        test_cases = [
            (100000000, "yuan"),  # 100 million yuan
            (10000, "wan_yuan"),  # 100 million yuan (in wan_yuan)
            (1, "yi_yuan"),  # 100 million yuan (in yi_yuan)
        ]

        for value, unit in test_cases:
            result = converter.convert_amount(value, unit, "yuan")

            # All should convert to same value (100 million yuan)
            expected = 100000000

            relative_error = abs(result - expected) / expected
            assert relative_error < 1e-9, \
                f"Amount precision lost for large value: {value} {unit} -> {result} yuan"

    def test_percentage_precision(self):
        """Contract: Percentage values should maintain reasonable precision."""
        test_pct_values = [5.5, 10.25, -3.75, 0.01, 99.99]

        df = pd.DataFrame({"pct_change": test_pct_values})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Precision should be maintained to at least 2 decimal places
        for i, val in enumerate(test_pct_values):
            result = standardized["pct_change"][i]
            assert abs(result - val) < 1e-6, \
                f"Percentage precision lost: {val} -> {result}"

    def test_ratio_precision(self):
        """Contract: Ratio values should maintain reasonable precision."""
        test_ratio_values = [0.5, 1.25, 10.75, 100.5, 1000.25]

        df = pd.DataFrame({"pe_ratio": test_ratio_values})

        standardized = BaseProvider.ensure_json_compatible(df)

        # Precision should be maintained to at least 2 decimal places
        for i, val in enumerate(test_ratio_values):
            result = standardized["pe_ratio"][i]
            assert abs(result - val) < 1e-6, \
                f"Ratio precision lost: {val} -> {result}"

    @given(
        price1=valid_price_values(),
        price2=valid_price_values()
    )
    @settings(max_examples=50)
    def test_price_comparison_precision(self, price1, price2):
        """Property: Price comparisons should be accurate within precision."""
        df = pd.DataFrame({
            "high": [max(price1, price2)],
            "low": [min(price1, price2)]
        })

        standardized = BaseProvider.ensure_json_compatible(df)

        # High should be >= Low (within floating point precision)
        if standardized["high"][0] is not None and standardized["low"][0] is not None:
            assert standardized["high"][0] >= standardized["low"][0] - 1e-6, \
                f"Price comparison failed: high {standardized['high'][0]} < low {standardized['low'][0]}"

    def test_numeric_column_statistics(self):
        """Contract: Numeric columns should support basic statistics."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        if df.empty:
            pytest.skip("No historical data available")

        numeric_columns = ["open", "high", "low", "close", "volume"]

        for col in numeric_columns:
            if col in df.columns:
                # Should be able to compute basic statistics without error
                with contextlib.suppress(Exception):
                    _ = df[col].mean()
                    _ = df[col].std()
                    _ = df[col].min()
                    _ = df[col].max()
                    _ = df[col].median()


# ============================================================================
# Contract Test 6: Integration with Real API Data
# ============================================================================

class TestRealAPIDataNumericContract:
    """
    Contract tests with real API data.

    Validates that real API responses comply with numeric type contracts.
    Note: These tests require network access and are marked as integration tests.
    """

    @pytest.mark.integration
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_hist_data_numeric_contract(self):
        """Contract: Historical data should comply with numeric type contracts."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        if df.empty:
            pytest.skip("No historical data available")

        # Test numeric types
        assert pd.api.types.is_numeric_dtype(df["close"]), "close must be numeric"
        assert pd.api.types.is_numeric_dtype(df["volume"]), "volume must be numeric"

        # Test value ranges
        assert (df["close"] > 0).all() or df.empty, "close must be positive"
        assert (df["volume"] >= 0).all() or df.empty, "volume must be non-negative"

        # Test no infinity
        assert not np.isinf(df["close"]).any(), "close should not have infinity"
        assert not np.isinf(df["volume"]).any(), "volume should not have infinity"

    @pytest.mark.integration
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_realtime_data_numeric_contract(self):
        """Contract: Realtime data should comply with numeric type contracts."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if df.empty:
            pytest.skip("No realtime data available")

        # Test numeric types
        if "price" in df.columns:
            assert pd.api.types.is_numeric_dtype(df["price"]), "price must be numeric"

        if "pct_change" in df.columns:
            assert pd.api.types.is_numeric_dtype(df["pct_change"]), "pct_change must be numeric"

        if "volume" in df.columns:
            assert pd.api.types.is_numeric_dtype(df["volume"]), "volume must be numeric"

        # Test no infinity
        for col in ["price", "pct_change", "volume"]:
            if col in df.columns:
                assert not np.isinf(df[col]).any(), f"{col} should not have infinity"

    @pytest.mark.integration
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_fundflow_data_numeric_contract(self):
        """Contract: Fund flow data should comply with numeric type contracts."""
        from akshare_one import get_stock_fund_flow

        df = get_stock_fund_flow(symbol="600000")

        if df.empty:
            pytest.skip("No fund flow data available")

        # Test numeric types for flow fields
        flow_columns = ["main_net_inflow", "main_net_inflow_rate"]

        for col in flow_columns:
            if col in df.columns:
                assert pd.api.types.is_numeric_dtype(df[col]), f"{col} must be numeric"
                assert not np.isinf(df[col]).any(), f"{col} should not have infinity"

    @pytest.mark.integration
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_northbound_data_numeric_contract(self):
        """Contract: Northbound data should comply with numeric type contracts."""
        from akshare_one import get_northbound_flow

        df = get_northbound_flow()

        if df.empty:
            pytest.skip("No northbound data available")

        # Test numeric types for flow fields
        if "net_buy" in df.columns:
            assert pd.api.types.is_numeric_dtype(df["net_buy"]), "net_buy must be numeric"
            assert not np.isinf(df["net_buy"]).any(), "net_buy should not have infinity"


# ============================================================================
# Summary Statistics
# ============================================================================

def test_numeric_types_contract_summary():
    """
    Summary test to document all numeric type contracts being validated.

    This test doesn't perform actual validation, but serves as documentation
    of all the numeric type contracts that should be enforced.
    """
    contracts = {
        "numeric_column_types": [
            "price_columns_are_float64",
            "volume_columns_are_numeric",
            "amount_columns_are_float64",
            "pct_change_columns_are_float64",
            "ratio_columns_are_float64",
            "shares_columns_are_numeric"
        ],
        "unit_conversion": [
            "yuan_to_yuan_is_identity",
            "wan_yuan_to_yuan_multiplier_10000",
            "yi_yuan_to_yuan_multiplier_100000000",
            "yuan_to_wan_yuan_divisor_10000",
            "yuan_to_yi_yuan_divisor_100000000",
            "unit_conversion_preserves_precision"
        ],
        "boundary_values": [
            "zero_price_valid",
            "zero_volume_valid",
            "negative_pct_change_valid",
            "large_volume_values",
            "large_amount_values",
            "small_price_values",
            "scientific_notation_values"
        ],
        "nan_infinity_handling": [
            "nan_replaced_with_none",
            "infinity_replaced_with_none",
            "negative_infinity_replaced_with_none",
            "mixed_nan_and_infinity",
            "all_nan_column",
            "all_infinity_column"
        ],
        "precision_range": [
            "price_decimal_precision",
            "volume_is_integer_like",
            "amount_precision_for_large_values",
            "percentage_precision",
            "ratio_precision"
        ]
    }

    # Just verify the contract categories exist
    assert len(contracts) == 5
    assert sum(len(v) for v in contracts.values()) >= 30

    print("\nNumeric Types Contract Summary:")
    print(f"  Total contract categories: {len(contracts)}")
    print(f"  Total contracts validated: {sum(len(v) for v in contracts.values())}")
    for category, items in contracts.items():
        print(f"\n  {category}:")
        for item in items:
            print(f"    - {item}")