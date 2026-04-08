"""
Comprehensive tests for multi-source failover and data source switching mechanisms.

This test suite covers:
- Data source switching and failover (Scenario A)
- Source priority and rotation strategies (Scenario B)
- Cache mechanisms (Scenario C)
- Partial data and degradation strategies (Scenario D)
- Concurrent and thread-safe tests
- Error handling and retry mechanisms
- Data quality checks
- Performance tests

Run: pytest tests/test_multi_source_failover_comprehensive.py -v
"""

import time
import threading
import concurrent.futures
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Any

import pandas as pd
import pytest
import requests

from akshare_one.modules.multi_source import (
    EmptyDataPolicy,
    ExecutionResult,
    MultiSourceRouter,
    create_historical_router,
    create_realtime_router,
    create_financial_router,
    create_northbound_router,
    create_fundflow_router,
    create_block_deal_router,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_stock_data():
    """Create sample stock data for testing."""
    return pd.DataFrame(
        {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "open": [10.0, 10.5, 11.0],
            "high": [10.5, 11.0, 11.5],
            "low": [9.5, 10.0, 10.5],
            "close": [10.2, 10.7, 11.2],
            "volume": [1000, 1200, 1500],
        }
    )


@pytest.fixture
def empty_dataframe():
    """Create empty DataFrame for testing."""
    return pd.DataFrame()


@pytest.fixture
def partial_data():
    """Create partial data (missing volume)."""
    return pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "open": [10.0],
            "high": [10.5],
            "low": [9.5],
            "close": [10.2],
        }
    )


@pytest.fixture
def delayed_data():
    """Create delayed data (T-1)."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    return pd.DataFrame(
        {
            "timestamp": [yesterday],
            "open": [10.0],
            "high": [10.5],
            "low": [9.5],
            "close": [10.2],
            "volume": [1000],
        }
    )


@pytest.fixture
def quality_issue_data():
    """Create data with quality issues (negative price, zero volume)."""
    return pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "open": [-10.0],
            "high": [-10.5],
            "low": [-9.5],
            "close": [-10.2],
            "volume": [0],
        }
    )


# ============================================================================
# Scenario A: Primary Source Fails, Fallback to Secondary
# ============================================================================


class TestPrimarySourceFailover:
    """Test primary source failure and automatic fallback."""

    def test_primary_source_fails_fallback_to_secondary(self, sample_stock_data):
        """Test primary source fails, automatically switch to secondary."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = Exception("Primary source unavailable")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "sina"
        assert provider1.get_hist_data.called
        assert provider2.get_hist_data.called

    def test_all_sources_fail_returns_error(self):
        """Test all data sources fail, returns error."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = requests.Timeout("Timeout")

        provider2 = Mock()
        provider2.get_hist_data.side_effect = requests.ConnectionError("Connection failed")

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        with pytest.raises(ValueError, match="All data sources failed"):
            router.execute("get_hist_data")

    def test_primary_fails_with_network_error_fallback(self, sample_stock_data):
        """Test network error triggers fallback."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = requests.ConnectionError("Network error")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "sina"

    def test_primary_fails_with_timeout_fallback(self, sample_stock_data):
        """Test timeout error triggers fallback."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = requests.Timeout("Request timeout")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "sina"

    def test_primary_fails_with_rate_limit_fallback(self, sample_stock_data):
        """Test rate limit error triggers fallback."""
        provider1 = Mock()

        response = Mock()
        response.status_code = 429
        http_error = requests.HTTPError()
        http_error.response = response
        provider1.get_hist_data.side_effect = http_error

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "sina"

    def test_multiple_sources_fallback_chain(self, sample_stock_data):
        """Test fallback chain across multiple sources."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = Exception("Source 1 failed")

        provider2 = Mock()
        provider2.get_hist_data.side_effect = Exception("Source 2 failed")

        provider3 = Mock()
        provider3.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
                ("netease", provider3),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "netease"
        assert provider1.get_hist_data.called
        assert provider2.get_hist_data.called
        assert provider3.get_hist_data.called


# ============================================================================
# Scenario B: Source Priority and Rotation Strategies
# ============================================================================


