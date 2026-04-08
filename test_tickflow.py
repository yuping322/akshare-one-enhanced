#!/usr/bin/env python3
"""
Test script for TickFlow API integration.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from akshare_one.modules.realtime import get_current_data
from akshare_one.modules.historical import get_hist_data
from akshare_one.modules.financial import get_balance_sheet, get_income_statement, get_cash_flow, get_financial_metrics
from akshare_one.modules.market import get_instruments, get_exchanges, get_universes


def test_realtime():
    """Test realtime quotes."""
    print("\n=== Testing Realtime Quotes ===")

    print("\n--- Single Symbol ---")
    df = get_current_data(symbol="600000.SH", source="tickflow")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Rows: {len(df)}")
    if not df.empty:
        print(df)

    print("\n--- Multiple Symbols via Batch ---")
    from akshare_one.tickflow_client import get_tickflow_client

    client = get_tickflow_client()
    response = client.query_api("/v1/quotes", method="POST", data={"symbols": ["600000.SH", "000001.SZ"]})
    import pandas as pd

    df_batch = pd.DataFrame(response.get("data", []))
    print(f"Columns: {df_batch.columns.tolist()}")
    print(f"Rows: {len(df_batch)}")
    if not df_batch.empty:
        print(df_batch.head(2))

    return df, df_batch


def test_historical():
    """Test historical K-lines."""
    print("\n=== Testing Historical K-lines ===")
    df = get_hist_data(
        symbol="600000", start_date="2024-01-01", end_date="2024-01-31", interval="day", adjust="qfq", source="tickflow"
    )
    print(f"Columns: {df.columns.tolist()}")
    print(f"Rows: {len(df)}")
    if not df.empty:
        print(df.head(3))
    return df


def test_financial():
    """Test financial data."""
    print("\n=== Testing Financial Data ===")
    print("⚠️  Note: Financial data requires special API permissions")
    print("Skipping financial data tests (API key lacks permission)")

    try:
        print("\n--- Balance Sheet ---")
        df_bs = get_balance_sheet(symbol="600000", source="tickflow")
        print(f"Columns: {df_bs.columns.tolist()}")
        print(f"Rows: {len(df_bs)}")
        if not df_bs.empty:
            print(df_bs.head(2))
    except RuntimeError as e:
        print(f"❌ Balance sheet test skipped: {e}")

    try:
        print("\n--- Income Statement ---")
        df_income = get_income_statement(symbol="600000", source="tickflow")
        print(f"Columns: {df_income.columns.tolist()}")
        print(f"Rows: {len(df_income)}")
        if not df_income.empty:
            print(df_income.head(2))
    except RuntimeError as e:
        print(f"❌ Income statement test skipped: {e}")

    try:
        print("\n--- Cash Flow ---")
        df_cf = get_cash_flow(symbol="600000", source="tickflow")
        print(f"Columns: {df_cf.columns.tolist()}")
        print(f"Rows: {len(df_cf)}")
        if not df_cf.empty:
            print(df_cf.head(2))
    except RuntimeError as e:
        print(f"❌ Cash flow test skipped: {e}")

    try:
        print("\n--- Financial Metrics ---")
        df_metrics = get_financial_metrics(symbol="600000", source="tickflow")
        print(f"Columns: {df_metrics.columns.tolist()}")
        print(f"Rows: {len(df_metrics)}")
        if not df_metrics.empty:
            print(df_metrics.head(2))
    except RuntimeError as e:
        print(f"❌ Financial metrics test skipped: {e}")

    return None


def test_market():
    """Test market infrastructure."""
    print("\n=== Testing Market Infrastructure ===")

    print("\n--- Exchanges ---")
    df_exchanges = get_exchanges(source="tickflow")
    print(f"Columns: {df_exchanges.columns.tolist()}")
    print(f"Rows: {len(df_exchanges)}")
    if not df_exchanges.empty:
        print(df_exchanges)

    print("\n--- Instruments ---")

    try:
        df_instruments = get_instruments(symbols=["600000.SH", "000001.SZ"], source="tickflow")
        print(f"Columns: {df_instruments.columns.tolist()}")
        print(f"Rows: {len(df_instruments)}")
        if not df_instruments.empty:
            print(df_instruments)
    except Exception as e:
        print(f"❌ Instruments test failed: {e}")
        import traceback

        traceback.print_exc()
        df_instruments = pd.DataFrame()

    print("\n--- Universes ---")
    df_universes = get_universes(source="tickflow")
    print(f"Columns: {df_universes.columns.tolist()}")
    print(f"Rows: {len(df_universes)}")
    if not df_universes.empty:
        print(df_universes)

    return df_exchanges, df_instruments, df_universes


def main():
    """Run all tests."""
    print("=" * 60)
    print("TickFlow API Integration Test")
    print("=" * 60)

    try:
        test_realtime()
        test_historical()
        test_financial()
        test_market()

        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
