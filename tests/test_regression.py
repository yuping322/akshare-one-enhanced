"""
Regression tests with snapshot baseline for critical APIs.

This module tests that key API responses maintain consistent structure and data types.
Uses pytest-snapshot to create and update baselines.

Run with: pytest tests/test_regression.py
Update snapshots: pytest tests/test_regression.py --snapshot-update
"""

import json
import pandas as pd
import pytest
from typing import Any

from akshare_one import (
    get_etf_list,
    get_bond_list,
    get_futures_main_contracts,
    get_index_list,
    get_stock_valuation,
)


@pytest.fixture
def snapshot_checker(snapshot):
    """Custom snapshot fixture for DataFrame structure checking."""
    return snapshot


class DataFrameSnapshot:
    """Helper class to extract DataFrame structure for snapshot comparison."""

    @staticmethod
    def extract_schema(df: pd.DataFrame) -> dict[str, Any]:
        """Extract DataFrame schema (columns, types, sample values) for snapshot."""
        if df.empty:
            return {
                "empty": True,
                "columns": [],
                "types": {},
                "sample_count": 0,
            }

        # Get column types
        types = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            # Simplify dtype names
            if "int" in dtype:
                types[col] = "int"
            elif "float" in dtype:
                types[col] = "float"
            elif "object" in dtype or "str" in dtype:
                types[col] = "str"
            elif "datetime" in dtype:
                types[col] = "datetime"
            else:
                types[col] = dtype

        # Get sample values (first 3 rows, convert to string for consistency)
        sample_values = {}
        for col in df.columns:
            try:
                sample_values[col] = [str(v) for v in df[col].head(3).tolist()]
            except Exception:
                sample_values[col] = ["ERROR_CONVERTING"]

        return {
            "empty": False,
            "columns": sorted(list(df.columns)),
            "column_count": len(df.columns),
            "row_count": len(df),
            "types": types,
            "sample_values": sample_values,
            "sample_count": 3,
        }

    @staticmethod
    def validate_against_schema(df: pd.DataFrame, schema: dict[str, Any]) -> list[str]:
        """Validate DataFrame against expected schema, return list of errors."""
        errors = []

        # Check if empty
        if schema["empty"] and not df.empty:
            errors.append("Expected empty DataFrame but got non-empty")
            return errors
        if not schema["empty"] and df.empty:
            errors.append("Expected non-empty DataFrame but got empty")
            return errors

        if schema["empty"]:
            return errors

        # Check columns
        expected_cols = set(schema["columns"])
        actual_cols = set(df.columns)

        missing_cols = expected_cols - actual_cols
        extra_cols = actual_cols - expected_cols

        if missing_cols:
            errors.append(f"Missing columns: {sorted(missing_cols)}")
        if extra_cols:
            errors.append(f"Extra columns: {sorted(extra_cols)}")

        # Check column count
        if len(df.columns) != schema["column_count"]:
            errors.append(
                f"Column count mismatch: expected {schema['column_count']}, got {len(df.columns)}"
            )

        # Check types for common columns
        common_cols = expected_cols & actual_cols
        for col in common_cols:
            expected_type = schema["types"].get(col, "unknown")
            actual_dtype = str(df[col].dtype)

            # Simplify actual dtype
            if "int" in actual_dtype:
                actual_type = "int"
            elif "float" in actual_dtype:
                actual_type = "float"
            elif "object" in actual_dtype or "str" in actual_dtype:
                actual_type = "str"
            elif "datetime" in actual_dtype:
                actual_type = "datetime"
            else:
                actual_type = actual_dtype

            if expected_type != actual_type:
                errors.append(f"Column '{col}' type mismatch: expected {expected_type}, got {actual_type}")

        return errors


# ==================== ETF Snapshot Tests ====================


@pytest.mark.integration
class TestETFRegression:
    """Regression tests for ETF API."""

    def test_etf_list_schema(self, snapshot):
        """Test ETF list maintains consistent schema."""
        df = get_etf_list(category="all", source="eastmoney")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(json.dumps(schema, indent=2, ensure_ascii=False), "etf_list_schema.json")

        # Also validate structure even when not updating snapshot
        if not df.empty:
            assert "symbol" in df.columns, "ETF list must have 'symbol' column"
            assert len(df) > 0, "ETF list should not be empty"

    def test_etf_list_stock_category(self, snapshot):
        """Test stock ETF list schema."""
        df = get_etf_list(category="stock", source="eastmoney")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(json.dumps(schema, indent=2, ensure_ascii=False), "etf_list_stock_schema.json")

    def test_etf_list_bond_category(self, snapshot):
        """Test bond ETF list schema."""
        df = get_etf_list(category="bond", source="eastmoney")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(json.dumps(schema, indent=2, ensure_ascii=False), "etf_list_bond_schema.json")


# ==================== Bond Snapshot Tests ====================


@pytest.mark.integration
class TestBondRegression:
    """Regression tests for Bond API."""

    def test_bond_list_schema(self, snapshot):
        """Test bond list maintains consistent schema."""
        df = get_bond_list(source="eastmoney")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(json.dumps(schema, indent=2, ensure_ascii=False), "bond_list_schema.json")

        # Validate essential columns
        if not df.empty:
            assert "symbol" in df.columns, "Bond list must have 'symbol' column"

    def test_bond_list_jsl_source(self, snapshot):
        """Test bond list from JSL source."""
        df = get_bond_list(source="jsl")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(json.dumps(schema, indent=2, ensure_ascii=False), "bond_list_jsl_schema.json")


