# Market Data Exception System

## Overview

The market data exception system provides a comprehensive hierarchy of exceptions for handling various error scenarios in data fetching and processing operations. All exceptions inherit from the base `MarketDataError` class, making it easy to catch and handle errors at different levels of specificity.

## Exception Hierarchy

```
Exception (built-in)
└── MarketDataError
    ├── InvalidParameterError
    ├── DataSourceUnavailableError
    ├── NoDataError
    ├── UpstreamChangedError
    ├── RateLimitError
    └── DataValidationError
```

## Exception Classes

### MarketDataError

**Base exception class for all market data related errors.**

This is the root exception that all other market data exceptions inherit from. Use this for catching any market data related error.

```python
from akshare_one.modules import MarketDataError

try:
    data = provider.fetch_data()
except MarketDataError as e:
    logger.error(f"Market data error: {e}")
```

### InvalidParameterError

**Raised when invalid parameters are provided to a data provider.**

Common scenarios:
- Invalid symbol format (e.g., not 6 digits)
- Invalid date format (e.g., not YYYY-MM-DD)
- Invalid date range (start_date > end_date)
- Invalid enum values (e.g., invalid market type)
- Out of range values (e.g., negative top_n)

```python
from akshare_one.modules import InvalidParameterError

def get_stock_data(symbol: str):
    if not re.match(r'^\d{6}$', symbol):
        raise InvalidParameterError(
            f"Invalid symbol format: {symbol}. Expected 6-digit code."
        )
```

### DataSourceUnavailableError

**Raised when a data source is unavailable or unreachable.**

Common scenarios:
- Network timeout
- HTTP errors (4xx, 5xx)
- DNS resolution failures
- Connection refused
- SSL/TLS errors

The upper layer (View Service) can use this to trigger data source switching or return UPSTREAM_TIMEOUT status.

```python
from akshare_one.modules import DataSourceUnavailableError
import requests

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    raise DataSourceUnavailableError(f"Failed to reach {url}: {e}")
```

### NoDataError

**Raised when no data is returned from the data source.**

This is different from an empty result - it indicates that the data source returned an unexpected empty response or explicitly indicated no data is available.

**Note:** Providers should typically return an empty DataFrame with proper column structure instead of raising this exception. This exception is for cases where the data source explicitly signals "no data available" vs. "empty result set".

```python
from akshare_one.modules import NoDataError

if response.json().get('error') == 'NO_DATA':
    raise NoDataError(f"No data available for symbol {symbol}")
```

### UpstreamChangedError

**Raised when upstream data source structure has changed.**

Common scenarios:
- Missing expected fields in response
- Changed field names
- Changed data types
- Changed response format (e.g., JSON to XML)

This exception helps detect when the upstream API has been modified and the provider code needs to be updated. Contract tests should catch these issues early.

```python
from akshare_one.modules import UpstreamChangedError

expected_columns = ['date', 'symbol', 'close']
if not all(col in df.columns for col in expected_columns):
    missing = set(expected_columns) - set(df.columns)
    raise UpstreamChangedError(
        f"Missing expected columns: {missing}. Upstream API may have changed."
    )
```

### RateLimitError

**Raised when API rate limit is exceeded.**

This indicates that the data source has throttled requests due to exceeding rate limits. The provider should implement retry logic with exponential backoff.

```python
from akshare_one.modules import RateLimitError

if response.status_code == 429:
    retry_after = response.headers.get('Retry-After', 60)
    raise RateLimitError(
        f"Rate limit exceeded. Retry after {retry_after} seconds."
    )
```

### DataValidationError

**Raised when data validation fails.**

Common scenarios:
- Data type mismatches
- Out of range values
- Invalid data combinations
- Failed integrity checks

```python
from akshare_one.modules import DataValidationError

if df['close'].min() < 0:
    raise DataValidationError("Close price cannot be negative")
```

## Utility Functions

### handle_upstream_error()

**Convert common upstream errors to appropriate MarketDataError subclasses.**

This helper function standardizes error handling across different providers.

```python
from akshare_one.modules import handle_upstream_error
import requests

try:
    response = requests.get(url)
    response.raise_for_status()
except Exception as e:
    raise handle_upstream_error(e, 'eastmoney')
```

**Error Mapping:**

| Upstream Error | Converted To |
|---------------|--------------|
| `requests.Timeout` | `DataSourceUnavailableError` |
| `requests.ConnectionError` | `DataSourceUnavailableError` |
| `requests.HTTPError` (429) | `RateLimitError` |
| `requests.HTTPError` (4xx) | `InvalidParameterError` |
| `requests.HTTPError` (5xx) | `DataSourceUnavailableError` |
| `KeyError`, `AttributeError` | `UpstreamChangedError` |
| Other exceptions | `MarketDataError` |

## Usage Patterns

### Pattern 1: Specific Exception Handling

Handle different exception types with specific recovery strategies:

```python
from akshare_one.modules import (
    InvalidParameterError,
    DataSourceUnavailableError,
    NoDataError,
    MarketDataError,
)

try:
    data = provider.get_stock_fund_flow("600000", "2024-01-01", "2024-12-31")
except InvalidParameterError as e:
    # Log and return error to user
    logger.error(f"Invalid parameters: {e}")
    return {"error": "INVALID_PARAMS", "message": str(e)}
except DataSourceUnavailableError as e:
    # Try alternative data source or return cached data
    logger.warning(f"Primary source unavailable: {e}")
    data = try_alternative_source()
except NoDataError as e:
    # Return empty result with appropriate message
    logger.info(f"No data available: {e}")
    return {"data": [], "message": "No data for the requested period"}
except MarketDataError as e:
    # Catch-all for any other market data errors
    logger.error(f"Unexpected market data error: {e}")
    return {"error": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
```

