# Testing Framework for akshare-one

This directory contains the testing framework for akshare-one market data modules.

## Structure

```
tests/
├── conftest.py                 # Pytest configuration and shared fixtures
├── templates/                  # Test templates for new modules
│   └── test_template.py       # Unit test template
├── utils/                      # Testing utilities
│   ├── __init__.py
│   ├── contract_test.py       # Contract testing (golden samples)
│   └── integration_helpers.py # Integration test helpers
├── golden_samples/            # Golden sample data (created on first run)
│   ├── fundflow/
│   ├── disclosure/
│   └── ...
└── test_*.py                  # Actual test files

```

## Test Types

### 1. Unit Tests

Unit tests verify individual components in isolation using mocks.

**Template**: `tests/templates/test_template.py`

**Example**:
```python
def test_provider_initialization():
    """Test provider can be initialized."""
    provider = FundFlowProvider()
    assert provider is not None
```

**Run**:
```bash
pytest tests/test_fundflow.py
```

### 2. Contract Tests (Golden Samples)

Contract tests detect upstream API changes by comparing against saved "golden samples".

**Framework**: `tests/utils/contract_test.py`

**Example**:
```python
from tests.utils.contract_test import GoldenSampleValidator

def test_fund_flow_schema():
    """Test fund flow data schema matches golden sample."""
    from akshare_one.modules.fundflow import get_stock_fund_flow
    
    df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-31')
    
    validator = GoldenSampleValidator('fundflow')
    validator.assert_schema_matches('stock_fund_flow', df)
```

**Create Golden Sample**:
```python
def test_create_golden_sample():
    """Create golden sample for fund flow data."""
    from akshare_one.modules.fundflow import get_stock_fund_flow
    
    df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-31')
    
    validator = GoldenSampleValidator('fundflow')
    validator.save_golden_sample(
        'stock_fund_flow',
        df,
        metadata={'description': 'Stock fund flow data for 600000'}
    )
```

**Update Golden Samples**:
```bash
pytest tests/test_fundflow.py --update-golden-samples
```

### 3. Integration Tests

Integration tests verify real API calls and end-to-end functionality.

**Framework**: `tests/utils/integration_helpers.py`

**Example**:
```python
import pytest
from tests.utils.integration_helpers import skip_if_no_network, DataFrameValidator

@pytest.mark.integration
@skip_if_no_network()
def test_real_api_call(rate_limiter):
    """Test with real API call."""
    from akshare_one.modules.fundflow import get_stock_fund_flow
    
    # Rate limit to avoid overwhelming API
    rate_limiter.wait()
    
    df = get_stock_fund_flow('600000', start_date='2024-01-01', end_date='2024-01-31')
    
    # Validate result
    validator = DataFrameValidator()
    validator.validate_required_columns(df, ['date', 'symbol', 'close'])
    validator.validate_json_compatible(df)
```

**Run**:
```bash
# Run integration tests
pytest tests/ --run-integration

# Run specific integration test
pytest tests/test_fundflow.py::test_real_api_call --run-integration
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_fundflow.py
```

### Run Specific Test
```bash
pytest tests/test_fundflow.py::TestProviderBasics::test_provider_initialization
```

### Run with Coverage
```bash
pytest tests/ --cov=akshare_one --cov-report=html
```

### Run Integration Tests
```bash
pytest tests/ --run-integration
```

### Run Slow Tests
```bash
pytest tests/ --run-slow
```

### Update Golden Samples
```bash
pytest tests/ --update-golden-samples
```

### Run Tests Matching Pattern
```bash
pytest tests/ -k "fund_flow"
```

### Run Tests with Verbose Output
```bash
pytest tests/ -v
```

### Run Tests and Stop on First Failure
```bash
pytest tests/ -x
```

## Test Markers

Tests can be marked with decorators to categorize them:

- `@pytest.mark.integration` - Integration test (requires network)
- `@pytest.mark.slow` - Slow running test
- `@pytest.mark.contract` - Contract test (golden sample)

**Example**:
```python
@pytest.mark.integration
@pytest.mark.slow
def test_large_dataset():
    """Test with large dataset."""
    pass
```

## Fixtures

Common fixtures are available in `conftest.py`:

- `rate_limiter` - Rate limiter for API calls
- `df_validator` - DataFrame validator
- `mock_data_generator` - Mock data generator
- `sample_symbols` - Sample stock symbols
- `sample_date_range` - Sample date range

**Example**:
```python
def test_with_fixtures(sample_symbols, sample_date_range):
    """Test using fixtures."""
    for symbol in sample_symbols:
        df = get_data(symbol, **sample_date_range)
        assert not df.empty
```

## Creating Tests for New Modules

### Step 1: Copy Template
```bash
cp tests/templates/test_template.py tests/test_<module_name>.py
```

### Step 2: Replace Placeholders
- Replace `MODULE_NAME` with your module name (e.g., 'fundflow')
- Replace `PROVIDER_CLASS` with your provider class name
- Update imports

### Step 3: Implement Test Methods
Remove `pass` statements and implement actual test logic.

### Step 4: Create Golden Samples
Run tests with `--update-golden-samples` to create initial golden samples.

### Step 5: Run Tests
```bash
pytest tests/test_<module_name>.py -v
```

## Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names
- One assertion per test (when possible)

### 2. Test Coverage
- Test happy path
- Test edge cases (empty results, invalid parameters)
- Test error handling
- Test JSON compatibility

### 3. Mock vs Real Data
- Use mocks for unit tests
- Use real API calls for integration tests
- Rate limit integration tests

### 4. Golden Samples
- Create golden samples for all public APIs
- Update golden samples when upstream changes are intentional
- Review changes carefully before updating

### 5. Test Data
- Use realistic test data
- Don't hardcode dates (use relative dates)
- Clean up test data after tests

## Troubleshooting

### Golden Sample Not Found
```
FileNotFoundError: Golden sample not found: tests/golden_samples/fundflow/stock_fund_flow.json
```

**Solution**: Create the golden sample first:
```bash
pytest tests/test_fundflow.py::test_create_golden_sample
```

### Schema Validation Failed
```
AssertionError: Schema validation failed for 'stock_fund_flow':
  - Missing columns: {'close_price'}
  - Extra columns: {'close'}
```

**Solution**: Upstream API changed. Review changes and update golden sample if intentional:
```bash
pytest tests/test_fundflow.py --update-golden-samples
```

### Integration Test Skipped
```
SKIPPED [1] tests/test_fundflow.py:123: need --run-integration option to run
```

**Solution**: Run with integration flag:
```bash
pytest tests/test_fundflow.py --run-integration
```

### Rate Limited
If you get rate limited by upstream API:
1. Reduce test frequency
2. Use mocks instead of real API calls
3. Add delays between tests

## Contributing

When adding new tests:
1. Follow the template structure
2. Add docstrings to all test functions
3. Use appropriate markers
4. Create golden samples
5. Ensure tests pass locally before committing

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest markers](https://docs.pytest.org/en/stable/mark.html)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
