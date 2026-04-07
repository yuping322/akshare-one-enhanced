"""
Example tests demonstrating test stability improvements.

This file shows how to use the new stability features:
1. pytest-rerunfailures automatic retry
2. retry_on_failure decorator
3. flaky_test decorator
4. retry_on_network_error decorator
5. Enhanced error handling
"""

import pytest
from tests.conftest import retry_on_failure
from tests.utils.integration_helpers import flaky_test, integration_rate_limiter


# ============================================================================
# Example 1: Automatic Retry with pytest-rerunfailures
# ============================================================================


class TestAutomaticRetryExample:
    """Tests that benefit from automatic retry mechanism."""

    def test_simple_api_call(self):
        """
        This test will be automatically retried if it fails.
        No special decorator needed - pytest-rerunfailures handles it.

        Default: 2 retries with 1-second delay (configured in pyproject.toml)
        """
        # Simulate a test that might occasionally fail due to network issues
        import random

        # This test has a 10% chance of failure, demonstrating retry
        if random.random() < 0.1:
            pytest.fail("Simulated random failure - will be retried automatically")

        # Normal test logic
        assert True, "Test passed successfully"


# ============================================================================
# Example 2: Manual Retry with retry_on_failure Decorator
# ============================================================================


class TestManualRetryExample:
    """Tests with custom retry logic using retry_on_failure decorator."""

    @retry_on_failure(max_retries=3, delay=2.0, exceptions=(ValueError, KeyError))
    def test_with_custom_retry(self):
        """
        This test uses custom retry decorator for specific exceptions.

        Features:
        - Max 3 retries (instead of default 2)
        - 2-second delay (instead of default 1)
        - Only retries on ValueError or KeyError
        """
        import random

        # Simulate occasional failure
        if random.random() < 0.15:
            raise ValueError("Simulated ValueError - will be retried")

        assert True, "Test passed"


# ============================================================================
# Example 3: Flaky Test Handling
# ============================================================================


@pytest.mark.flaky
class TestFlakyTestExample:
    """
    Tests marked as flaky are known to be unstable.
    They need special handling and more retries.
    """

    @flaky_test(max_retries=5, retry_delay=3.0)
    def test_known_flaky_api(self):
        """
        This test is marked as flaky and has custom retry logic.

        Features:
        - Marked with @pytest.mark.flaky for documentation
        - Uses flaky_test decorator with 5 retries
        - Longer retry delay (3 seconds)
        - Will be logged as flaky test failure for monitoring
        """
        import random

        # Simulate a test that fails 20% of the time
        if random.random() < 0.2:
            pytest.fail("Flaky test failed - will retry up to 5 times")

        assert True, "Flaky test eventually passed"


# ============================================================================
# Example 4: Network Error Handling with Rate Limiter
# ============================================================================


@pytest.mark.integration
class TestNetworkErrorHandlingExample:
    """Tests that handle network errors with automatic retry."""

    @integration_rate_limiter.retry_on_network_error
    def test_api_with_network_retry(self):
        """
        This test automatically retries on network errors.

        Features:
        - Rate limiting: 1 call per second
        - Retry on: ConnectionError, TimeoutError, OSError
        - Max retries: 3
        - Retry delay: 5 seconds
        """
        # Simulate network call
        import random

        if random.random() < 0.1:
            raise ConnectionError("Simulated connection error - will retry")

        # Normal test logic
        assert True, "Network call succeeded"


# ============================================================================
# Example 5: Graceful Data Availability Handling
# ============================================================================


class TestGracefulHandlingExample:
    """Tests that handle data unavailability gracefully."""

    def test_with_data_availability_check(self):
        """
        Test that skips gracefully when data is unavailable.

        This is better than failing when the issue is with data availability,
        not with the code logic.
        """
        # Simulate data fetch
        import pandas as pd

        df = pd.DataFrame()  # Empty DataFrame simulation

        # Skip test if no data available
        if df.empty:
            pytest.skip("No data available for testing - not a code issue")

        # Continue with assertions if data is available
        assert len(df) > 0, "Data should not be empty"