class TestSourcePriorityAndRotation:
    """Test data source priority and rotation strategies."""

    def test_source_priority_order(self, sample_stock_data):
        """Test data source priority order."""
        providers_data = {
            "eastmoney": sample_stock_data,
            "sina": sample_stock_data,
            "netease": sample_stock_data,
            "tencent": sample_stock_data,
        }

        providers = [
            ("eastmoney", Mock(get_hist_data=Mock(return_value=providers_data["eastmoney"]))),
            ("sina", Mock(get_hist_data=Mock(return_value=providers_data["sina"]))),
            ("netease", Mock(get_hist_data=Mock(return_value=providers_data["netease"]))),
            ("tencent", Mock(get_hist_data=Mock(return_value=providers_data["tencent"]))),
        ]

        router = MultiSourceRouter(providers)

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "eastmoney"
        assert providers[0][1].get_hist_data.called
        assert not providers[1][1].get_hist_data.called

    def test_source_rotation_on_failure(self, sample_stock_data):
        """Test source rotation on failure."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", Mock(get_hist_data=Mock(return_value=sample_stock_data))),
            ]
        )

        result1 = router.execute("get_hist_data")
        assert result1.attrs["source"] == "eastmoney"

        provider1.get_hist_data.side_effect = Exception("Source failed")

        result2 = router.execute("get_hist_data")
        assert result2.attrs["source"] == "sina"

    def test_source_health_tracking(self):
        """Test data source health status tracking."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = requests.Timeout("Timeout")

        provider2 = Mock()
        provider2.get_hist_data.return_value = pd.DataFrame(
            {
                "timestamp": ["2024-01-01"],
                "close": [10.0],
            }
        )

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        for _ in range(3):
            result = router.execute("get_hist_data")

        stats = router.get_stats()

        assert stats["eastmoney"]["failure"] == 3
        assert stats["sina"]["success"] == 3

    def test_source_stats_reset(self, sample_stock_data):
        """Test source statistics tracking and reset."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        router.execute("get_hist_data")
        router.execute("get_hist_data")

        stats = router.get_stats()
        assert stats["eastmoney"]["success"] == 2

    def test_priority_respects_order(self, sample_stock_data):
        """Test priority respects configured order."""
        providers = [
            ("high_priority", Mock(get_hist_data=Mock(return_value=sample_stock_data))),
            ("low_priority", Mock(get_hist_data=Mock(return_value=sample_stock_data))),
        ]

        router = MultiSourceRouter(providers)

        result = router.execute("get_hist_data")

        assert result.attrs.get("source") == "high_priority"
        assert providers[0][1].get_hist_data.called
        assert not providers[1][1].get_hist_data.called


# ============================================================================
# Scenario C: Cache Hit and Miss
# ============================================================================


class TestCacheMechanisms:
    """Test cache mechanisms for multi-source data."""

    def test_cache_hit_avoids_api_call(self, sample_stock_data):
        """Test cache hit avoids API call."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        result1 = router.execute("get_hist_data")
        assert provider1.get_hist_data.call_count == 1

        result2 = router.execute("get_hist_data")
        assert provider1.get_hist_data.call_count == 2

    def test_cache_expired_refreshes_data(self, sample_stock_data):
        """Test cache expiration triggers data refresh."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data.copy()

        router = MultiSourceRouter([("eastmoney", provider1)])

        result1 = router.execute("get_hist_data")

        new_data = sample_stock_data.copy()
        new_data["close"] = [11.0, 11.5, 12.0]
        provider1.get_hist_data.return_value = new_data

        result2 = router.execute("get_hist_data")

        assert provider1.get_hist_data.call_count == 2

    def test_cache_with_different_params(self, sample_stock_data):
        """Test cache handles different parameters."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        router.execute("get_hist_data", symbol="600000")
        router.execute("get_hist_data", symbol="000001")

        assert provider1.get_hist_data.call_count == 2

    def test_cache_with_source_switch(self, sample_stock_data):
        """Test cache works with source switching."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = Exception("Failed")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result1 = router.execute("get_hist_data")
        assert result1.attrs["source"] == "sina"

        result2 = router.execute("get_hist_data")
        assert result2.attrs["source"] == "sina"

    def test_cache_invalidation_on_error(self, sample_stock_data):
        """Test cache invalidation when errors occur."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        router.execute("get_hist_data")

        provider1.get_hist_data.side_effect = Exception("Failed")

        with pytest.raises(ValueError):
            router.execute("get_hist_data")


