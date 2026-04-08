#!/usr/bin/env python3
"""
Test script for Lixinger providers.

This script tests basic functionality of the Lixinger data providers
integrated into various modules.
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from akshare_one.modules.valuation import get_stock_valuation
from akshare_one.modules.historical import get_hist_data
from akshare_one.modules.index import get_index_constituents, get_index_list
from akshare_one.modules.macro import get_cpi_data
from akshare_one.modules.margin import get_margin_data


def test_valuation():
    print("\n=== Testing Valuation Module (Lixinger) ===")

    try:
        df = get_stock_valuation(symbol="600519", start_date="2024-12-01", end_date="2024-12-10", source="lixinger")
        print(f"✓ Valuation data: {len(df)} rows")
        if not df.empty:
            print(df.head())
    except Exception as e:
        print(f"✗ Error: {e}")


def test_historical():
    print("\n=== Testing Historical Module (Lixinger) ===")

    try:
        df = get_hist_data(
            symbol="600519", start_date="2024-12-01", end_date="2024-12-10", adjust="qfq", source="lixinger"
        )
        print(f"✓ Historical data: {len(df)} rows")
        if not df.empty:
            print(df.head())
    except Exception as e:
        print(f"✗ Error: {e}")


def test_index():
    print("\n=== Testing Index Module (Lixinger) ===")

    print("\n1. Testing get_index_list...")
    try:
        df = get_index_list(category="cn", source="lixinger")
        print(f"✓ Index list: {len(df)} rows")
        if not df.empty:
            print(df.head())
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n2. Testing get_index_constituents...")
    try:
        df = get_index_constituents(
            symbol="000300",  # 沪深300
            include_weight=True,
            source="lixinger",
        )
        print(f"✓ Index constituents: {len(df)} rows")
        if not df.empty:
            print(df.head(10))
    except Exception as e:
        print(f"✗ Error: {e}")


def test_macro():
    print("\n=== Testing Macro Module (Lixinger) ===")

    try:
        df = get_cpi_data(start_date="2024-01-01", end_date="2024-12-31", source="lixinger")
        print(f"✓ CPI data: {len(df)} rows")
        if not df.empty:
            print(df.head())
    except Exception as e:
        print(f"✗ Error: {e}")


def test_margin():
    print("\n=== Testing Margin Module (Lixinger) ===")

    try:
        df = get_margin_data(symbol="600519", start_date="2024-12-01", end_date="2024-12-10", source="lixinger")
        print(f"✓ Margin data: {len(df)} rows")
        if not df.empty:
            print(df.head())
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    print("=" * 60)
    print("Lixinger Provider Integration Test Suite")
    print("=" * 60)

    if not os.getenv("LIXINGER_TOKEN"):
        print("\n⚠ WARNING: LIXINGER_TOKEN not found in environment.")
        print("Please set LIXINGER_TOKEN or create token.cfg file.")
        print("Tests will fail without valid token.\n")

    test_valuation()
    test_historical()
    test_index()
    test_macro()
    test_margin()

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
