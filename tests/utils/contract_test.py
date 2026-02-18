"""
Contract testing (Golden Sample) framework for market data modules.

This framework helps detect upstream API changes by comparing current responses
against saved "golden samples" of expected data structures.

Usage:
    1. Create golden samples for your module
    2. Use GoldenSampleValidator to validate responses
    3. Update golden samples when upstream changes are intentional
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd
import pytest


class GoldenSampleValidator:
    """Validator for contract testing using golden samples."""

    def __init__(self, module_name: str, samples_dir: Path | None = None):
        """
        Initialize golden sample validator.

        Args:
            module_name: Name of the module (e.g., 'fundflow', 'disclosure')
            samples_dir: Directory to store golden samples (default: tests/golden_samples/)
        """
        self.module_name = module_name
        if samples_dir is None:
            # Default to tests/golden_samples/
            test_dir = Path(__file__).parent.parent
            samples_dir = test_dir / "golden_samples"
        self.samples_dir = samples_dir / module_name
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    def save_golden_sample(
        self, sample_name: str, data: pd.DataFrame, metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Save a golden sample for future comparison.

        Args:
            sample_name: Name of the sample (e.g., 'stock_fund_flow_600000')
            data: DataFrame to save as golden sample
            metadata: Optional metadata about the sample
        """
        sample_path = self.samples_dir / f"{sample_name}.json"

        sample_data = []
        if not data.empty:
            df_sample = data.head(3).copy()
            for col in df_sample.columns:
                if pd.api.types.is_datetime64_any_dtype(df_sample[col]):
                    df_sample[col] = df_sample[col].astype(str)
            sample_data = json.loads(df_sample.to_json(orient="records", date_format="iso"))

        schema = {
            "columns": list(data.columns),
            "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
            "row_count": len(data),
            "sample_data": sample_data,
        }

        if metadata:
            schema["metadata"] = metadata

        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

    def load_golden_sample(self, sample_name: str) -> dict[str, Any]:
        """
        Load a golden sample.

        Args:
            sample_name: Name of the sample to load

        Returns:
            Dictionary containing golden sample schema

        Raises:
            FileNotFoundError: If golden sample doesn't exist
        """
        sample_path = self.samples_dir / f"{sample_name}.json"

        if not sample_path.exists():
            raise FileNotFoundError(
                f"Golden sample not found: {sample_path}\n"
                f"Create it first using save_golden_sample()"
            )

        with open(sample_path, encoding="utf-8") as f:
            return json.load(f)

    def validate_schema(
        self, sample_name: str, data: pd.DataFrame, strict_dtypes: bool = False
    ) -> list[str]:
        """
        Validate DataFrame against golden sample schema.

        Args:
            sample_name: Name of the golden sample to compare against
            data: DataFrame to validate
            strict_dtypes: If True, enforce exact dtype matching

        Returns:
            List of validation errors (empty if valid)
        """
        golden = self.load_golden_sample(sample_name)
        errors = []

        # Check columns
        expected_columns = golden["columns"]
        actual_columns = list(data.columns)

        if expected_columns != actual_columns:
            missing = set(expected_columns) - set(actual_columns)
            extra = set(actual_columns) - set(expected_columns)

            if missing:
                errors.append(f"Missing columns: {missing}")
            if extra:
                errors.append(f"Extra columns: {extra}")
            if set(expected_columns) == set(actual_columns):
                errors.append(
                    f"Column order changed: expected {expected_columns}, got {actual_columns}"
                )

        # Check dtypes (if strict)
        if strict_dtypes:
            expected_dtypes = golden["dtypes"]
            for col in expected_columns:
                if col in data.columns:
                    expected_dtype = expected_dtypes[col]
                    actual_dtype = str(data[col].dtype)
                    if expected_dtype != actual_dtype:
                        errors.append(
                            f"Column '{col}' dtype mismatch: "
                            f"expected {expected_dtype}, got {actual_dtype}"
                        )

        return errors

    def assert_schema_matches(
        self, sample_name: str, data: pd.DataFrame, strict_dtypes: bool = False
    ) -> None:
        """
        Assert that DataFrame matches golden sample schema.

        Args:
            sample_name: Name of the golden sample to compare against
            data: DataFrame to validate
            strict_dtypes: If True, enforce exact dtype matching

        Raises:
            AssertionError: If schema doesn't match
        """
        errors = self.validate_schema(sample_name, data, strict_dtypes)

        if errors:
            error_msg = f"Schema validation failed for '{sample_name}':\n"
            error_msg += "\n".join(f"  - {error}" for error in errors)
            raise AssertionError(error_msg)

    def list_samples(self) -> list[str]:
        """
        List all available golden samples for this module.

        Returns:
            List of sample names
        """
        if not self.samples_dir.exists():
            return []

        return [f.stem for f in self.samples_dir.glob("*.json")]

    def delete_sample(self, sample_name: str) -> None:
        """
        Delete a golden sample.

        Args:
            sample_name: Name of the sample to delete
        """
        sample_path = self.samples_dir / f"{sample_name}.json"
        if sample_path.exists():
            sample_path.unlink()