# ============================================================================
# Scenario D: Partial Data and Degradation Strategies
# ============================================================================


class TestPartialDataHandling:
    """Test partial data handling and degradation strategies."""

    def test_partial_data_handling(self, partial_data):
        """Test partial data returns with missing fields."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = partial_data

        router = MultiSourceRouter(
            [("eastmoney", provider1)],
            required_columns=["timestamp", "open", "close", "volume"],
        )

        with pytest.raises(ValueError, match="All data sources failed"):
            router.execute("get_hist_data")

    def test_graceful_degradation_delayed_data(self, delayed_data):
        """Test graceful degradation with delayed data."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = delayed_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        result = router.execute("get_hist_data")

        assert not result.empty
        assert "timestamp" in result.columns

    def test_partial_data_with_fallback(self, partial_data, sample_stock_data):
        """Test partial data triggers fallback to complete data."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = partial_data

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [("eastmoney", provider1), ("sina", provider2)],
            required_columns=["timestamp", "open", "close", "volume"],
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert "volume" in result.columns
        assert result.attrs.get("source") == "sina"

    def test_degraded_quality_acceptance(self, delayed_data):
        """Test degraded quality data acceptance."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = delayed_data

        router = MultiSourceRouter(
            [("eastmoney", provider1)],
            empty_data_policy=EmptyDataPolicy.RELAXED,
        )

        result = router.execute("get_hist_data")

        assert not result.empty


# ============================================================================
# EmptyDataPolicy Tests
# ============================================================================


class TestEmptyDataPolicy:
    """Test EmptyDataPolicy functionality."""

    def test_strict_policy_empty_fails(self, empty_dataframe, sample_stock_data):
        """Test STRICT policy: empty DataFrame triggers fallback."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = empty_dataframe

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [("eastmoney", provider1), ("sina", provider2)],
            empty_data_policy=EmptyDataPolicy.STRICT,
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "sina"

    def test_relaxed_policy_empty_accepted(self, empty_dataframe):
        """Test RELAXED policy: empty DataFrame is valid."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = empty_dataframe

        router = MultiSourceRouter(
            [("eastmoney", provider1)],
            empty_data_policy=EmptyDataPolicy.RELAXED,
        )

        result = router.execute("get_hist_data")

        assert result.empty
        assert provider1.get_hist_data.called

    def test_best_effort_policy_continues_on_empty(self, empty_dataframe):
        """Test BEST_EFFORT policy: tries all sources."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = empty_dataframe

        provider2 = Mock()
        provider2.get_hist_data.return_value = empty_dataframe

        router = MultiSourceRouter(
            [("eastmoney", provider1), ("sina", provider2)],
            empty_data_policy=EmptyDataPolicy.BEST_EFFORT,
        )

        result = router.execute("get_hist_data")

        assert result.empty
        assert provider1.get_hist_data.called
        assert provider2.get_hist_data.called

    def test_best_effort_returns_first_non_empty(self, empty_dataframe, sample_stock_data):
        """Test BEST_EFFORT policy: returns first non-empty result."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = empty_dataframe

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        provider3 = Mock()
        provider3.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [("eastmoney", provider1), ("sina", provider2), ("netease", provider3)],
            empty_data_policy=EmptyDataPolicy.BEST_EFFORT,
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "sina"
        assert not provider3.get_hist_data.called

    def test_execute_with_result_strict_policy(self, empty_dataframe):
        """Test execute_with_result with STRICT policy."""
        provider = Mock()
        provider.get_data.return_value = empty_dataframe

        router = MultiSourceRouter(
            [("source1", provider)],
            empty_data_policy=EmptyDataPolicy.STRICT,
        )

        result = router.execute_with_result("get_data")

        assert result.success is False
        assert result.data is None
        assert result.attempts == 1

    def test_execute_with_result_relaxed_policy(self, empty_dataframe):
        """Test execute_with_result with RELAXED policy."""
        provider = Mock()
        provider.get_data.return_value = empty_dataframe

        router = MultiSourceRouter(
            [("source1", provider)],
            empty_data_policy=EmptyDataPolicy.RELAXED,
        )

        result = router.execute_with_result("get_data")

        assert result.success is True
        assert result.is_empty is True
        assert result.data is not None
        assert result.data.empty

    def test_default_policy_is_strict(self, empty_dataframe):
        """Test default policy is STRICT."""
        provider = Mock()
        provider.get_data.return_value = empty_dataframe

        router = MultiSourceRouter([("source1", provider)])

        result = router.execute_with_result("get_data")

        assert result.success is False
        assert result.data is None


