# Mock Data Testing Guide

This guide explains how to write tests that run offline without network dependencies using mock data fixtures.

## Overview

The `tests/fixtures/` directory provides mock data and fixtures for testing without requiring network access. This enables:

- Tests run faster (no network latency)
- Tests are more reliable (no API rate limits or downtime)
- Tests can run in CI/CD environments without network access
- Better isolation for testing edge cases

## Directory Structure

```
tests/fixtures/
├── __init__.py                      # Package initialization
├── mock_api_responses.py            # Pytest fixtures for mocking APIs
├── northbound_fixtures.py           # Mock data for northbound module
├── blockdeal_fixtures.py            # Mock data for block deal module
└── fundflow_fixtures.py             # Mock data for fund flow module
```

## Quick Start

### 1. Basic Mock Usage

Use the provided mock fixtures in your tests:

```python
import pytest
from akshare_one.modules.northbound import get_northbound_flow

def test_with_mock(mock_northbound_flow_api):
    """Test runs without network access."""
    df = get_northbound_flow(
        start_date='2024-01-15',
        end_date='2024-01-17',
        market='all'
    )
    
    # Verify the mock was called
    mock_northbound_flow_api.assert_called_once()
    
    # Test the results
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
```

### 2. Mocking All APIs

For comprehensive mocking, use `mock_all_akshare_apis`:

```python
def test_with_all_mocks(mock_all_akshare_apis):
    """Test with all APIs mocked."""
    # All akshare APIs are mocked automatically
    df1 = get_northbound_flow(...)
    df2 = get_northbound_holdings(...)
    
    # Verify mocks were called
    mock_all_akshare_apis['stock_hsgt_hist_em'].assert_called()
```

### 3. Custom Mock Data

Create custom mock data for specific test scenarios:

```python
def test_custom_scenario(mock_api_response, mocker):
    """Test with custom mock data."""
    import pandas as pd
    
    # Create custom data
    custom_data = pd.DataFrame({
        "日期": ["2024-02-01"],
        "当日成交净买额": [100.5],
        ...
    })
    
    # Apply custom mock
    mock_api_response.add_data('stock_hsgt_hist_em', custom_data)
    mocks = mock_api_response.apply_mocks(mocker)
    
    # Test with custom data
    df = get_northbound_flow(...)
    assert df['date'].iloc[0] == '2024-02-01'
```

### 4. Testing Edge Cases

Test error handling and edge cases:

```python
def test_empty_response(empty_dataframe_mock):
    """Test handling of empty API response."""
    df = get_northbound_flow(...)
    assert df.empty
    assert 'date' in df.columns  # Still has correct structure

def test_api_error(api_error_mock):
    """Test handling of API errors."""
    df = get_northbound_flow(...)
    assert df.empty  # Returns empty DataFrame instead of raising
```

## Available Fixtures

### Module-Specific Fixtures

- `mock_northbound_flow_api`: Mock `akshare.stock_hsgt_hist_em`
- `mock_northbound_holdings_individual_api`: Mock `akshare.stock_hsgt_individual_em`
- `mock_northbound_holdings_all_api`: Mock `akshare.stock_hsgt_hold_stock_em`
- `mock_northbound_top_stocks_api`: Mock top stocks ranking
- `mock_block_deal_api`: Mock block deal data
- `mock_stock_fund_flow_api`: Mock stock fund flow
- `mock_sector_fund_flow_api`: Mock sector fund flow

### Comprehensive Fixtures

- `mock_all_akshare_apis`: Mock all commonly used APIs at once
- `empty_dataframe_mock`: Mock that returns empty DataFrame
- `api_error_mock`: Mock that raises connection error

### Helper Fixtures

- `mock_api_response`: Helper for creating custom mock scenarios

## Creating New Mock Data

To add mock data for a new module:

1. Create a new fixtures file: `tests/fixtures/new_module_fixtures.py`

```python
import pandas as pd

def get_mock_new_module_data() -> pd.DataFrame:
    """Get mock data matching akshare API format."""
    return pd.DataFrame({
        "原始列名": [...],  # Use original Chinese column names
        ...
    })
```

2. Add fixtures in `tests/fixtures/mock_api_responses.py`:

```python
@pytest.fixture
def mock_new_module_api(mocker):
    """Mock new module API."""
    return mocker.patch(
        'akshare.new_api_function',
        return_value=get_mock_new_module_data()
    )
```

3. Import in `tests/fixtures/__init__.py` if needed

4. Write tests using the new fixture

## Best Practices

1. **Match Real Data Structure**: Mock data should match the exact structure (column names, data types) returned by real APIs

2. **Test Data Transformation**: Verify that Chinese column names are correctly mapped to English standardized names

3. **Test Edge Cases**: Include tests for empty responses, errors, and boundary conditions

4. **Keep Mocks Simple**: Use minimal but representative data (3-5 rows usually sufficient)

5. **Update Mocks**: When real API format changes, update corresponding mock data

6. **Separate Tests**: Keep mocked tests separate from integration tests that require network

## Integration vs Mock Tests

- **Integration Tests**: Use `@pytest.mark.integration` and require `--run-integration` flag
- **Mock Tests**: Run by default, no flags needed, no network required

Example test file structure:

```python
# test_module.py

# Mock tests (run by default)
class TestModuleWithMocks:
    def test_basic_mock(self, mock_api):
        ...

# Integration tests (require --run-integration)
@pytest.mark.integration
class TestModuleIntegration:
    def test_real_api(self):
        ...
```

## Running Tests

```bash
# Run all mock tests (default)
pytest tests/

# Run integration tests (requires network)
pytest tests/ --run-integration

# Run specific mock test file
pytest tests/test_northbound_with_mocks.py -v

# Run without network (verify offline capability)
# First disable network, then run tests
pytest tests/test_northbound_with_mocks.py -v
```

## Example Test Files

- `tests/test_northbound_with_mocks.py`: Complete northbound module mock tests
- `tests/test_blockdeal_with_mocks.py`: Block deal mock tests
- `tests/test_fundflow_with_mocks.py`: Fund flow mock tests

## Troubleshooting

### Mock Not Working

Ensure the mock path matches exactly where akshare is imported:

```python
# If akshare is imported as:
import akshare as ak

# Mock should be:
mocker.patch('akshare.stock_hsgt_hist_em')

# Not:
mocker.patch('ak.stock_hsgt_hist_em')  # Won't work
```

### AttributeError on Mock

Check that the mock fixture is properly injected:

```python
def test_example(mock_northbound_flow_api):  # Fixture as parameter
    mock_northbound_flow_api.assert_called()  # Use it
```

### Data Format Mismatch

If mock data doesn't match real data format:

1. Run real API to see actual structure: `akshare.stock_hsgt_hist_em()`
2. Update mock data to match exact column names and types
3. Ensure conversion logic handles both real and mock data

## Dependencies

Mock testing requires:

- `pytest-mock>=3.14.0`: For mocker fixture
- `responses>=0.25.0`: For HTTP mocking (if needed)

These are already included in `pyproject.toml` dev dependencies.

## Contributing

When adding new modules:

1. Create corresponding mock fixtures
2. Write mock-based tests alongside integration tests
3. Update this README if adding new patterns

## See Also

- `tests/conftest.py`: Shared pytest configuration
- `tests/utils/integration_helpers.py`: Helpers for integration tests
- `tests/golden_samples/`: Golden sample data for contract tests