def create_golden_sample_if_missing(
    validator: GoldenSampleValidator,
    sample_name: str,
    data: pd.DataFrame,
    metadata: dict[str, Any] | None = None,
    update_mode: bool = False,
) -> None:
    """
    Helper function to create golden sample if it doesn't exist.

    Useful for test setup - creates sample on first run, validates on subsequent runs.

    Args:
        validator: GoldenSampleValidator instance
        sample_name: Name of the sample
        data: DataFrame to save/validate
        metadata: Optional metadata
        update_mode: If True, always update the golden sample
    """
    sample_path = validator.samples_dir / f"{sample_name}.json"

    if update_mode or not sample_path.exists():
        validator.save_golden_sample(sample_name, data, metadata)
        print(f"Golden sample created/updated: {sample_name}")
    else:
        validator.assert_schema_matches(sample_name, data)


# Pytest fixtures for contract testing
@pytest.fixture
def golden_sample_validator(request):
    """
    Pytest fixture to create a GoldenSampleValidator for the current test module.

    Usage in tests:
        def test_schema(golden_sample_validator):
            validator = golden_sample_validator('fundflow')
            # Use validator...
    """

    def _create_validator(module_name: str) -> GoldenSampleValidator:
        return GoldenSampleValidator(module_name)

    return _create_validator


@pytest.fixture
def update_golden_samples(request):
    """
    Pytest fixture to enable golden sample update mode.

    Usage:
        pytest tests/test_fundflow.py --update-golden-samples

    In test:
        def test_schema(update_golden_samples):
            if update_golden_samples:
                # Update mode
            else:
                # Validation mode
    """
    return request.config.getoption("--update-golden-samples", default=False)


def pytest_addoption(parser):
    """Add pytest command line option for updating golden samples."""
    parser.addoption(
        "--update-golden-samples",
        action="store_true",
        default=False,
        help="Update golden samples instead of validating against them",
    )


# Example usage in tests:
"""
from tests.utils.contract_test import GoldenSampleValidator, create_golden_sample_if_missing

def test_fund_flow_schema():
    '''Test fund flow data schema matches golden sample.'''
    from akshare_one.modules.fundflow import get_stock_fund_flow
    
    # Get data
    df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-31')
    
    # Validate against golden sample
    validator = GoldenSampleValidator('fundflow')
    validator.assert_schema_matches('stock_fund_flow', df)

def test_create_golden_sample():
    '''Create golden sample for fund flow data.'''
    from akshare_one.modules.fundflow import get_stock_fund_flow
    
    # Get data
    df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-31')
    
    # Create golden sample
    validator = GoldenSampleValidator('fundflow')
    validator.save_golden_sample(
        'stock_fund_flow',
        df,
        metadata={
            'description': 'Stock fund flow data for 600000',
            'date_range': '2024-01-01 to 2024-01-31',
            'created_at': '2024-01-15'
        }
    )
"""
