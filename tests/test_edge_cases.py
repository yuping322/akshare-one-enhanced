"""
Edge case tests for boundary conditions.

These tests verify correct handling of:
1. Extreme date ranges (future, single day, leap year)
2. Invalid symbols
3. Empty data scenarios
4. Numeric boundary conditions

Run: pytest tests/test_edge_cases.py -v
"""

from datetime import datetime, timedelta

import pandas as pd
import pytest

# ============================================================================
# Date Boundary Tests
# ============================================================================


class TestDateBoundaries:
    """Test boundary conditions for date parameters."""

    def test_future_date_range(self):
        """Test with future date range."""
        from akshare_one import get_hist_data

        future_start = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        future_end = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

        df = get_hist_data(symbol="600000", start_date=future_start, end_date=future_end)

        assert df is not None
        assert df.empty or len(df) == 0

    def test_single_day_range(self):
        """Test with single day date range."""
        from akshare_one import get_hist_data

        today = datetime.now().strftime("%Y-%m-%d")

        df = get_hist_data(symbol="600000", start_date=today, end_date=today)

        assert df is not None

    def test_leap_year_date(self):
        """Test with leap year date (Feb 29)."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-02-29", end_date="2024-02-29")

        assert df is not None

    def test_weekend_date_range(self):
        """Test with weekend date range."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-01-06", end_date="2024-01-07")

        assert df is not None

    def test_chinese_new_year_period(self):
        """Test with Chinese New Year holiday period."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-02-10", end_date="2024-02-17")

        assert df is not None

    def test_very_old_date(self):
        """Test with very old historical date."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2000-01-01", end_date="2000-01-31")

        assert df is not None

    def test_invalid_date_format(self):
        """Test with invalid date format."""
        from akshare_one import get_hist_data

        with pytest.raises((ValueError, Exception)):
            get_hist_data(symbol="600000", start_date="2024-13-01", end_date="2024-01-31")

        with pytest.raises((ValueError, Exception)):
            get_hist_data(symbol="600000", start_date="invalid", end_date="2024-01-31")


class TestSymbolBoundaries:
    """Test boundary conditions for symbol parameters."""

    def test_empty_symbol(self):
        """Test with empty symbol."""
        from akshare_one import get_hist_data, get_realtime_data

        with pytest.raises((ValueError, Exception)):
            get_hist_data(symbol="", start_date="2024-01-01", end_date="2024-01-31")

        with pytest.raises((ValueError, Exception)):
            get_realtime_data(symbol="")

    def test_invalid_symbol_format(self):
        """Test with invalid symbol format."""
        from akshare_one import get_hist_data, get_realtime_data

        with pytest.raises((ValueError, KeyError, Exception)):
            get_hist_data(symbol="INVALID", start_date="2024-01-01", end_date="2024-01-31")

        with pytest.raises((ValueError, KeyError, Exception)):
            get_realtime_data(symbol="INVALID")

    def test_nonexistent_symbol(self):
        """Test with non-existent symbol."""
        from akshare_one import get_hist_data

        with pytest.raises((ValueError, KeyError, Exception)):
            get_hist_data(symbol="999999", start_date="2024-01-01", end_date="2024-01-31")

    def test_different_symbol_types(self):
        """Test with different symbol types (A-share, B-share, HK)."""
        from akshare_one import get_hist_data

        a_share = get_hist_data(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")
        assert a_share is not None

        b_share = get_hist_data(
            symbol="sh900901", start_date="2024-01-01", end_date="2024-01-31", source="sina"
        )
        assert b_share is not None

        hk_stock = get_hist_data(
            symbol="00700",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="eastmoney_direct",
        )
        assert hk_stock is not None


class TestNumericBoundaries:
    """Test numeric boundary conditions."""

    def test_zero_volume(self):
        """Test handling of zero volume."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        if not df.empty:
            assert (df["volume"] >= 0).all()

    def test_extreme_price_values(self):
        """Test handling of extreme price values."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        if not df.empty:
            price = df.iloc[0]["price"]
            assert 0 < price < 1000000

    def test_negative_values_not_allowed(self):
        """Test that negative values are not present."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2024-01-01", end_date="2024-01-31")

        if not df.empty:
            assert (df["open"] > 0).all()
            assert (df["high"] > 0).all()
            assert (df["low"] > 0).all()
            assert (df["close"] > 0).all()

    def test_large_date_range(self):
        """Test with very large date range."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2020-01-01", end_date="2024-01-31")

        assert df is not None
        if not df.empty:
            assert len(df) > 100