# ==================== Futures Snapshot Tests ====================


@pytest.mark.integration
class TestFuturesRegression:
    """Regression tests for Futures API."""

    def test_futures_main_contracts_schema(self, snapshot):
        """Test futures main contracts maintains consistent schema."""
        df = get_futures_main_contracts(source="sina")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(json.dumps(schema, indent=2, ensure_ascii=False), "futures_main_contracts_schema.json")

        # Validate essential columns
        if not df.empty:
            assert "symbol" in df.columns, "Futures main contracts must have 'symbol' column"
            assert "contract" in df.columns, "Futures main contracts must have 'contract' column"


# ==================== Index Snapshot Tests ====================


@pytest.mark.integration
class TestIndexRegression:
    """Regression tests for Index API."""

    def test_index_list_cn_schema(self, snapshot):
        """Test Chinese index list schema."""
        df = get_index_list(category="cn", source="eastmoney")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(json.dumps(schema, indent=2, ensure_ascii=False), "index_list_cn_schema.json")

        # Validate essential columns
        if not df.empty:
            assert "symbol" in df.columns, "Index list must have 'symbol' column"

    def test_index_list_global_schema(self, snapshot):
        """Test global index list schema."""
        df = get_index_list(category="global", source="eastmoney")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(json.dumps(schema, indent=2, ensure_ascii=False), "index_list_global_schema.json")


# ==================== Valuation Snapshot Tests ====================


@pytest.mark.integration
class TestValuationRegression:
    """Regression tests for Valuation API."""

    def test_stock_valuation_schema(self, snapshot):
        """Test stock valuation schema."""
        # Use a common stock for testing
        df = get_stock_valuation(symbol="600000", source="eastmoney")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(json.dumps(schema, indent=2, ensure_ascii=False), "stock_valuation_schema.json")

        # Validate essential columns if not empty
        if not df.empty:
            # Valuation data should have key metrics
            essential_cols = ["symbol"]
            for col in essential_cols:
                assert col in df.columns, f"Stock valuation must have '{col}' column"


# ==================== Data Type Validation Tests ====================


@pytest.mark.integration
class TestDataTypeValidation:
    """Test that data types remain consistent."""

    def test_etf_numeric_fields(self):
        """Test ETF numeric fields are proper types."""
        df = get_etf_list(category="all", source="eastmoney")

        if not df.empty:
            # Check numeric columns if present
            numeric_cols = ["volume", "amount", "price"]
            for col in numeric_cols:
                if col in df.columns:
                    # Should be numeric type (int or float)
                    dtype = str(df[col].dtype)
                    assert "int" in dtype or "float" in dtype, f"Column '{col}' should be numeric, got {dtype}"

    def test_bond_numeric_fields(self):
        """Test bond numeric fields are proper types."""
        df = get_bond_list(source="eastmoney")

        if not df.empty:
            # Price and volume should be numeric if present
            numeric_cols = ["price", "volume", "amount"]
            for col in numeric_cols:
                if col in df.columns:
                    dtype = str(df[col].dtype)
                    assert "int" in dtype or "float" in dtype, f"Column '{col}' should be numeric, got {dtype}"

    def test_futures_numeric_fields(self):
        """Test futures numeric fields are proper types."""
        df = get_futures_main_contracts(source="sina")

        if not df.empty:
            # Should have string columns for identifiers
            if "symbol" in df.columns:
                dtype = str(df["symbol"].dtype)
                assert "object" in dtype or "str" in dtype, f"Column 'symbol' should be string, got {dtype}"


# ==================== Value Range Tests ====================


@pytest.mark.integration
class TestValueRanges:
    """Test that values are within reasonable ranges."""

    def test_etf_price_range(self):
        """Test ETF prices are within reasonable range."""
        df = get_etf_list(category="all", source="eastmoney")

        if not df.empty and "price" in df.columns:
            # ETF prices should be positive and reasonable (0.01 to 10000)
            prices = df["price"].dropna()
            if len(prices) > 0:
                assert all(prices >= 0), "ETF prices should be non-negative"
                assert all(prices <= 100000), "ETF prices should be below 100000 (reasonable upper bound)"

    def test_bond_price_range(self):
        """Test bond prices are within reasonable range."""
        df = get_bond_list(source="eastmoney")

        if not df.empty and "price" in df.columns:
            prices = df["price"].dropna()
            if len(prices) > 0:
                # Bond prices typically range 50-200 for convertible bonds
                assert all(prices >= 0), "Bond prices should be non-negative"
                assert all(prices <= 10000), "Bond prices should be below 10000"


# ==================== Snapshot Update Helper ====================


class TestSnapshotHelper:
    """Helper tests to understand snapshot system."""

    def test_snapshot_example(self, snapshot):
        """Example of how snapshot testing works."""
        # This test shows how to use snapshot
        data = {"key": "value", "number": 42}
        snapshot.assert_match(json.dumps(data, indent=2), "example.json")

        # When run with --snapshot-update, this creates tests/snapshots/test_snapshot_helper/test_snapshot_example/example.json
        # Future runs will compare against that file


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_regression.py -v
    # Update snapshots: python -m pytest tests/test_regression.py --snapshot-update -v
    pytest.main([__file__, "-v"])