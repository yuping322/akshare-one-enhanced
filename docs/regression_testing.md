# Regression Testing Guide

This document describes the regression testing system for akshare-one, which uses snapshot-based testing to ensure API stability and data quality.

## Overview

Regression tests validate that critical API endpoints maintain consistent:
- Data structure (columns and their names)
- Data types (int, float, str, datetime)
- Value ranges (reasonable bounds)
- Sample data patterns

## Snapshot Testing Basics

### What are Snapshot Tests?

Snapshot tests capture the expected output of an API call and compare future runs against this baseline. If the output changes, the test fails, alerting developers to potential breaking changes.

### Key Benefits

1. **Detect Breaking Changes**: Automatically catch when APIs return different structures
2. **Document API Contracts**: Snapshots serve as living documentation
3. **Easy Updates**: Update baselines with a single flag when changes are intentional
4. **Fast Validation**: Compare structure without re-fetching data every time

## Running Regression Tests

### Basic Test Run

```bash
# Run all regression tests
pytest tests/test_regression.py -v

# Run specific test class
pytest tests/test_regression.py::TestETFRegression -v

# Run specific test
pytest tests/test_regression.py::TestETFRegression::test_etf_list_schema -v
```

### Update Snapshots

When API changes are intentional (e.g., adding a new column), update snapshots:

```bash
# Update all snapshots
pytest tests/test_regression.py --snapshot-update -v

# Update specific test snapshot
pytest tests/test_regression.py::TestETFRegression::test_etf_list_schema --snapshot-update -v
```

**Important**: Only update snapshots after verifying the changes are correct and intentional.

### Review Snapshot Changes

```bash
# Show diff between current and expected
pytest tests/test_regression.py --snapshot-details
```

## Snapshot File Structure

Snapshots are stored in `tests/snapshots/`:

```
tests/snapshots/
├── TestETFRegression/
│   ├── test_etf_list_schema/
│   │   └── etf_list_schema.json
│   ├── test_etf_list_stock_category/
│   │   └── etf_list_stock_schema.json
│   └── test_etf_list_bond_category/
│       └── etf_list_bond_schema.json
├── TestBondRegression/
│   ├── test_bond_list_schema/
│   │   └ bond_list_schema.json
│   └ test_bond_list_jsl_source/
│       └ bond_list_jsl_schema.json
└── TestFuturesRegression/
    └── test_futures_main_contracts_schema/
        └ futures_main_contracts_schema.json
```

Each snapshot file contains:
- Column names and count
- Row count
- Data types per column
- Sample values (first 3 rows)

## Creating New Regression Tests

### Step 1: Add Test Method

```python
@pytest.mark.integration
class TestNewAPIRegression:
    """Regression tests for NewAPI."""

    def test_new_api_schema(self, snapshot):
        """Test NewAPI maintains consistent schema."""
        df = get_new_api_data(source="provider")

        # Extract schema
        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(
            json.dumps(schema, indent=2, ensure_ascii=False),
            "new_api_schema.json"
        )

        # Add validation
        if not df.empty:
            assert "symbol" in df.columns
```

### Step 2: Create Initial Snapshot

```bash
# Run with --snapshot-update to create baseline
pytest tests/test_regression.py::TestNewAPIRegression::test_new_api_schema --snapshot-update -v
```

### Step 3: Verify Snapshot

Check the generated snapshot file in `tests/snapshots/TestNewAPIRegression/test_new_api_schema/`.

Ensure it captures:
- All expected columns
- Correct data types
- Representative sample values

## Test Categories

### Schema Tests

Test that DataFrame structure remains consistent:

```python
def test_api_schema(self, snapshot):
    df = get_api_data()
    schema = DataFrameSnapshot.extract_schema(df)
    snapshot.assert_match(json.dumps(schema, indent=2), "schema.json")
```

### Data Type Tests

Test that column types are correct:

```python
def test_numeric_fields(self):
    df = get_api_data()
    if not df.empty and "price" in df.columns:
        dtype = str(df["price"].dtype)
        assert "float" in dtype or "int" in dtype
```

### Value Range Tests

Test that values are within reasonable bounds:

```python
def test_price_range(self):
    df = get_api_data()
    if not df.empty and "price" in df.columns:
        prices = df["price"].dropna()
        assert all(prices >= 0)
        assert all(prices <= 100000)
```

## Best Practices

### 1. Choose Stable APIs

Create regression tests for:
- Core APIs (ETF list, Bond list, Index list)
- APIs with stable schemas
- Frequently used endpoints

Avoid testing:
- APIs with frequently changing columns
- Real-time data (prices change constantly)
- APIs still in development