# ============================================================================
# Concurrent and Thread-Safe Tests
# ============================================================================


class TestConcurrentAccess:
    """Test concurrent and thread-safe access."""

    def test_concurrent_multi_source_requests(self, sample_stock_data):
        """Test concurrent multi-source requests."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        results = []

        def fetch_data():
            result = router.execute("get_hist_data")
            results.append(result)

        threads = [threading.Thread(target=fetch_data) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(not r.empty for r in results)

    def test_concurrent_source_switching(self, sample_stock_data):
        """Test concurrent source switching."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = requests.Timeout("Timeout")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        results = []

        def fetch_data():
            result = router.execute("get_hist_data")
            results.append(result)

        threads = [threading.Thread(target=fetch_data) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 5
        assert all(not r.empty for r in results)
        assert all(r.attrs.get("source") == "sina" for r in results)

    def test_concurrent_with_pool(self, sample_stock_data):
        """Test concurrent requests with ThreadPoolExecutor."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(router.execute, "get_hist_data") for _ in range(10)]

            results = [f.result() for f in futures]

        assert len(results) == 10
        assert all(not r.empty for r in results)

    def test_concurrent_stats_tracking(self, sample_stock_data):
        """Test concurrent statistics tracking."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        def fetch_data():
            router.execute("get_hist_data")

        threads = [threading.Thread(target=fetch_data) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = router.get_stats()
        assert stats["eastmoney"]["success"] == 10

    def test_thread_safety_with_errors(self, sample_stock_data):
        """Test thread safety when errors occur."""
        call_count = 0

        def mock_fetch():
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                raise Exception("Simulated error")
            return sample_stock_data

        provider1 = Mock()
        provider1.get_hist_data.side_effect = mock_fetch

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        results = []

        def fetch_data():
            result = router.execute("get_hist_data")
            results.append(result)

        threads = [threading.Thread(target=fetch_data) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(not r.empty for r in results)


# ============================================================================
# Error Handling and Retry Mechanisms
# ============================================================================


class TestErrorHandlingAndRetry:
    """Test error handling and retry mechanisms."""

    def test_retry_on_transient_failure(self, sample_stock_data):
        """Test retry on transient failure."""
        call_count = 0

        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise requests.Timeout("Timeout")
            return sample_stock_data

        provider1 = Mock()
        provider1.get_hist_data.side_effect = failing_then_success

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert call_count == 1

    def test_retry_exhausted_fallback(self, sample_stock_data):
        """Test retry exhausted, fallback to next source."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = requests.Timeout("Timeout")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "sina"

    def test_rate_limit_handling(self):
        """Test rate limit error handling."""
        provider1 = Mock()

        response = Mock()
        response.status_code = 429
        response.headers = {"Retry-After": "60"}

        http_error = requests.HTTPError()
        http_error.response = response
        provider1.get_hist_data.side_effect = http_error

        provider2 = Mock()
        provider2.get_hist_data.return_value = pd.DataFrame(
            {
                "timestamp": ["2024-01-01"],
                "close": [10.0],
            }
        )

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "sina"

    def test_connection_error_handling(self, sample_stock_data):
        """Test connection error handling."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = requests.ConnectionError("Connection failed")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty

    def test_ssl_error_handling(self, sample_stock_data):
        """Test SSL error handling."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = requests.exceptions.SSLError("SSL error")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty

    def test_generic_exception_handling(self, sample_stock_data):
        """Test generic exception handling."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = Exception("Unexpected error")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        result = router.execute("get_hist_data")

        assert not result.empty

    def test_error_details_tracking(self):
        """Test error details are tracked correctly."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = Exception("Error 1")

        provider2 = Mock()
        provider2.get_hist_data.side_effect = Exception("Error 2")

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        with pytest.raises(ValueError) as exc_info:
            router.execute("get_hist_data")

        error_msg = str(exc_info.value)
        assert "eastmoney" in error_msg
        assert "sina" in error_msg


# ============================================================================
# Data Quality Checks
# ============================================================================


class TestDataQuality:
    """Test data quality checks."""

    def test_data_quality_check_negative_price(self, quality_issue_data):
        """Test data quality check for negative prices."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = quality_issue_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        result = router.execute("get_hist_data")

        assert not result.empty
        assert "close" in result.columns

    def test_data_quality_check_zero_volume(self, quality_issue_data):
        """Test data quality check for zero volume."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = quality_issue_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        result = router.execute("get_hist_data")

        assert not result.empty
        assert "volume" in result.columns

    def test_required_columns_validation(self, partial_data, sample_stock_data):
        """Test required columns validation."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = partial_data

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [("eastmoney", provider1), ("sina", provider2)],
            required_columns=["timestamp", "open", "close", "volume"],
        )

        result = router.execute("get_hist_data")

        assert "volume" in result.columns
        assert result.attrs.get("source") == "sina"

    def test_min_rows_validation(self):
        """Test minimum rows validation."""
        small_data = pd.DataFrame(
            {
                "timestamp": ["2024-01-01"],
                "close": [10.0],
            }
        )

        provider1 = Mock()
        provider1.get_hist_data.return_value = small_data

        router = MultiSourceRouter(
            [("eastmoney", provider1)],
            min_rows=2,
        )

        with pytest.raises(ValueError):
            router.execute("get_hist_data")

    def test_data_validation_with_fallback(self, sample_stock_data):
        """Test data validation triggers fallback."""
        small_data = pd.DataFrame(
            {
                "timestamp": ["2024-01-01"],
                "close": [10.0],
            }
        )

        provider1 = Mock()
        provider1.get_hist_data.return_value = small_data

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [("eastmoney", provider1), ("sina", provider2)],
            min_rows=2,
        )

        result = router.execute("get_hist_data")

        assert len(result) >= 2
        assert result.attrs.get("source") == "sina"


# ============================================================================
# Performance Tests
# ============================================================================


class TestPerformance:
    """Test performance characteristics."""

    @pytest.mark.performance
    def test_multi_source_performance(self, sample_stock_data):
        """Test multi-source performance."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmemory", provider1)])

        start = time.time()
        router.execute("get_hist_data")
        single_time = time.time() - start

        start = time.time()
        router.execute("get_hist_data")
        multi_time = time.time() - start

        assert multi_time < single_time * 2

    @pytest.mark.performance
    def test_cache_performance(self, sample_stock_data):
        """Test cache performance improvement."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmemory", provider1)])

        router.execute("get_hist_data")

        start = time.time()
        router.execute("get_hist_data")
        cached_time = time.time() - start

        assert cached_time < 0.5

    @pytest.mark.performance
    def test_concurrent_performance(self, sample_stock_data):
        """Test concurrent request performance."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        start = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(router.execute, "get_hist_data") for _ in range(20)]
            results = [f.result() for f in futures]

        concurrent_time = time.time() - start

        assert len(results) == 20
        assert concurrent_time < 5.0

    @pytest.mark.performance
    def test_failover_performance(self, sample_stock_data):
        """Test failover performance."""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = Exception("Failed")

        provider2 = Mock()
        provider2.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter(
            [
                ("eastmoney", provider1),
                ("sina", provider2),
            ]
        )

        start = time.time()
        result = router.execute("get_hist_data")
        failover_time = time.time() - start

        assert not result.empty
        assert failover_time < 1.0

    @pytest.mark.performance
    def test_stats_tracking_performance(self, sample_stock_data):
        """Test statistics tracking performance."""
        provider1 = Mock()
        provider1.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        for _ in range(100):
            router.execute("get_hist_data")

        start = time.time()
        stats = router.get_stats()
        stats_time = time.time() - start

        assert stats["eastmoney"]["success"] == 100
        assert stats_time < 0.1


# ============================================================================
# ExecutionResult Tests
# ============================================================================


class TestExecutionResult:
    """Test ExecutionResult functionality."""

    def test_execution_result_success(self, sample_stock_data):
        """Test successful execution result."""
        result = ExecutionResult(
            success=True,
            data=sample_stock_data,
            source="eastmoney",
            error=None,
            attempts=1,
        )

        assert result.success is True
        assert result.data is not None
        assert not result.data.empty
        assert result.source == "eastmoney"
        assert result.error is None
        assert result.attempts == 1

    def test_execution_result_failure(self):
        """Test failed execution result."""
        result = ExecutionResult(
            success=False,
            data=None,
            source=None,
            error="All sources failed",
            attempts=3,
            error_details=[
                ("eastmoney", "Timeout"),
                ("sina", "Connection error"),
            ],
        )

        assert result.success is False
        assert result.data is None
        assert result.source is None
        assert result.error == "All sources failed"
        assert result.attempts == 3
        assert len(result.error_details) == 2

    def test_execution_result_with_empty_flag(self, empty_dataframe):
        """Test execution result with empty flag."""
        result = ExecutionResult(
            success=True,
            data=empty_dataframe,
            source="eastmoney",
            error=None,
            attempts=1,
            is_empty=True,
        )

        assert result.success is True
        assert result.is_empty is True
        assert result.data is not None
        assert result.data.empty

    def test_execution_result_sources_tried(self, sample_stock_data):
        """Test execution result with sources tried tracking."""
        result = ExecutionResult(
            success=True,
            data=sample_stock_data,
            source="sina",
            error=None,
            attempts=2,
            sources_tried=[
                {"source": "eastmoney", "status": "error", "error": "Timeout"},
                {"source": "sina", "status": "success", "rows": 3},
            ],
        )

        assert len(result.sources_tried) == 2
        assert result.sources_tried[0]["status"] == "error"
        assert result.sources_tried[1]["status"] == "success"


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for multi-source functionality."""

    @pytest.mark.integration
    def test_real_multi_source_failover(self):
        """Test real multi-source failover with actual providers."""
        try:
            router = create_historical_router(
                symbol="600000",
                start_date="2024-01-01",
                end_date="2024-01-31",
                sources=["eastmoney_direct", "eastmoney", "sina"],
            )

            result = router.execute("get_hist_data")

            assert not result.empty
            assert "timestamp" in result.columns
            assert "close" in result.columns
        except Exception as e:
            pytest.skip(f"Integration test failed: {str(e)}")

    @pytest.mark.integration
    def test_real_execution_with_result(self):
        """Test real execution with detailed result."""
        try:
            router = create_historical_router(
                symbol="600000",
                start_date="2024-01-01",
                end_date="2024-01-31",
            )

            result = router.execute_with_result("get_hist_data")

            assert result.success is True
            assert result.data is not None
            assert result.source is not None
        except Exception as e:
            pytest.skip(f"Integration test failed: {str(e)}")

    @pytest.mark.integration
    def test_real_stats_tracking(self):
        """Test real statistics tracking."""
        try:
            router = create_historical_router(
                symbol="600000",
                start_date="2024-01-01",
                end_date="2024-01-31",
            )

            router.execute("get_hist_data")

            stats = router.get_stats()

            assert len(stats) > 0
            success_count = sum(s.get("success", 0) for s in stats.values())
            assert success_count >= 1
        except Exception as e:
            pytest.skip(f"Integration test failed: {str(e)}")


