"""
Pytest configuration and shared fixtures for akshare-one tests.

This file is automatically loaded by pytest and provides:
- Command line options
- Shared fixtures
- Test configuration
"""

import pytest


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
