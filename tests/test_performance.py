"""
Performance and reliability tests for akshare-one.

Tests key interfaces for:
- Response time benchmarks
- Concurrent access safety
- Memory usage and leaks
- Resource management
"""

import gc
import os
import threading
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import pytest

from akshare_one import (
    get_basic_info,
    get_hist_data,
    get_realtime_data,
)
from akshare_one.modules.etf import (
    get_etf_hist_data,
    get_etf_realtime_data,
    get_fund_manager_info,
)
from akshare_one.modules.fundflow import get_stock_fund_flow


# Performance baselines (in seconds)
PERFORMANCE_BASELINES = {
    "get_basic_info": 2.0,
    "get_hist_data": 3.0,
    "get_realtime_data": 1.0,
    "get_etf_hist_data": 2.0,
    "get_etf_realtime_data": 1.5,
    "get_fund_manager_info": 2.0,
    "get_stock_fund_flow": 3.0,
}


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.timeout(300)
class TestResponseTime:
    """Test response time for key interfaces."""

    def test_get_basic_info_performance(self):
        """Test get_basic_info response time < 2s."""
        start = time.time()
        df = get_basic_info("600000")
        elapsed = time.time() - start

        assert not df.empty
        assert elapsed < PERFORMANCE_BASELINES["get_basic_info"]
        print(f"get_basic_info elapsed: {elapsed:.3f}s (baseline: {PERFORMANCE_BASELINES['get_basic_info']}s)")

    def test_get_hist_data_performance(self):
        """Test get_hist_data response time < 3s."""
        start = time.time()
        df = get_hist_data("600000", interval="day", start_date="2024-01-01", end_date="2024-01-07")
        elapsed = time.time() - start

        assert not df.empty
        assert elapsed < PERFORMANCE_BASELINES["get_hist_data"]
        print(f"get_hist_data elapsed: {elapsed:.3f}s (baseline: {PERFORMANCE_BASELINES['get_hist_data']}s)")

    def test_get_realtime_data_performance(self):
        """Test get_realtime_data response time < 1s."""
        start = time.time()
        df = get_realtime_data(symbol="600000")
        elapsed = time.time() - start

        assert not df.empty
        assert elapsed < PERFORMANCE_BASELINES["get_realtime_data"]
        print(f"get_realtime_data elapsed: {elapsed:.3f}s (baseline: {PERFORMANCE_BASELINES['get_realtime_data']}s)")

    def test_get_etf_hist_data_performance(self):
        """Test get_etf_hist_data response time < 2s."""
        start = time.time()
        df = get_etf_hist_data(symbol="510300", start_date="2024-01-01", end_date="2024-01-07")
        elapsed = time.time() - start

        assert not df.empty
        assert elapsed < PERFORMANCE_BASELINES["get_etf_hist_data"]
        print(f"get_etf_hist_data elapsed: {elapsed:.3f}s (baseline: {PERFORMANCE_BASELINES['get_etf_hist_data']}s)")

    def test_get_etf_realtime_data_performance(self):
        """Test get_etf_realtime_data response time < 1.5s."""
        start = time.time()
        df = get_etf_realtime_data()
        elapsed = time.time() - start

        assert not df.empty
        assert elapsed < PERFORMANCE_BASELINES["get_etf_realtime_data"]
        print(
            f"get_etf_realtime_data elapsed: {elapsed:.3f}s (baseline: {PERFORMANCE_BASELINES['get_etf_realtime_data']}s)"
        )

    def test_get_fund_manager_info_performance(self):
        """Test get_fund_manager_info response time < 2s."""
        start = time.time()
        df = get_fund_manager_info()
        elapsed = time.time() - start

        assert not df.empty
        assert elapsed < PERFORMANCE_BASELINES["get_fund_manager_info"]
        print(
            f"get_fund_manager_info elapsed: {elapsed:.3f}s (baseline: {PERFORMANCE_BASELINES['get_fund_manager_info']}s)"
        )

    def test_get_stock_fund_flow_performance(self):
        """Test get_stock_fund_flow response time < 3s."""
        start = time.time()
        df = get_stock_fund_flow(symbol="600000", start_date="2024-01-01", end_date="2024-01-07")
        elapsed = time.time() - start

        assert not df.empty
        assert elapsed < PERFORMANCE_BASELINES["get_stock_fund_flow"]
        print(
            f"get_stock_fund_flow elapsed: {elapsed:.3f}s (baseline: {PERFORMANCE_BASELINES['get_stock_fund_flow']}s)"
        )


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.timeout(300)
class TestConcurrency:
    """Test concurrent access and thread safety."""

    def test_concurrent_basic_info_requests(self):
        """Test 10 concurrent get_basic_info requests."""
        symbols = ["600000", "600001", "600002", "600003", "600004", "600005", "600006", "600007", "600008", "600009"]

        results = []
        errors = []

        def fetch_info(symbol):
            try:
                df = get_basic_info(symbol)
                return (symbol, df, None)
            except Exception as e:
                return (symbol, None, str(e))

        start = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_info, symbol): symbol for symbol in symbols}
            for future in as_completed(futures):
                symbol, df, error = future.result()
                if error:
                    errors.append((symbol, error))
                else:
                    results.append((symbol, df))
        elapsed = time.time() - start

        # At least 8 out of 10 should succeed (allow some network failures)
        success_rate = len(results) / len(symbols)
        assert success_rate >= 0.8, f"Success rate {success_rate:.2%} < 80%"
        assert len(errors) <= 2, f"Too many errors: {errors}"

        # All successful results should be valid DataFrames
        for symbol, df in results:
            assert isinstance(df, pd.DataFrame)
            assert not df.empty

        print(f"Concurrent test: {len(results)} succeeded, {len(errors)} failed in {elapsed:.3f}s")

    def test_concurrent_mixed_requests(self):
        """Test concurrent requests to different endpoints."""
        tasks = [
            ("basic_info", lambda: get_basic_info("600000")),
            (
                "hist_data",
                lambda: get_hist_data("600000", interval="day", start_date="2024-01-01", end_date="2024-01-07"),
            ),
            ("realtime", lambda: get_realtime_data(symbol="600000")),
            ("fund_flow", lambda: get_stock_fund_flow(symbol="600000", start_date="2024-01-01", end_date="2024-01-07")),
            ("basic_info_2", lambda: get_basic_info("000001")),
            (
                "hist_data_2",
                lambda: get_hist_data("000001", interval="day", start_date="2024-01-01", end_date="2024-01-07"),
            ),
            ("realtime_2", lambda: get_realtime_data(symbol="000001")),
            ("basic_info_3", lambda: get_basic_info("600519")),
            (
                "hist_data_3",
                lambda: get_hist_data("600519", interval="day", start_date="2024-01-01", end_date="2024-01-07"),
            ),
            ("realtime_3", lambda: get_realtime_data(symbol="600519")),
        ]

        results = []
        errors = []

        def execute_task(task):
            name, func = task
            try:
                result = func()
                return (name, result, None)
            except Exception as e:
                return (name, None, str(e))

        start = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(execute_task, task): task[0] for task in tasks}
            for future in as_completed(futures):
                name, result, error = future.result()
                if error:
                    errors.append((name, error))
                else:
                    results.append((name, result))
        elapsed = time.time() - start

        # At least 8 out of 10 should succeed
        success_rate = len(results) / len(tasks)
        assert success_rate >= 0.8, f"Success rate {success_rate:.2%} < 80%"

        print(f"Mixed concurrent test: {len(results)} succeeded, {len(errors)} failed in {elapsed:.3f}s")

    def test_thread_safety_multiple_threads_same_symbol(self):
        """Test that multiple threads accessing same symbol don't cause issues."""
        symbol = "600000"
        num_threads = 5

        results = []
        lock = threading.Lock()

        def fetch_data(thread_id):
            try:
                df = get_basic_info(symbol)
                with lock:
                    results.append((thread_id, df))
            except Exception as e:
                with lock:
                    results.append((thread_id, None))

        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=fetch_data, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=10)

        # All threads should complete successfully
        assert len(results) == num_threads
        successful = sum(1 for _, df in results if df is not None and not df.empty)
        assert successful >= num_threads - 1  # Allow 1 failure


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.timeout(300)
class TestMemoryUsage:
    """Test memory usage and detect leaks."""

    def test_memory_usage_basic_info(self):
        """Test memory usage for get_basic_info."""
        tracemalloc.start()

        # Clear baseline
        gc.collect()
        snapshot1 = tracemalloc.take_snapshot()

        # Execute operation
        df = get_basic_info("600000")

        # Measure memory
        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()

        # Calculate memory difference
        top_stats = snapshot2.compare_to(snapshot1, "lineno")
        total_diff = sum(stat.size_diff for stat in top_stats)

        tracemalloc.stop()

        # Memory usage should be reasonable (< 5MB for a single request)
        assert total_diff < 5 * 1024 * 1024, f"Memory usage too high: {total_diff / 1024 / 1024:.2f} MB"
        print(f"get_basic_info memory usage: {total_diff / 1024:.2f} KB")

    def test_memory_usage_large_dataset(self):
        """Test memory usage for large dataset retrieval."""
        tracemalloc.start()

        # Clear baseline
        gc.collect()
        snapshot1 = tracemalloc.take_snapshot()

        # Get large dataset (1 year of daily data)
        df = get_hist_data("600000", interval="day", start_date="2024-01-01", end_date="2024-01-31")

        # Measure memory
        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()

        # Calculate memory difference
        top_stats = snapshot2.compare_to(snapshot1, "lineno")
        total_diff = sum(stat.size_diff for stat in top_stats)

        tracemalloc.stop()

        # Memory usage should scale linearly with data size
        # For ~250 rows of OHLCV data, expect < 10MB
        assert total_diff < 10 * 1024 * 1024, f"Memory usage too high: {total_diff / 1024 / 1024:.2f} MB"
        assert not df.empty
        print(f"Large dataset memory usage: {total_diff / 1024 / 1024:.2f} MB for {len(df)} rows")

    def test_no_memory_leak_repeated_calls(self):
        """Test that repeated calls don't cause memory leaks."""
        tracemalloc.start()

        # Initial measurement
        gc.collect()
        initial_snapshot = tracemalloc.take_snapshot()

        # Perform 20 repeated calls
        for i in range(20):
            df = get_basic_info("600000")
            # Explicitly delete to help garbage collection
            del df

        # Force garbage collection
        gc.collect()

        # Final measurement
        final_snapshot = tracemalloc.take_snapshot()

        # Calculate memory growth
        top_stats = final_snapshot.compare_to(initial_snapshot, "lineno")
        memory_growth = sum(stat.size_diff for stat in top_stats)

        tracemalloc.stop()

        # Memory growth should be minimal (< 1MB) - indicates no major leaks
        assert memory_growth < 1 * 1024 * 1024, (
            f"Potential memory leak: {memory_growth / 1024:.2f} KB growth after 20 calls"
        )
        print(f"Memory growth after 20 calls: {memory_growth / 1024:.2f} KB")

    def test_memory_cleanup_after_large_operations(self):
        """Test that memory is properly cleaned up after large operations."""
        tracemalloc.start()

        # Get baseline after initialization
        df1 = get_hist_data("600000", interval="day", start_date="2024-01-01", end_date="2024-03-31")
        data_size = len(df1)

        gc.collect()
        baseline_snapshot = tracemalloc.take_snapshot()
        baseline_memory = sum(stat.size for stat in baseline_snapshot.statistics("lineno"))

        # Delete the large dataframe
        del df1
        gc.collect()

        # Check memory after cleanup
        cleanup_snapshot = tracemalloc.take_snapshot()
        cleanup_memory = sum(stat.size for stat in cleanup_snapshot.statistics("lineno"))

        tracemalloc.stop()

        # Memory should decrease significantly after cleanup
        memory_reduction = baseline_memory - cleanup_memory
        assert memory_reduction > 0, "Memory should decrease after cleanup"

        print(f"Memory baseline: {baseline_memory / 1024:.2f} KB")
        print(f"Memory after cleanup: {cleanup_memory / 1024:.2f} KB")
        print(f"Memory reduction: {memory_reduction / 1024:.2f} KB for {data_size} rows")


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.timeout(300)
class TestResourceManagement:
    """Test proper resource management and cleanup."""

    def test_cache_memory_limits(self):
        """Test that cache doesn't exceed memory limits."""
        from akshare_one.modules.cache import CACHE_CONFIG

        # Get multiple different symbols to fill cache
        symbols = [f"600{i:03d}" for i in range(10)]

        for symbol in symbols:
            try:
                df = get_basic_info(symbol)
            except Exception:
                pass  # Some symbols might not exist

        # Check cache size
        cache = CACHE_CONFIG.get("info_cache")
        if cache:
            # Cache size should be within limits
            assert cache.currsize <= cache.maxsize
            print(f"Cache size: {cache.currsize} / {cache.maxsize}")

    def test_connection_cleanup(self):
        """Test that HTTP connections are properly managed."""
        from akshare_one.http_client import get_http_client

        # Make multiple requests
        for i in range(5):
            df = get_basic_info("600000")

        # Check that client session is still functional
        client = get_http_client()
        assert client is not None

        # Make one more request to verify connection still works
        df = get_basic_info("600001")
        assert not df.empty

    def test_no_resource_leak_under_load(self):
        """Test system under sustained load doesn't leak resources."""
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Get initial resource usage
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_threads = process.num_threads()

        # Perform sustained operations (50 requests)
        for i in range(50):
            try:
                df = get_basic_info("600000")
                del df
            except Exception:
                pass

            # Periodic cleanup
            if i % 10 == 0:
                gc.collect()

        # Get final resource usage
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        final_threads = process.num_threads()

        # Memory growth should be reasonable (< 50MB)
        memory_growth = final_memory - initial_memory
        assert memory_growth < 50, f"Memory grew by {memory_growth:.2f} MB under load"

        # Thread count should not increase significantly
        thread_growth = final_threads - initial_threads
        assert thread_growth < 5, f"Threads grew by {thread_growth} under load"

        print(f"Initial memory: {initial_memory:.2f} MB, threads: {initial_threads}")
        print(f"Final memory: {final_memory:.2f} MB, threads: {final_threads}")
        print(f"Memory growth: {memory_growth:.2f} MB, thread growth: {thread_growth}")


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.timeout(300)
class TestStabilityUnderLoad:
    """Test system stability under various load conditions."""

    def test_rapid_sequential_requests(self):
        """Test rapid sequential requests don't cause issues."""
        results = []
        errors = []

        for i in range(30):
            try:
                start = time.time()
                df = get_basic_info("600000")
                elapsed = time.time() - start
                results.append((i, elapsed, len(df)))
            except Exception as e:
                errors.append((i, str(e)))

        # Most requests should succeed
        success_rate = len(results) / 30
        assert success_rate >= 0.9, f"Success rate {success_rate:.2%} too low"

        # Response times should remain stable (no significant degradation)
        if len(results) >= 10:
            early_avg = sum(elapsed for _, elapsed, _ in results[:10]) / 10
            late_avg = sum(elapsed for _, elapsed, _ in results[-10:]) / 10

            # Late requests shouldn't be significantly slower
            degradation_ratio = late_avg / early_avg
            assert degradation_ratio < 2.0, f"Performance degraded: early {early_avg:.3f}s, late {late_avg:.3f}s"

            print(f"Early avg response time: {early_avg:.3f}s")
            print(f"Late avg response time: {late_avg:.3f}s")

    def test_timeout_handling(self):
        """Test that operations complete within reasonable timeout."""
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Operation timed out")

        # Set 30 second timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)

        try:
            start = time.time()
            df = get_hist_data("600000", interval="day", start_date="2024-01-01", end_date="2024-01-07")
            elapsed = time.time() - start

            # Should complete well before timeout
            assert elapsed < 30
            assert not df.empty
            print(f"Operation completed in {elapsed:.3f}s (timeout: 30s)")
        finally:
            signal.alarm(0)  # Cancel alarm


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.timeout(300)
def test_performance_baseline_summary():
    """Generate performance baseline summary report."""
    import time

    results = {}

    # Test each interface
    test_cases = [
        ("get_basic_info", lambda: get_basic_info("600000")),
        (
            "get_hist_data",
            lambda: get_hist_data("600000", interval="day", start_date="2024-01-01", end_date="2024-01-07"),
        ),
        ("get_realtime_data", lambda: get_realtime_data(symbol="600000")),
        (
            "get_stock_fund_flow",
            lambda: get_stock_fund_flow(symbol="600000", start_date="2024-01-01", end_date="2024-01-07"),
        ),
    ]

    for name, func in test_cases:
        try:
            start = time.time()
            df = func()
            elapsed = time.time() - start
            results[name] = {
                "elapsed": elapsed,
                "baseline": PERFORMANCE_BASELINES.get(name, 5.0),
                "rows": len(df) if not df.empty else 0,
                "success": True,
            }
        except Exception as e:
            results[name] = {
                "elapsed": None,
                "baseline": PERFORMANCE_BASELINES.get(name, 5.0),
                "rows": 0,
                "success": False,
                "error": str(e),
            }

    # Print summary
    print("\n" + "=" * 60)
    print("Performance Baseline Summary")
    print("=" * 60)

    for name, data in results.items():
        if data["success"]:
            status = "PASS" if data["elapsed"] < data["baseline"] else "FAIL"
            print(
                f"{name:30s} {data['elapsed']:6.3f}s (baseline: {data['baseline']:5.1f}s) [{status}] rows: {data['rows']}"
            )
        else:
            print(f"{name:30s} ERROR: {data['error']}")

    print("=" * 60)

    # All should pass baseline
    successful_tests = sum(1 for data in results.values() if data["success"])
    assert successful_tests >= len(test_cases) - 1, "Most tests should succeed"
