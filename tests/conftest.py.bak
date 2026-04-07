"""
Pytest configuration and shared fixtures for akshare-one tests.

This file is automatically loaded by pytest and provides:
- Command line options
- Shared fixtures
- Test configuration
- Retry mechanisms for flaky tests
- Error handling improvements
"""

import logging
import time
import pytest
from functools import wraps
from typing import Callable


# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_logger')


# Register command line options
def pytest_addoption(parser):
    """Add custom pytest command line options."""
    # Add golden sample update option
    parser.addoption(
        "--update-golden-samples",
        action="store_true",
        default=False,
        help="Update golden samples instead of validating against them"
    )
    
    # Add integration test options
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires network access)"
    )

    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests"
    )

    parser.addoption(
        "--run-performance",
        action="store_true",
        default=False,
        help="Run performance tests"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires network)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "contract: mark test as contract test (golden sample)"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "flaky: mark test as flaky (inherently unstable, needs special handling)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    # Skip integration tests unless --run-integration is specified
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

    # Skip slow tests unless --run-slow is specified
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

    # Skip performance tests unless --run-performance or --run-integration is specified
    if not (config.getoption("--run-performance") or config.getoption("--run-integration")):
        skip_performance = pytest.mark.skip(reason="need --run-performance or --run-integration option to run")
        for item in items:
            if "performance" in item.keywords:
                item.add_marker(skip_performance)


# Shared fixtures
@pytest.fixture
def rate_limiter():
    """Fixture providing rate limiter for integration tests."""
    from tests.utils.integration_helpers import integration_rate_limiter
    return integration_rate_limiter


@pytest.fixture
def df_validator():
    """Fixture providing DataFrame validator."""
    from tests.utils.integration_helpers import DataFrameValidator
    return DataFrameValidator()


@pytest.fixture
def mock_data_generator():
    """Fixture providing mock data generator."""
    from tests.utils.integration_helpers import MockDataGenerator
    return MockDataGenerator()


@pytest.fixture
def sample_symbols():
    """Fixture providing sample stock symbols for testing."""
    return ['600000', '000001', '300001']


@pytest.fixture
def sample_date_range():
    """Fixture providing sample date range for testing."""
    return {
        'start_date': '2024-01-01',
        'end_date': '2024-01-31'
    }


@pytest.fixture
def test_logger():
    """Fixture providing test logger."""
    return logger


# ============================================================================
# Retry Mechanism for Flaky Tests
# ============================================================================


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 2.0,
    exceptions: tuple = (Exception,),
    condition: Callable[[Exception], bool] = None
):
    """
    Decorator to retry a test function on specific failures.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay in seconds between retries
        exceptions: Tuple of exception types to retry on
        condition: Optional function to check if retry should happen

    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            last_exception = None

            while retry_count < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Check if this exception should trigger a retry
                    should_retry = condition is None or condition(e)

                    if should_retry and retry_count < max_retries - 1:
                        retry_count += 1
                        logger.warning(
                            f"Test {func.__name__} failed (attempt {retry_count}/{max_retries}): {str(e)}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                    else:
                        # Final attempt failed or condition not met
                        logger.error(
                            f"Test {func.__name__} failed after {retry_count + 1} attempts: {str(e)}"
                        )
                        raise

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


@pytest.fixture
def retry_helper():
    """Fixture providing retry helper for tests."""
    return retry_on_failure


# ============================================================================
# Enhanced Test Hooks
# ============================================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results and log failures.
    This helps diagnose flaky tests by providing detailed failure logs.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Log test failure with details
        logger.error(
            f"Test failed: {item.nodeid}\n"
            f"Duration: {call.duration:.2f}s\n"
            f"Exception: {call.excinfo}\n"
        )

        # Check if this is a flaky test marker
        if "flaky" in item.keywords:
            logger.warning(
                f"Flaky test detected: {item.nodeid}. "
                f"Consider increasing retry count or improving test isolation."
            )


def pytest_runtest_setup(item):
    """
    Setup hook called before each test.
    Logs test start and checks for special markers.
    """
    logger.info(f"Starting test: {item.nodeid}")

    # Add extra delay for integration tests to avoid rate limiting
    if "integration" in item.keywords:
        time.sleep(0.5)  # Small delay to avoid API rate limits


def pytest_runtest_teardown(item, nextitem):
    """
    Teardown hook called after each test.
    Logs test completion and cleans up resources.
    """
    logger.info(f"Completed test: {item.nodeid}")


# Import mock API fixtures from fixtures module
# These fixtures allow tests to run without network access
pytest_plugins = ["tests.fixtures.mock_api_responses"]