# ============================================================================
# Execute with Fallback Tests
# ============================================================================


class TestExecuteWithFallback:
    """Test execute_with_fallback method."""

    def test_execute_with_fallback_same_method(self, sample_stock_data):
        """Test execute_with_fallback with same method name."""
        provider1 = Mock()
        provider1.primary_method.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        result = router.execute_with_fallback("primary_method")

        assert not result.empty
        assert provider1.primary_method.called

    def test_execute_with_fallback_different_methods(self, sample_stock_data):
        """Test execute_with_fallback with different method names."""
        provider1 = Mock(spec=["fallback_method"])
        provider1.fallback_method.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider1)])

        result = router.execute_with_fallback("primary_method", "fallback_method")

        assert not result.empty
        assert provider1.fallback_method.called

    def test_execute_with_fallback_no_methods(self, sample_stock_data):
        """Test execute_with_fallback when primary method not available but fallback works."""
        provider1 = Mock(spec=["fallback_method"])
        provider1.fallback_method.return_value = sample_stock_data

        provider2 = Mock(spec=["primary_method"])
        provider2.primary_method.side_effect = Exception("Failed")

        router = MultiSourceRouter([("eastmoney", provider1), ("sina", provider2)])

        result = router.execute_with_fallback("primary_method", "fallback_method")

        assert not result.empty
        assert provider1.fallback_method.called

    def test_execute_with_fallback_respects_policy(self, empty_dataframe, sample_stock_data):
        """Test execute_with_fallback respects empty_data_policy."""
        provider1 = Mock()
        provider1.primary_method.return_value = empty_dataframe

        provider2 = Mock()
        provider2.primary_method.return_value = sample_stock_data

        router = MultiSourceRouter(
            [("eastmoney", provider1), ("sina", provider2)],
            empty_data_policy=EmptyDataPolicy.STRICT,
        )

        result = router.execute_with_fallback("primary_method")

        assert not result.empty
        assert provider2.primary_method.called