class TestEmptyDataScenarios:
    """Test handling of empty data scenarios."""

    def test_no_data_for_period(self):
        """Test handling when no data available for period."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2099-01-01", end_date="2099-01-31")

        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_empty_dataframe_structure(self):
        """Test that empty DataFrame has correct structure."""
        from akshare_one import get_hist_data

        df = get_hist_data(symbol="600000", start_date="2099-01-01", end_date="2099-01-31")

        if df.empty:
            expected_columns = {"timestamp", "open", "high", "low", "close", "volume"}
            if len(df.columns) > 0:
                assert expected_columns.issubset(set(df.columns))


class TestAdjustmentBoundaries:
    """Test boundary conditions for adjustments."""

    def test_qfq_adjustment(self):
        """Test forward adjustment."""
        from akshare_one import get_hist_data

        df = get_hist_data(
            symbol="600000", adjust="qfq", start_date="2024-01-01", end_date="2024-01-31"
        )

        assert df is not None
        if not df.empty:
            assert (df["close"] > 0).all()

    def test_hfq_adjustment(self):
        """Test backward adjustment."""
        from akshare_one import get_hist_data

        df = get_hist_data(
            symbol="600000", adjust="hfq", start_date="2024-01-01", end_date="2024-01-31"
        )

        assert df is not None
        if not df.empty:
            assert (df["close"] > 0).all()

    def test_no_adjustment(self):
        """Test no adjustment."""
        from akshare_one import get_hist_data

        df = get_hist_data(
            symbol="600000", adjust=None, start_date="2024-01-01", end_date="2024-01-31"
        )

        assert df is not None


class TestIntervalBoundaries:
    """Test boundary conditions for intervals."""

    def test_day_interval(self):
        """Test day interval."""
        from akshare_one import get_hist_data

        df = get_hist_data(
            symbol="600000", interval="day", start_date="2024-01-01", end_date="2024-01-31"
        )

        assert df is not None

    def test_minute_interval(self):
        """Test minute interval."""
        from akshare_one import get_hist_data

        df = get_hist_data(
            symbol="600000",
            interval="minute",
            interval_multiplier=5,
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sina",
        )

        assert df is not None

    def test_invalid_interval(self):
        """Test invalid interval."""
        from akshare_one import get_hist_data

        with pytest.raises((ValueError, KeyError, Exception)):
            get_hist_data(
                symbol="600000", interval="invalid", start_date="2024-01-01", end_date="2024-01-31"
            )


class TestMultiSymbolBoundaries:
    """Test boundary conditions for multiple symbols."""

    def test_single_symbol(self):
        """Test with single symbol."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000")

        assert df is not None
        assert len(df) == 1 or df.empty

    def test_multiple_symbols(self):
        """Test with multiple symbols."""
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol=["600000", "600001"])

        assert df is not None
        if not df.empty:
            assert len(df) <= 2


class TestCacheBoundaries:
    """Test boundary conditions for caching."""

    def test_repeated_requests(self):
        """Test repeated requests return consistent data."""
        from akshare_one import get_realtime_data

        df1 = get_realtime_data(symbol="600000")
        df2 = get_realtime_data(symbol="600000")

        assert df1 is not None
        assert df2 is not None

        if not df1.empty and not df2.empty:
            assert df1.columns.equals(df2.columns)


class TestConcurrencyBoundaries:
    """Test boundary conditions for concurrent access."""

    def test_sequential_requests_stability(self):
        """Test that sequential requests are stable."""
        from akshare_one import get_realtime_data

        results = []
        for _ in range(5):
            df = get_realtime_data(symbol="600000")
            results.append(df is not None)

        assert all(results)
