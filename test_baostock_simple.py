#!/usr/bin/env python
"""
Simple test for Baostock basic functionality.
"""

import sys

sys.path.insert(0, "src")

import pandas as pd
from akshare_one.modules.historical import HistoricalDataFactory


def test_basic():
    """Test basic baostock functionality."""
    print("Testing Baostock basic functionality...")

    # Test 1: List sources
    sources = HistoricalDataFactory.list_sources()
    print(f"Available sources: {sources}")
    assert "baostock" in sources
    print("✓ Baostock registered")

    # Test 2: Fetch daily data
    provider = HistoricalDataFactory.get_provider(
        "baostock", symbol="sh.600000", interval="day", start_date="2024-01-01", end_date="2024-01-10"
    )

    print("Fetching daily data...")
    df = provider.get_hist_data()

    print(f"✓ Fetched {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")

    if not df.empty:
        print("\nSample data:")
        print(df.head(3))

    print("\n✅ All basic tests passed!")


if __name__ == "__main__":
    test_basic()
