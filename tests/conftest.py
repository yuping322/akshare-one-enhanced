"""
Pytest configuration and shared fixtures for akshare-one tests.

This file is automatically loaded by pytest and provides:
- Command line options
- Shared fixtures
- Test configuration
- Network error handling for offline testing
- Auto-detection and graceful handling of network-dependent tests
- Retry mechanisms for flaky tests
"""

import os
import sys
import time
import pytest
import logging
import traceback
from typing import Any, Callable
from functools import wraps

# Configure logging to suppress network warnings during tests
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("http.client").setLevel(logging.ERROR)

# Configure test logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_logger')


# Network error patterns to detect
NETWORK_ERROR_PATTERNS = [
    "ConnectionError",
    "TimeoutError",
    "HTTPConnectionPool",
    "Max retries exceeded",
    "Failed to establish connection",
    "Network is unreachable",
    "Connection refused",
    "SSLError",
    "ProxyError",
    "socket.timeout",
    "NewConnectionError",
    "ConnectTimeoutError",
]


def is_network_error(error_message: str) -> bool:
    """Check if an error message indicates a network problem."""
    return any(pattern.lower() in error_message.lower() for pattern in NETWORK_ERROR_PATTERNS)


def should_skip_on_network_error() -> bool:
    """Determine if tests should skip on network errors based on environment."""
    return os.getenv("OFFLINE_TEST", "false").lower() in ("true", "1", "yes")


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

    parser.addoption(
        "--offline",
        action="store_true",
        default=should_skip_on_network_error(),
        help="Run tests in offline mode (gracefully handle network errors)"
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
        "markers", "network: mark test as requiring network access"
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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to handle network errors during test execution.

    This allows tests that encounter network errors in offline mode
    to be skipped instead of failed, making the test suite more resilient.
    """
    outcome = yield
    report = outcome.get_result()

    # Only process failed tests during call phase
    if report.when == "call" and report.failed:
        if call.excinfo:
            error_message = str(call.excinfo.value)
            error_traceback = "".join(traceback.format_exception(
                type(call.excinfo.value),
                call.excinfo.value,
                call.excinfo.tb
            ))

            # Check if this is a network error
            if is_network_error(error_message) or is_network_error(error_traceback):
                # In offline mode or if test doesn't explicitly require integration,
                # skip the test instead of failing
                offline_mode = item.config.getoption("--offline") or should_skip_on_network_error()

                # Always skip network errors in offline mode
                if offline_mode:
                    report.outcome = 'skipped'
                    report.wasxfail = f"Skipped due to network error (offline mode): {error_message[:100]}"
                # For tests not marked as integration, provide helpful message
                elif "integration" not in item.keywords:
                    # Log the issue but don't change outcome
                    logging.warning(
                        f"Test {item.nodeid} encountered network error but is not marked as @pytest.mark.integration. "
                        f"Consider adding the marker or using mock data. Error: {error_message[:100]}"
                    )


# Shared fixtures
@pytest.fixture
def rate_limiter():
    """Fixture providing rate limiter for integration tests."""
    try:
        from tests.utils.integration_helpers import integration_rate_limiter
        return integration_rate_limiter
    except ImportError:
        return None


@pytest.fixture
def df_validator():
    """Fixture providing DataFrame validator."""
    try:
        from tests.utils.integration_helpers import DataFrameValidator
        return DataFrameValidator()
    except ImportError:
        return None


@pytest.fixture
def mock_data_generator():
    """Fixture providing mock data generator."""
    try:
        from tests.utils.integration_helpers import MockDataGenerator
        return MockDataGenerator()
    except ImportError:
        return None


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
def offline_mode(request):
    """Fixture to check if offline mode is enabled."""
    return request.config.getoption("--offline") or should_skip_on_network_error()


@pytest.fixture
def mock_network_safe(request):
    """
    Fixture that provides network-safe test context.

    Usage:
        def test_api_call(mock_network_safe):
            if mock_network_safe:
                pytest.skip("Test requires network access")
            # ... rest of test
    """
    return should_skip_on_network_error() or request.config.getoption("--offline")


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

    Usage:
        @retry_on_failure(max_retries=3, delay=2.0)
        def test_flaky_api():
            ...
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
# Additional Test Hooks
# ============================================================================


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
try:
    pytest_plugins = ["tests.fixtures.mock_api_responses"]
except ImportError:
    # Mock fixtures not available, tests will need real network
    pass