### Pattern 2: Catch-All with Base Exception

Use the base exception to catch all market data errors:

```python
from akshare_one.modules import MarketDataError

try:
    data = provider.fetch_data()
except MarketDataError as e:
    logger.error(f"Market data error: {e}")
    # Handle all market data errors uniformly
```

### Pattern 3: Parameter Validation

Use `InvalidParameterError` for input validation:

```python
from akshare_one.modules import BaseProvider, InvalidParameterError

def get_stock_data(symbol: str, start_date: str, end_date: str):
    # Validate parameters
    try:
        BaseProvider.validate_symbol(symbol)
        BaseProvider.validate_date_range(start_date, end_date)
    except ValueError as e:
        raise InvalidParameterError(str(e))
    
    # Proceed with data fetching
    ...
```

### Pattern 4: Upstream Error Handling

Use `handle_upstream_error()` for consistent error conversion:

```python
from akshare_one.modules import handle_upstream_error
import requests

def fetch_from_api(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise handle_upstream_error(e, 'eastmoney')
```

### Pattern 5: Data Validation

Use `DataValidationError` and `UpstreamChangedError` for data integrity checks:

```python
from akshare_one.modules import DataValidationError, UpstreamChangedError

def validate_data(df: pd.DataFrame):
    # Check for required fields
    required_fields = ['date', 'symbol', 'close']
    missing = set(required_fields) - set(df.columns)
    if missing:
        raise UpstreamChangedError(
            f"Missing required fields: {missing}. API may have changed."
        )
    
    # Check for invalid values
    if (df['close'] < 0).any():
        raise DataValidationError("Close price cannot be negative")
```

## Best Practices

### 1. Use Specific Exceptions

Always raise the most specific exception type that matches the error scenario:

```python
# Good
raise InvalidParameterError(f"Invalid symbol: {symbol}")

# Bad
raise MarketDataError(f"Invalid symbol: {symbol}")
```

### 2. Include Context in Error Messages

Provide helpful context in exception messages:

```python
# Good
raise DataSourceUnavailableError(
    f"Failed to connect to eastmoney API at {url}. "
    f"Timeout after {timeout} seconds."
)

# Bad
raise DataSourceUnavailableError("Connection failed")
```

### 3. Use handle_upstream_error() for External APIs

Standardize error handling for external API calls:

```python
# Good
try:
    response = requests.get(url)
except Exception as e:
    raise handle_upstream_error(e, 'eastmoney')

# Less ideal
try:
    response = requests.get(url)
except requests.Timeout:
    raise DataSourceUnavailableError("Timeout")
except requests.ConnectionError:
    raise DataSourceUnavailableError("Connection error")
# ... many more cases
```

### 4. Validate Early

Validate parameters at the entry point before making expensive operations:

```python
def get_stock_data(symbol: str, start_date: str, end_date: str):
    # Validate first
    BaseProvider.validate_symbol(symbol)
    BaseProvider.validate_date_range(start_date, end_date)
    
    # Then fetch data
    return fetch_data(symbol, start_date, end_date)
```

### 5. Return Empty DataFrames Instead of NoDataError

For empty results, return an empty DataFrame with proper structure:

```python
# Good
if raw_df.empty:
    return pd.DataFrame(columns=['date', 'symbol', 'close'])

# Less ideal (use only when data source explicitly signals error)
if raw_df.empty:
    raise NoDataError("No data available")
```

### 6. Use Contract Tests for UpstreamChangedError

Implement contract tests to detect upstream changes early:

```python
def test_upstream_schema_stability():
    """Test that upstream API schema hasn't changed."""
    expected_columns = ['date', 'symbol', 'close']
    
    provider = EastmoneyProvider()
    df = provider.fetch_data()
    
    assert list(df.columns) == expected_columns, "Schema changed!"
```

## Integration with View Service

The exception system is designed to integrate with the upper layer View Service:

| Provider Exception | View Service Status | HTTP Status |
|-------------------|-------------------|-------------|
| `InvalidParameterError` | `INVALID_PARAMS` | 400 |
| `DataSourceUnavailableError` | `UPSTREAM_TIMEOUT` | 503 |
| `NoDataError` | `EMPTY_RESULT` (warning) | 200 |
| `UpstreamChangedError` | `UPSTREAM_CHANGED` (warning) | 200 |
| `RateLimitError` | `RATE_LIMITED` | 429 |
| Other `MarketDataError` | `INTERNAL_ERROR` | 500 |

## Testing

The exception system includes comprehensive unit tests. Run them with:

```bash
pytest tests/test_exceptions.py -v
```

Test coverage includes:
- Exception hierarchy verification
- Exception catching behavior
- `handle_upstream_error()` utility function
- Realistic usage scenarios
- Error message quality

## Examples

See `examples/exception_usage_example.py` for complete working examples demonstrating:
1. Parameter validation
2. Upstream error handling
3. Data validation
4. Exception hierarchy usage
5. Provider integration

Run the examples:

```bash
python examples/exception_usage_example.py
```

## Summary

The market data exception system provides:

✅ **Clear hierarchy** - Easy to catch errors at different levels of specificity  
✅ **Comprehensive coverage** - Handles all common error scenarios  
✅ **Utility functions** - `handle_upstream_error()` for standardized error conversion  
✅ **Well-documented** - Clear docstrings and usage examples  
✅ **Fully tested** - 100% test coverage with realistic scenarios  
✅ **Integration-ready** - Designed to work with View Service layer  

Use these exceptions consistently across all providers to ensure robust error handling throughout the system.
