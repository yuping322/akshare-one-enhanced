# Testing Framework Guide

## Quick Start

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_fundflow.py

# Run with coverage
pytest tests/ --cov=akshare_one --cov-report=html

# Run integration tests (requires network)
pytest tests/ --run-integration

# Update golden samples
pytest tests/ --update-golden-samples
```

## Framework Components

### 1. Unit Test Template (`tests/templates/test_template.py`)

Copy this template when creating tests for a new module:

```bash
cp tests/templates/test_template.py tests/test_<module_name>.py
```

Then replace placeholders:
- `MODULE_NAME` → your module name (e.g., 'fundflow')
- `PROVIDER_CLASS` → your provider class name
- Implement test methods

### 2. Contract Testing (`tests/utils/contract_test.py`)

Detect upstream API changes using golden samples:

```python
from tests.utils.contract_test import GoldenSampleValidator

# Create validator
validator = GoldenSampleValidator('fundflow')

# Save golden sample (first time)
validator.save_golden_sample('stock_fund_flow', df)

# Validate against golden sample (subsequent runs)
validator.assert_schema_matches('stock_fund_flow', df)
```

### 3. Integration Helpers (`tests/utils/integration_helpers.py`)

Utilities for integration testing:

```python
from tests.utils.integration_helpers import DataFrameValidator

# Validate DataFrame
validator = DataFrameValidator()
validator.validate_required_columns(df, ['date', 'symbol', 'close'])
validator.validate_json_compatible(df)
validator.validate_date_range(df, 'date', '2024-01-01', '2024-01-31')
```

## Test Checklist

When creating tests for a new module, ensure you test:

- [ ] Provider initialization
- [ ] Parameter validation (valid/invalid symbols, dates, ranges)
- [ ] Data standardization (column names, types)
- [ ] JSON compatibility (no NaN/Infinity, dates as strings)
- [ ] Empty result handling
- [ ] Error handling (timeout, connection errors, field changes)
- [ ] Factory pattern
- [ ] Public API functions
- [ ] Golden sample validation

## Example Test Structure

```python
import pytest
import pandas as pd
from tests.utils.contract_test import GoldenSampleValidator
from tests.utils.integration_helpers import DataFrameValidator

class TestFundFlowProvider:
    """Test FundFlowProvider."""
    
    def test_get_stock_fund_flow(self):
        """Test getting stock fund flow data."""
        from akshare_one.modules.fundflow import get_stock_fund_flow
        
        df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-31')
        
        # Validate structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        
        # Validate columns
        validator = DataFrameValidator()
        validator.validate_required_columns(df, ['date', 'symbol', 'close'])
        
        # Validate JSON compatibility
        validator.validate_json_compatible(df)
    
    def test_schema_stability(self):
        """Test schema matches golden sample."""
        from akshare_one.modules.fundflow import get_stock_fund_flow
        
        df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-31')
        
        validator = GoldenSampleValidator('fundflow')
        validator.assert_schema_matches('stock_fund_flow', df)
```

## Fixtures

Available fixtures in `conftest.py`:

- `rate_limiter` - Rate limiter for API calls
- `df_validator` - DataFrame validator instance
- `mock_data_generator` - Mock data generator
- `sample_symbols` - List of sample stock symbols
- `sample_date_range` - Sample date range dict

Usage:

```python
def test_with_fixtures(sample_symbols, sample_date_range):
    """Test using fixtures."""
    for symbol in sample_symbols:
        df = get_data(symbol, **sample_date_range)
        assert not df.empty
```

## Best Practices

1. **One test, one assertion** (when possible)
2. **Use descriptive test names** that explain what is being tested
3. **Test both happy path and edge cases**
4. **Mock external dependencies** in unit tests
5. **Use real APIs** only in integration tests (with rate limiting)
6. **Create golden samples** for all public APIs
7. **Update golden samples carefully** after reviewing changes

## Troubleshooting

### Golden Sample Not Found

```
FileNotFoundError: Golden sample not found
```

**Solution**: Create the golden sample first or run with `--update-golden-samples`

### Schema Validation Failed

```
AssertionError: Schema validation failed: Missing columns: {'close'}
```

**Solution**: Upstream API changed. Review and update golden sample if intentional.

### Integration Test Skipped

```
SKIPPED: need --run-integration option to run
```

**Solution**: Run with `--run-integration` flag

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest markers](https://docs.pytest.org/en/stable/mark.html)
