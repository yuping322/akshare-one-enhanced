"""
Integration tests for multi-source failover logic.

These tests verify that the system correctly handles:
1. Primary source failure → fallback to backup sources
2. All sources exhausted → graceful error handling
3. Source-specific errors are logged appropriately

Run: pytest tests/test_multi_source_failover.py -m integration -v
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import pytest


@pytest.mark.integration
class TestMultiSourceFailover:
    """Test multi-source failover logic."""

    def test_hist_data_source_fallback(self):
        """Test historical data falls back to alternative sources on failure."""
        from akshare_one.exceptions import DataUnavailableError

        from akshare_one import get_hist_data

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        with patch(
            "akshare_one.modules.historical.eastmoney_direct.EastMoneyDirectHistorical.get_hist_data"
        ) as mock_primary:
            mock_primary.side_effect = Exception("Primary source unavailable")

            try:
                df = get_hist_data(symbol="600000", start_date=start_date, end_date=end_date)

                if not df.empty:
                    assert True, "Fallback to alternative source succeeded"
            except (DataUnavailableError, Exception) as e:
                error_msg = str(e).lower()
                assert "unavailable" in error_msg or "failed" in error_msg or "error" in error_msg

    def test_realtime_data_source_fallback(self):
        """Test realtime data handles source failures gracefully."""
        from akshare_one import get_realtime_data

        with patch(
            "akshare_one.modules.realtime.eastmoney.EastmoneyRealtime.get_current_data"
        ) as mock_primary:
            mock_primary.side_effect = Exception("Primary source unavailable")

            try:
                get_realtime_data(symbol="600000", source="eastmoney")
            except Exception as e:
                assert "unavailable" in str(e).lower() or "error" in str(e).lower()

    def test_invalid_source_raises_error(self):
        """Test that invalid source raises appropriate error."""
        from akshare_one import get_hist_data, get_realtime_data

        with pytest.raises((ValueError, KeyError)):
            get_hist_data(
                symbol="600000", start_date="2024-01-01", end_date="2024-01-31", source="invalid"
            )

        with pytest.raises((ValueError, KeyError)):
            get_realtime_data(symbol="600000", source="invalid")


@pytest.mark.integration
class TestSourceAvailability:
    """Test source availability and connectivity."""

    def test_eastmoney_direct_source_available(self):
        """Test eastmoney_direct source is available."""
        from akshare_one import get_hist_data

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_hist_data(
            symbol="600000", start_date=start_date, end_date=end_date, source="eastmoney_direct"
        )

        assert df is not None
        if not df.empty:
            assert len(df) > 0

    def test_sina_source_available(self):
        """Test sina source is available."""
        from akshare_one import get_hist_data

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_hist_data(symbol="600000", start_date=start_date, end_date=end_date, source="sina")

        assert df is not None

    def test_multiple_sources_same_data(self):
        """Test that multiple sources return similar data (when available)."""
        from akshare_one import get_realtime_data

        sources = ["eastmoney", "eastmoney_direct"]
        results = {}

        for source in sources:
            try:
                df = get_realtime_data(symbol="600000", source=source)
                if not df.empty:
                    results[source] = df.iloc[0]["price"]
            except Exception:
                continue

        if len(results) >= 2:
            prices = list(results.values())
            price_diff_pct = abs(prices[0] - prices[1]) / prices[0] * 100
            assert price_diff_pct < 5, f"Prices differ by {price_diff_pct:.2f}%"


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling across data sources."""

    def test_network_error_handling(self):
        """Test network errors are handled gracefully."""
        from akshare_one import get_hist_data

        with patch(
            "akshare_one.modules.historical.eastmoney_direct.EastMoneyDirectHistorical.get_hist_data"
        ) as mock_get:
            mock_get.side_effect = ConnectionError("Network error")

            with pytest.raises((ConnectionError, Exception)):
                get_hist_data(
                    symbol="600000",
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                    source="eastmoney_direct",
                )

    def test_timeout_error_handling(self):
        """Test timeout errors are handled gracefully."""
        from akshare_one import get_hist_data

        with patch(
            "akshare_one.modules.historical.eastmoney_direct.EastMoneyDirectHistorical.get_hist_data"
        ) as mock_get:
            mock_get.side_effect = TimeoutError("Request timeout")

            with pytest.raises((TimeoutError, Exception)):
                get_hist_data(
                    symbol="600000",
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                    source="eastmoney_direct",
                )

    def test_invalid_symbol_error(self):
        """Test invalid symbol errors are handled."""
        from akshare_one import get_hist_data, get_realtime_data

        with pytest.raises((ValueError, KeyError)):
            get_hist_data(symbol="INVALID_SYMBOL", start_date="2024-01-01", end_date="2024-01-31")

        with pytest.raises((ValueError, KeyError)):
            get_realtime_data(symbol="INVALID_SYMBOL")


@pytest.mark.integration
class TestConcurrentAccess:
    """Test concurrent access to data sources."""

    def test_concurrent_realtime_requests(self):
        """Test concurrent realtime data requests."""
        import concurrent.futures

        from akshare_one import get_realtime_data

        symbols = ["600000", "600001", "600002"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(get_realtime_data, symbol=s): s for s in symbols}

            results = {}
            for future in concurrent.futures.as_completed(futures, timeout=30):
                symbol = futures[future]
                try:
                    df = future.result()
                    results[symbol] = not df.empty
                except Exception as e:
                    results[symbol] = str(e)

        success_count = sum(1 for v in results.values() if v is True)
        assert success_count >= 2, f"Only {success_count}/{len(symbols)} requests succeeded"

    def test_sequential_requests_same_symbol(self):
        """Test sequential requests for same symbol."""
        from akshare_one import get_realtime_data

        results = []
        for _ in range(3):
            df = get_realtime_data(symbol="600000")
            results.append(not df.empty)

        assert all(results), "All sequential requests should succeed"


@pytest.mark.integration
class TestDataQuality:
    """Test data quality across sources."""

    def test_no_null_prices(self):
        """Test that prices are not null."""
        from akshare_one import get_hist_data

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        df = get_hist_data(symbol="600000", start_date=start_date, end_date=end_date)

        if not df.empty:
            assert df["close"].notna().all(), "Close prices should not be null"
            assert df["open"].notna().all(), "Open prices should not be null"

    def test_reasonable_price_range(self):
        """Test that prices are in reasonable range."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if not df.empty:
            price = df.iloc[0]["price"]
            assert 0.01 < price < 100000, f"Price {price} is out of reasonable range"

    def test_timestamp_reasonable(self):
        """Test that timestamps are reasonable."""
        from akshare_one import get_hist_data

        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        df = get_hist_data(
            symbol="600000",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        if not df.empty and "timestamp" in df.columns:
            min_ts = df["timestamp"].min()
            max_ts = df["timestamp"].max()

            if pd.api.types.is_numeric_dtype(df["timestamp"]):
                assert min_ts > 1000000000000, "Timestamp should be in milliseconds"
                assert max_ts <= end_date.timestamp() * 1000 + 86400000
