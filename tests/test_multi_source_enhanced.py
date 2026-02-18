"""Test suite for enhanced MultiSourceRouter functionality"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unittest.mock import Mock

import pandas as pd
import pytest

from akshare_one.modules.multi_source import (
    ExecutionResult,
    MultiSourceRouter,
)


class TestExecutionResult:
    """Test ExecutionResult dataclass"""

    def test_execution_result_success(self):
        """Test successful execution result"""
        df = pd.DataFrame({"col": [1, 2, 3]})
        result = ExecutionResult(
            success=True,
            data=df,
            source="test_source",
            error=None,
            attempts=1,
        )

        assert result.success is True
        assert result.source == "test_source"
        assert len(result.data) == 3
        assert result.error is None
        assert result.attempts == 1

    def test_execution_result_failure(self):
        """Test failed execution result"""
        result = ExecutionResult(
            success=False,
            data=None,
            source=None,
            error="All sources failed",
            attempts=3,
            error_details=[
                ("source1", "Network timeout"),
                ("source2", "Empty response"),
            ],
        )

        assert result.success is False
        assert result.source is None
        assert result.data is None
        assert len(result.error_details) == 2


class TestMultiSourceRouter:
    """Test MultiSourceRouter with enhanced validation"""

    def test_router_initialization(self):
        """Test router initialization with providers"""
        provider1 = Mock()
        provider2 = Mock()

        router = MultiSourceRouter(
            providers=[
                ("source1", provider1),
                ("source2", provider2),
            ]
        )

        assert len(router.providers) == 2
        assert router.providers[0][0] == "source1"

    def test_result_validation_empty_dataframe(self):
        """Test validation rejects empty DataFrame"""
        router = MultiSourceRouter(providers=[])

        # Empty DataFrame should be invalid
        assert router._validate_result(pd.DataFrame()) is False

    def test_result_validation_required_columns(self):
        """Test validation checks for required columns"""
        router = MultiSourceRouter(
            providers=[],
            required_columns=["col1", "col2"],
        )

        # DataFrame missing required columns should be invalid
        df_missing = pd.DataFrame({"col1": [1, 2, 3]})
        assert router._validate_result(df_missing) is False

        # DataFrame with required columns should be valid
        df_valid = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        assert router._validate_result(df_valid) is True

    def test_result_validation_min_rows(self):
        """Test validation checks minimum rows"""
        router = MultiSourceRouter(
            providers=[],
            min_rows=3,
        )

        # DataFrame with too few rows should be invalid
        df_few = pd.DataFrame({"col": [1, 2]})
        assert router._validate_result(df_few) is False

        # DataFrame with enough rows should be valid
        df_enough = pd.DataFrame({"col": [1, 2, 3, 4]})
        assert router._validate_result(df_enough) is True

    def test_execute_with_valid_first_source(self):
        """Test execution succeeds with first source"""
        df_result = pd.DataFrame({
            "timestamp": ["2024-01-01"],
            "open": [100.0],
            "high": [101.0],
            "low": [99.0],
            "close": [100.5],
            "volume": [1000],
        })

        provider1 = Mock()
        provider1.get_hist_data.return_value = df_result

        router = MultiSourceRouter(
            providers=[("source1", provider1)],
            required_columns=["timestamp", "open", "close"],
        )

        result = router.execute("get_hist_data")
        assert len(result) == 1
        assert result.iloc[0]["timestamp"] == "2024-01-01"

    def test_execute_with_failover(self):
        """Test execution falls back to second source on first failure"""
        df_result = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        })

        # First provider fails
        provider1 = Mock()
        provider1.get_hist_data.side_effect = Exception("Network error")

        # Second provider succeeds
        provider2 = Mock()
        provider2.get_hist_data.return_value = df_result

        router = MultiSourceRouter(
            providers=[
                ("source1", provider1),
                ("source2", provider2),
            ],
        )

        result = router.execute("get_hist_data")
        assert len(result) == 3
        provider2.get_hist_data.assert_called_once()

    def test_execute_all_sources_fail(self):
        """Test execution fails when all sources fail"""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = Exception("Error 1")

        provider2 = Mock()
        provider2.get_hist_data.side_effect = Exception("Error 2")

        router = MultiSourceRouter(
            providers=[
                ("source1", provider1),
                ("source2", provider2),
            ],
        )

        with pytest.raises(ValueError) as exc_info:
            router.execute("get_hist_data")

        assert "All data sources failed" in str(exc_info.value)
        assert "Error 1" in str(exc_info.value)
        assert "Error 2" in str(exc_info.value)

    def test_execute_with_result_success(self):
        """Test execute_with_result returns success"""
        df_result = pd.DataFrame({"col": [1, 2, 3]})

        provider = Mock()
        provider.get_hist_data.return_value = df_result

        router = MultiSourceRouter(
            providers=[("test_source", provider)],
        )

        result = router.execute_with_result("get_hist_data")

        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.source == "test_source"
        assert result.attempts == 1
        assert result.error is None

    def test_execute_with_result_failure(self):
        """Test execute_with_result returns failure without raising"""
        provider1 = Mock()
        provider1.get_hist_data.side_effect = Exception("Error 1")

        provider2 = Mock()
        provider2.get_hist_data.side_effect = Exception("Error 2")

        router = MultiSourceRouter(
            providers=[
                ("source1", provider1),
                ("source2", provider2),
            ],
        )

        result = router.execute_with_result("get_hist_data")

        assert isinstance(result, ExecutionResult)
        assert result.success is False
        assert result.source is None
        assert result.data is None
        assert result.attempts == 2
        assert len(result.error_details) == 2

    def test_execution_statistics(self):
        """Test execution statistics tracking"""
        # Create successful provider
        provider_success = Mock()
        provider_success.get_hist_data.return_value = pd.DataFrame({"col": [1]})

        # Create failing provider
        provider_fail = Mock()
        provider_fail.get_hist_data.side_effect = Exception("Error")

        router = MultiSourceRouter(
            providers=[
                ("success_source", provider_success),
                ("fail_source", provider_fail),
            ],
        )

        # Execute multiple times
        for _ in range(3):
            router.execute("get_hist_data")

        stats = router.get_stats()

        # Success source should have 3 successes
        assert stats["success_source"]["success"] == 3
        assert stats["success_source"]["failure"] == 0

        # Fail source should not be called (early exit)
        # So its stats should be empty or not exist
        if "fail_source" in stats:
            assert stats["fail_source"]["failure"] == 0

    def test_empty_result_validation_and_fallback(self):
        """Test that empty results trigger fallback"""
        # First provider returns empty
        provider1 = Mock()
        provider1.get_hist_data.return_value = pd.DataFrame()

        # Second provider returns valid data
        provider2 = Mock()
        provider2.get_hist_data.return_value = pd.DataFrame({"col": [1, 2, 3]})

        router = MultiSourceRouter(
            providers=[
                ("source1", provider1),
                ("source2", provider2),
            ],
        )

        result = router.execute("get_hist_data")
        assert len(result) == 3


class TestMultiSourceRouterIntegration:
    """Integration tests with actual provider patterns"""

    def test_historical_data_sources_priority(self):
        """Test historical data source priority order"""
        # Simulate historical data providers
        providers = []

        # eastmoney_direct (primary)
        em_direct = Mock()
        em_direct.get_hist_data.return_value = pd.DataFrame({
            "timestamp": ["2024-01-01"],
            "open": [100.0],
            "close": [100.5],
            "volume": [1000],
        })
        providers.append(("eastmoney_direct", em_direct))

        # sina (backup)
        sina = Mock()
        sina.get_hist_data.return_value = pd.DataFrame({
            "timestamp": ["2024-01-01"],
            "open": [100.0],
            "close": [100.5],
            "volume": [1000],
        })
        providers.append(("sina", sina))

        router = MultiSourceRouter(
            providers=providers,
            required_columns=["timestamp", "open", "close", "volume"],
        )

        result = router.execute("get_hist_data")
        assert not result.empty
        assert em_direct.get_hist_data.called
        assert not sina.get_hist_data.called  # Should not be called

    def test_realtime_data_source_fallback(self):
        """Test realtime data with source fallback"""
        # First source fails
        provider1 = Mock()
        provider1.get_current_data.side_effect = Exception("Rate limited")

        # Second source succeeds
        provider2 = Mock()
        provider2.get_current_data.return_value = pd.DataFrame({
            "symbol": ["600000"],
            "price": [100.5],
            "timestamp": ["15:30:00"],
        })

        router = MultiSourceRouter(
            providers=[
                ("eastmoney", provider1),
                ("xueqiu", provider2),
            ],
            required_columns=["symbol", "price"],
        )

        result = router.execute_with_result("get_current_data")

        assert result.success is True
        assert result.source == "xueqiu"
        assert result.attempts == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
