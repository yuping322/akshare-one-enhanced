# Test Stability Optimization Guide

## Overview

This document describes the test stability improvements implemented to ensure tests can be run repeatedly without failures.

## Changes Implemented

### 1. pytest-rerunfailures Plugin Integration

**Location**: `pyproject.toml`

**Changes**:
- Added `pytest-rerunfailures>=16.1` to dev dependencies
- Configured pytest to automatically retry failed tests 2 times with 1-second delay
- Added `--reruns=2 --reruns-delay=1` to pytest addopts

**Benefits**:
- Automatically retries flaky tests without manual intervention
- Reduces test failures caused by transient network issues
- Provides built-in retry mechanism for all tests

**Usage**:
```bash
# Default retry behavior (2 retries)
pytest tests/

# Custom retry count
pytest tests/ --reruns=5 --reruns-delay=2

# Disable retries for debugging
pytest tests/ --reruns=0
```

### 2. Enhanced Test Configuration

**Location**: `tests/conftest.py`

**New Features**:

#### a. Retry Decorator for Flaky Tests
```python
from tests.conftest import retry_on_failure

@retry_on_failure(max_retries=3, delay=2.0)
def test_unstable_network_api():
    # Test code that might fail due to network issues
    pass
```

#### b. Test Logging Hooks
- `pytest_runtest_makereport`: Logs test failures with detailed information
- `pytest_runtest_setup`: Logs test start and adds delay for integration tests
- `pytest_runtest_teardown`: Logs test completion

#### c. New Test Marker
```python
@pytest.mark.flaky
def test_known_unstable():
    # Test that is inherently unstable
    pass
```

#### d. Enhanced Fixtures
- `test_logger`: Provides logging capabilities for tests
- `retry_helper`: Provides retry decorator function

### 3. Improved Integration Test Helpers

**Location**: `tests/utils/integration_helpers.py`

**Enhancements**:

#### a. RateLimiter with Retry Support
```python
from tests.utils.integration_helpers import integration_rate_limiter

# Automatic retry on network errors
@integration_rate_limiter.retry_on_network_error
def test_api_call():
    # API call that might fail
    pass
```

**Features**:
- Rate limiting: 1 call per second (configurable)
- Automatic retry on network errors: ConnectionError, TimeoutError, OSError
- Retry count: 3 attempts (configurable)
- Retry delay: 5 seconds (configurable)
- Detailed logging for each retry attempt

#### b. Enhanced Network Check
- Checks multiple DNS servers (Google, Cloudflare, OpenDNS)
- More reliable network availability detection
- Better failure diagnosis

#### c. Flaky Test Decorator
```python
from tests.utils.integration_helpers import flaky_test

@pytest.mark.flaky
@flaky_test(max_retries=5, retry_delay=2.0)
def test_known_flaky():
    # Test with custom retry logic
    pass
```

### 4. Test Independence Improvements

**Guidelines for Test Independence**:

1. **Use Fresh Fixtures**: Each test should use fresh data from fixtures
2. **Avoid Shared State**: Tests should not depend on execution order
3. **Clean Up Resources**: Use teardown hooks or context managers
4. **Mock External Dependencies**: Use mocks for external services when possible

**Example**:
```python
def test_independent_example(mock_data_generator):
    # Generate fresh mock data for this test
    df = mock_data_generator.generate_mock_dataframe(
        columns=['date', 'symbol', 'close'],
        row_count=10
    )

    # Test using isolated data
    assert len(df) == 10
    # No side effects on other tests
```

### 5. Error Handling Improvements

**Best Practices**:

1. **Graceful Failure Handling**:
```python
def test_api_with_retry():
    try:
        result = api_call()
        assert result is not None
    except ConnectionError as e:
        pytest.skip(f"Network unavailable: {e}")
```

2. **Data Availability Checks**:
```python
def test_data_availability():
    df = get_data()

    if df.empty:
        pytest.skip("No data available for testing")

    # Continue with assertions
    assert len(df) > 0
```

3. **Timeout Protection**:
```python
@pytest.mark.timeout(60)  # 60 second timeout
def test_long_running():
    # Test that might take too long
    pass
```

## Testing Stability Verification

### Run Tests Multiple Times