### 2. Use Representative Test Data

- Test with common symbols (e.g., "600000" for stocks)
- Test multiple categories if applicable (e.g., ETF "stock", "bond")
- Test multiple sources if supported (e.g., "eastmoney", "sina")

### 3. Validate Essential Columns

Always check critical columns exist:

```python
if not df.empty:
    assert "symbol" in df.columns, "API must return 'symbol'"
    assert "timestamp" in df.columns, "API must return 'timestamp'"
```

### 4. Handle Empty Results

Some APIs may return empty results (e.g., no data for a date). Handle gracefully:

```python
schema = DataFrameSnapshot.extract_schema(df)
# Schema will include {"empty": True} if df is empty
snapshot.assert_match(json.dumps(schema, indent=2), "schema.json")
```

### 5. Don't Test Exact Values

Avoid testing exact prices or timestamps - they change. Instead:
- Test structure (columns)
- Test types (int, float, str)
- Test ranges (price > 0, price < 100000)

### 6. Document Expected Changes

When updating snapshots, document why:

```bash
# Good: Document the change reason
git commit -m "Update ETF snapshot: added 'fund_manager' column to ETF list API"

# Bad: No explanation
git commit -m "Update snapshots"
```

## Common Workflows

### Workflow 1: Adding a New Column

1. Modify API to add new column
2. Run tests - they will fail
3. Verify new column is correct
4. Update snapshots: `pytest tests/test_regression.py --snapshot-update`
5. Commit with message explaining the change

### Workflow 2: Detecting Unintended Changes

1. Run tests - they fail unexpectedly
2. Review diff: `pytest tests/test_regression.py --snapshot-details`
3. If unintended, fix the code
4. If intended, update snapshots and document

### Workflow 3: Adding New API Regression Test

1. Add test method to `test_regression.py`
2. Run with `--snapshot-update` to create baseline
3. Review generated snapshot file
4. Add additional validation (types, ranges)
5. Commit test and snapshot together

## Troubleshooting

### Test Fails: Schema Changed

```
AssertionError: Snapshot 'etf_list_schema.json' does not match
Missing columns: ['new_column']
```

**Solution**: 
- If intentional: Update snapshot with `--snapshot-update`
- If unintentional: Fix code to restore original schema

### Test Fails: Type Changed

```
AssertionError: Column 'volume' type mismatch: expected int, got float
```

**Solution**:
- Check if upstream API changed data format
- If format changed permanently: Update snapshot
- If format changed temporarily: Add type conversion in code

### Test Fails: Empty Result

```
AssertionError: Expected non-empty DataFrame but got empty
```

**Solution**:
- Check if API source is available
- Check if test parameters (symbol, date) are valid
- May be temporary issue - retry later

### Snapshot File Not Created

**Cause**: Running test without `--snapshot-update` for first time

**Solution**: Always use `--snapshot-update` when creating new tests

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Regression Tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .[dev]
      
      - name: Run regression tests
        run: |
          pytest tests/test_regression.py -v
        continue-on-error: false
      
      - name: Check for snapshot changes
        run: |
          git diff tests/snapshots/
          if git diff --quiet tests/snapshots/; then
            echo "No snapshot changes detected"
          else
            echo "::warning::Snapshots changed. Review and update if intentional."
          fi
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: regression-tests
        name: Regression Tests
        entry: pytest tests/test_regression.py -v
        language: system
        pass_filenames: false
        stages: [push]
```

## Monitoring and Maintenance

### Regular Review

Monthly review:
1. Check if all critical APIs have regression tests
2. Review snapshot changes in git history
3. Update tests for deprecated APIs
4. Add tests for new APIs

### Metrics to Track

- Number of regression tests
- Number of snapshot updates per month
- APIs without regression coverage
- Test execution time

### Deprecation Process

When deprecating an API:
1. Mark regression test as deprecated
2. Add comment explaining deprecation
3. Remove test after API is fully removed

```python
@pytest.mark.skip(reason="API deprecated, will be removed in v2.0")
def test_deprecated_api_schema(self, snapshot):
    ...
```

## Resources

- [pytest-snapshot documentation](https://github.com/joshschreibman/pytest-snapshot)
- [Testing Guide](../tests/TESTING_GUIDE.md)
- [API Contract Tests](../tests/test_api_contract.py)

## Summary

Regression testing with snapshots provides:
- Automated detection of breaking changes
- Living documentation of API contracts
- Easy baseline updates for intentional changes
- Confidence in API stability

Remember:
- Run tests regularly
- Update snapshots carefully
- Document changes clearly
- Review snapshots periodically

---

**Last Updated**: 2026-04-04
**Maintainer**: akshare-one team