"""
Network error handling utilities for tests.

This module provides utilities to handle network errors gracefully in tests.
"""

import os
import pytest
import logging
import traceback
from functools import wraps

# Configure logging to suppress network warnings during tests
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)


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
]


def is_network_error(error_message: str) -> bool:
    """Check if an error message indicates a network problem."""
    return any(pattern in error_message for pattern in NETWORK_ERROR_PATTERNS)


def should_skip_on_network_error() -> bool:
    """Determine if tests should skip on network errors based on environment."""
    return os.getenv("OFFLINE_TEST", "false").lower() in ("true", "1", "yes")


def network_safe_test(test_func):
    """
    Decorator to make tests safe from network errors.

    If a network error occurs and OFFLINE_TEST is enabled or pytest --offline flag is set,
    the test will be skipped instead of failing.

    Usage:
        @network_safe_test
        def test_api_call():
            df = get_stock_valuation("600000")
            assert not df.empty
    """
    @wraps(test_func)
    def wrapper(*args, **kwargs):
        try:
            return test_func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            error_traceback = traceback.format_exc()

            # Check if this is a network error
            if is_network_error(error_message) or is_network_error(error_traceback):
                if should_skip_on_network_error():
                    pytest.skip(f"Skipped due to network error: {error_message}")
                else:
                    # Re-raise if not in offline mode
                    raise
            else:
                # Re-raise non-network errors
                raise

    return wrapper


def skip_if_offline(reason="Test requires network access"):
    """
    Decorator to skip test if offline mode is enabled.

    Usage:
        @skip_if_offline("Requires real API access")
        def test_real_api():
            ...
    """
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            if should_skip_on_network_error():
                pytest.skip(reason)
            return test_func(*args, **kwargs)
        return wrapper
    return decorator