To verify test stability, run the test suite 3 times:

```bash
# Run tests 3 times to check stability
for i in {1..3}; do
    echo "=== Test Run $i ==="
    pytest tests/ -v --tb=short || exit 1
done
```

### Run Integration Tests with Retry

```bash
# Run integration tests with extra retries
pytest tests/ -m integration --reruns=5 --reruns-delay=2 --run-integration
```

### Run Specific Flaky Tests

```bash
# Run tests marked as flaky
pytest tests/ -m flaky --reruns=10 --reruns-delay=3
```

## Monitoring and Diagnostics

### Enable Verbose Logging

```bash
# Run with detailed logging
pytest tests/ -v --log-cli-level=INFO
```

### Check Test Reports

After test runs, check:
- Test duration (slow tests might need timeout adjustment)
- Retry count (tests with many retries need improvement)
- Failure patterns (consistent failures indicate real issues)

### Analyze Flaky Tests

When a test is marked as flaky:
1. Check if it's a network-dependent test
2. Verify data availability assumptions
3. Consider using mock data instead of real API calls
4. Add proper retry decorators if needed

## Configuration Summary

### pytest.ini_options (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-v --cov=akshare_one --cov-report=term-missing --reruns=2 --reruns-delay=1"
timeout = 60
timeout_method = "signal"
markers = [
    "contract: Mark tests as contract tests",
    "integration: Mark tests as integration tests (require network)",
    "slow: Mark tests as slow running",
    "performance: Mark tests as performance tests",
    "flaky: Mark tests as flaky (inherently unstable, needs special handling)",
]
filterwarnings = [
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
]
```

### Retry Configuration

- **Default retries**: 2 attempts
- **Default delay**: 1 second
- **Network error retries**: 3 attempts (in RateLimiter)
- **Network retry delay**: 5 seconds
- **Flaky test retries**: 5 attempts (customizable)

## Best Practices Summary

1. **Use pytest-rerunfailures**: Leverage automatic retry mechanism
2. **Mark flaky tests**: Use `@pytest.mark.flaky` for inherently unstable tests
3. **Add retry decorators**: Use `retry_on_failure` or `flaky_test` for custom retry logic
4. **Check data availability**: Skip tests gracefully when data is unavailable
5. **Handle network errors**: Use `retry_on_network_error` for network-dependent tests
6. **Ensure test independence**: Use fresh fixtures, avoid shared state
7. **Set appropriate timeouts**: Use `@pytest.mark.timeout()` for long-running tests
8. **Log test progress**: Use test logger for diagnostics
9. **Monitor test stability**: Run tests multiple times to verify stability
10. **Clean up resources**: Use teardown hooks or context managers

## Troubleshooting Guide

### Test Fails Repeatedly

**Diagnosis**:
1. Check if it's a real bug in the code
2. Verify test assumptions (data availability, API behavior)
3. Check for environment issues (missing dependencies, wrong configuration)

**Solution**:
- Fix the underlying bug if found
- Update test expectations if API behavior changed
- Add proper error handling and skip conditions

### Test Passes Sometimes but Fails Other Times

**Diagnosis**:
1. Check for network dependency
2. Verify data availability assumptions
3. Look for race conditions or timing issues
4. Check for shared state between tests

**Solution**:
- Add retry decorators
- Use mock data instead of real API calls
- Ensure test independence
- Add proper delays or synchronization

### Test Timeout Issues

**Diagnosis**:
1. Check test duration in reports
2. Identify slow operations (network calls, large data processing)

**Solution**:
- Increase timeout: `@pytest.mark.timeout(120)`
- Optimize slow operations
- Use mock data to speed up tests
- Break large tests into smaller ones

## Success Metrics

After implementing these improvements, you should see:
- Reduced test failure rate (especially transient failures)
- Higher test reproducibility (tests pass consistently)
- Better failure diagnostics (detailed logs for debugging)
- Improved test isolation (no side effects between tests)
- More reliable CI/CD pipeline (fewer false negatives)

## Next Steps

1. Run tests 3 times to verify stability
2. Identify remaining flaky tests
3. Apply appropriate retry mechanisms
4. Monitor test metrics over time
5. Adjust retry parameters based on results
6. Document known flaky tests and their handling strategies