# ============================================================================
# Example 6: Timeout Protection
# ============================================================================


@pytest.mark.timeout(30)  # 30 second timeout
class TestTimeoutExample:
    """Tests with timeout protection to prevent hanging."""

    def test_with_timeout_protection(self):
        """
        Test that has timeout protection.

        If this test takes longer than 30 seconds, it will be terminated
        and marked as failed. This prevents tests from hanging indefinitely.
        """
        # Simulate a test that might take too long
        import time

        # Normal fast test
        time.sleep(0.1)  # Quick operation

        assert True, "Test completed within timeout"


# ============================================================================
# Example 7: Comprehensive Stability Example
# ============================================================================


@pytest.mark.integration
@pytest.mark.flaky
class TestComprehensiveStabilityExample:
    """
    Example combining multiple stability features.

    This shows best practices for writing stable integration tests.
    """

    @integration_rate_limiter.retry_on_network_error
    @retry_on_failure(max_retries=4, delay=2.5)
    @pytest.mark.timeout(60)
    def test_comprehensive_stability(self, test_logger):
        """
        Test combining all stability features:

        1. Network retry (from rate_limiter)
        2. Custom retry (from retry_on_failure)
        3. Timeout protection (60 seconds)
        4. Logging (from test_logger fixture)
        """
        test_logger.info("Starting comprehensive stability test")

        try:
            # Simulate API call that might have various issues
            import random
            import pandas as pd

            # Simulate different types of failures
            failure_type = random.choice(["none", "network", "logic", "timeout"])

            if failure_type == "network":
                test_logger.warning("Simulating network error")
                raise ConnectionError("Network error - will retry")
            elif failure_type == "logic":
                test_logger.warning("Simulating logic error")
                raise ValueError("Logic error - will retry")
            elif failure_type == "timeout":
                test_logger.warning("Simulating timeout")
                # This would trigger timeout if it was real
                # In example, we just fail to show handling
                pytest.fail("Test timed out")
            else:
                test_logger.info("Test running normally")

                # Normal test logic
                df = pd.DataFrame({"value": [1, 2, 3]})

                # Data availability check
                if df.empty:
                    test_logger.info("No data available, skipping test")
                    pytest.skip("No data available")

                # Assertions
                assert len(df) == 3, "DataFrame should have 3 rows"
                test_logger.info("Test completed successfully")

        except Exception as e:
            test_logger.error(f"Test failed: {str(e)}")
            raise


# ============================================================================
# Example 8: Test Independence Example
# ============================================================================


class TestIndependenceExample:
    """
    Example showing test independence best practices.

    Each test should:
    1. Use fresh fixtures (no shared mutable state)
    2. Not depend on execution order
    3. Clean up resources after completion
    """

    def test_independent_1(self, mock_data_generator):
        """Test 1: Generates its own fresh data."""
        df = mock_data_generator.generate_mock_dataframe(
            columns=["date", "symbol", "close"], row_count=10
        )

        # Test uses isolated data
        assert len(df) == 10
        # No side effects on other tests

    def test_independent_2(self, mock_data_generator):
        """Test 2: Generates its own fresh data (no dependency on test 1)."""
        df = mock_data_generator.generate_mock_dataframe(
            columns=["date", "symbol", "close"], row_count=20
        )

        # Test uses different data, no dependency on test 1
        assert len(df) == 20

    def test_independent_3(self, mock_data_generator):
        """Test 3: Can run independently of test 1 and 2."""
        df = mock_data_generator.generate_mock_dataframe(
            columns=["date", "symbol", "close"], row_count=30
        )

        # Completely independent test
        assert len(df) == 30


# ============================================================================
# Running Examples
# ============================================================================


if __name__ == "__main__":
    # Run examples to see stability features in action
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-m", "not integration",  # Skip integration tests without network
            "-p", "no:warnings",  # Disable warnings for cleaner output
        ]
    )