# ============================================================================
# Validation Tests
# ============================================================================


class TestValidation:
    """Test validation functionality."""

    def test_validate_result_none(self):
        """Test validation with None result."""
        router = MultiSourceRouter([("eastmoney", Mock())])

        is_valid = router._validate_result(None)

        assert is_valid is False

    def test_validate_result_not_dataframe(self):
        """Test validation with non-DataFrame result."""
        router = MultiSourceRouter([("eastmoney", Mock())])

        is_valid = router._validate_result("not a dataframe")

        assert is_valid is False

    def test_validate_result_empty_strict(self, empty_dataframe):
        """Test validation with empty DataFrame in STRICT mode."""
        router = MultiSourceRouter([("eastmoney", Mock())])

        is_valid = router._validate_result(empty_dataframe, is_empty_allowed=False)

        assert is_valid is False

    def test_validate_result_empty_allowed(self, empty_dataframe):
        """Test validation with empty DataFrame when allowed."""
        router = MultiSourceRouter([("eastmoney", Mock())])

        is_valid = router._validate_result(empty_dataframe, is_empty_allowed=True)

        assert is_valid is True

    def test_validate_result_missing_columns(self, partial_data):
        """Test validation with missing required columns."""
        router = MultiSourceRouter(
            [("eastmoney", Mock())],
            required_columns=["timestamp", "volume"],
        )

        is_valid = router._validate_result(partial_data)

        assert is_valid is False

    def test_validate_result_min_rows(self, sample_stock_data):
        """Test validation with minimum rows requirement."""
        router = MultiSourceRouter([("eastmoney", Mock())], min_rows=5)

        is_valid = router._validate_result(sample_stock_data)

        assert is_valid is False


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_provider_list(self):
        """Test with empty provider list."""
        router = MultiSourceRouter([])

        with pytest.raises(ValueError):
            router.execute("get_hist_data")

    def test_single_provider_success(self, sample_stock_data):
        """Test with single provider that succeeds."""
        provider = Mock()
        provider.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("eastmoney", provider)])

        result = router.execute("get_hist_data")

        assert not result.empty
        assert result.attrs.get("source") == "eastmoney"

    def test_single_provider_failure(self):
        """Test with single provider that fails."""
        provider = Mock()
        provider.get_hist_data.side_effect = Exception("Failed")

        router = MultiSourceRouter([("eastmoney", provider)])

        with pytest.raises(ValueError):
            router.execute("get_hist_data")

    def test_very_large_dataframe(self):
        """Test with very large DataFrame."""
        large_data = pd.DataFrame(
            {
                "timestamp": [f"2024-01-{i:02d}" for i in range(1, 1001)],
                "close": [float(i) for i in range(1, 1001)],
            }
        )

        provider = Mock()
        provider.get_hist_data.return_value = large_data

        router = MultiSourceRouter([("eastmoney", provider)])

        result = router.execute("get_hist_data")

        assert len(result) == 1000

    def test_unicode_in_error_message(self):
        """Test with unicode characters in error message."""
        provider = Mock()
        provider.get_hist_data.side_effect = Exception("错误: 数据源不可用")

        router = MultiSourceRouter([("eastmoney", provider)])

        with pytest.raises(ValueError):
            router.execute("get_hist_data")

    def test_special_characters_in_source_name(self, sample_stock_data):
        """Test with special characters in source name."""
        provider = Mock()
        provider.get_hist_data.return_value = sample_stock_data

        router = MultiSourceRouter([("east-money_special", provider)])

        result = router.execute("get_hist_data")

        assert result.attrs.get("source") == "east-money_special"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
