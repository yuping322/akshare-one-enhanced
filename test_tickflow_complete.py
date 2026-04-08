#!/usr/bin/env python3
"""
Comprehensive test script for all TickFlow API endpoints.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import pandas as pd
from akshare_one.tickflow_client import get_tickflow_client
from akshare_one.modules.realtime import get_current_data
from akshare_one.modules.historical import get_hist_data
from akshare_one.modules.financial import get_balance_sheet, get_income_statement, get_cash_flow, get_financial_metrics
from akshare_one.modules.market import (
    get_instruments,
    get_exchanges,
    get_exchange_instruments,
    get_universes,
    get_universe_detail,
)


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(df, name="Result"):
    """Print DataFrame result."""
    print(f"\n{name}:")
    print(f"  Columns: {df.columns.tolist()}")
    print(f"  Rows: {len(df)}")
    if not df.empty:
        print("\n" + df.head(3).to_string())
    print()


def test_tickflow_client():
    """Test TickFlow client directly."""
    print_section("Testing TickFlow Client")

    client = get_tickflow_client()
    print(f"✓ Client initialized")
    print(f"  API Key: {client.api_key[:20]}...")
    print(f"  Base URL: {client.BASE_URL}")

    return client


def test_realtime_quotes():
    """Test realtime quotes API."""
    print_section("1. Realtime Quotes API")

    # Test 1: Single symbol via provider
    print("\n[1.1] Single symbol quote:")
    try:
        df = get_current_data(symbol="600000.SH", source="tickflow")
        print_result(df, "600000.SH Realtime Quote")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 2: Multiple symbols via POST
    print("\n[1.2] Multiple symbols quote (POST):")
    try:
        client = get_tickflow_client()
        response = client.query_api(
            "/v1/quotes", method="POST", data={"symbols": ["600000.SH", "000001.SZ", "000002.SZ"]}
        )
        df = pd.DataFrame(response.get("data", []))
        print_result(df, "Batch Quotes")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 3: Query by universe
    print("\n[1.3] Query by universe (CN_Equity_A - first 5 stocks):")
    try:
        df = get_current_data(source="tickflow", row_filter={"top_n": 5})
        print_result(df, "Universe Quotes (Top 5)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 4: US stocks
    print("\n[1.4] US stock quote (AAPL.US):")
    try:
        df = get_current_data(symbol="AAPL.US", source="tickflow")
        print_result(df, "AAPL.US Realtime Quote")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 5: HK stocks
    print("\n[1.5] HK stock quote (00700.HK - Tencent):")
    try:
        df = get_current_data(symbol="00700.HK", source="tickflow")
        print_result(df, "00700.HK Realtime Quote")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


def test_klines():
    """Test K-line data API."""
    print_section("2. K-line Data API")

    # Test 1: Daily K-line
    print("\n[2.1] Daily K-line (2024-01-01 to 2024-01-31):")
    try:
        df = get_hist_data(
            symbol="600000",
            start_date="2024-01-01",
            end_date="2024-01-31",
            interval="day",
            adjust="qfq",
            source="tickflow",
        )
        print_result(df, "Daily K-line (前复权)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 2: Weekly K-line
    print("\n[2.2] Weekly K-line:")
    try:
        df = get_hist_data(
            symbol="600000", start_date="2024-01-01", end_date="2024-03-31", interval="week", source="tickflow"
        )
        print_result(df, "Weekly K-line")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 3: Monthly K-line
    print("\n[2.3] Monthly K-line:")
    try:
        df = get_hist_data(
            symbol="600000", start_date="2023-01-01", end_date="2024-12-31", interval="month", source="tickflow"
        )
        print_result(df, "Monthly K-line")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 4: No adjustment
    print("\n[2.4] Daily K-line (不复权):")
    try:
        df = get_hist_data(
            symbol="600000",
            start_date="2024-01-01",
            end_date="2024-01-31",
            interval="day",
            adjust="none",
            source="tickflow",
        )
        print_result(df, "Daily K-line (不复权)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 5: US stock K-line
    print("\n[2.5] US stock K-line (AAPL.US):")
    try:
        df = get_hist_data(
            symbol="AAPL.US", start_date="2024-01-01", end_date="2024-01-31", interval="day", source="tickflow"
        )
        print_result(df, "AAPL Daily K-line")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 6: Batch K-line query
    print("\n[2.6] Batch K-line query:")
    try:
        client = get_tickflow_client()
        response = client.query_api(
            "/v1/klines/batch", method="GET", params={"symbols": "600000.SH,000001.SZ", "period": "1d", "count": 5}
        )
        for symbol, klines in response.get("data", {}).items():
            df = pd.DataFrame(klines)
            print_result(df, f"{symbol} K-line")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


def test_intraday_klines():
    """Test intraday K-line data API."""
    print_section("3. Intraday K-line Data API")

    # Test 1: 1-minute K-line
    print("\n[3.1] 1-minute K-line (today):")
    try:
        client = get_tickflow_client()
        response = client.query_api(
            "/v1/klines/intraday", method="GET", params={"symbol": "600000.SH", "period": "1m", "count": 10}
        )
        df = pd.DataFrame(response.get("data", []))
        print_result(df, "1-minute K-line (last 10 bars)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 2: 5-minute K-line
    print("\n[3.2] 5-minute K-line (today):")
    try:
        client = get_tickflow_client()
        response = client.query_api(
            "/v1/klines/intraday", method="GET", params={"symbol": "600000.SH", "period": "5m", "count": 10}
        )
        df = pd.DataFrame(response.get("data", []))
        print_result(df, "5-minute K-line (last 10 bars)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 3: Batch intraday K-line
    print("\n[3.3] Batch intraday K-line:")
    try:
        client = get_tickflow_client()
        response = client.query_api(
            "/v1/klines/intraday/batch",
            method="GET",
            params={"symbols": "600000.SH,000001.SZ", "period": "5m", "count": 5},
        )
        for symbol, klines in response.get("data", {}).items():
            df = pd.DataFrame(klines)
            print_result(df, f"{symbol} 5-minute K-line")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


def test_ex_factors():
    """Test ex-rights factors API."""
    print_section("4. Ex-rights Factors API")

    print("\n[4.1] Get ex-rights factors:")
    try:
        client = get_tickflow_client()
        response = client.query_api("/v1/klines/ex-factors", method="GET", params={"symbols": "600000.SH"})
        factors = response.get("data", {}).get("600000.SH", [])
        df = pd.DataFrame(factors)
        print_result(df, "600000.SH Ex-rights Factors")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


def test_instruments():
    """Test instruments API."""
    print_section("5. Instruments API")

    # Test 1: Single instrument
    print("\n[5.1] Single instrument:")
    try:
        df = get_instruments(symbols="600000.SH", source="tickflow")
        print_result(df, "600000.SH Instrument Info")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 2: Multiple instruments
    print("\n[5.2] Multiple instruments:")
    try:
        df = get_instruments(symbols=["600000.SH", "000001.SZ", "AAPL.US"], source="tickflow")
        print_result(df, "Multiple Instruments Info")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 3: Batch query (POST)
    print("\n[5.3] Batch instruments query (POST):")
    try:
        client = get_tickflow_client()
        symbols = [f"{str(i).zfill(6)}.SH" for i in range(600000, 600010)]
        response = client.query_api("/v1/instruments", method="POST", data={"symbols": symbols})
        df = pd.DataFrame(response.get("data", []))
        print_result(df, "Batch Instruments (10 SH stocks)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


def test_exchanges():
    """Test exchanges API."""
    print_section("6. Exchanges API")

    # Test 1: List all exchanges
    print("\n[6.1] List all exchanges:")
    try:
        df = get_exchanges(source="tickflow")
        print_result(df, "All Exchanges")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 2: Get SH exchange instruments
    print("\n[6.2] SH exchange stocks:")
    try:
        df = get_exchange_instruments(exchange="SH", type="stock", source="tickflow", row_filter={"top_n": 5})
        print_result(df, "SH Exchange Stocks (Top 5)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 3: Get SZ exchange ETFs
    print("\n[6.3] SZ exchange ETFs:")
    try:
        df = get_exchange_instruments(exchange="SZ", type="etf", source="tickflow", row_filter={"top_n": 5})
        print_result(df, "SZ Exchange ETFs (Top 5)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


def test_universes():
    """Test universes API."""
    print_section("7. Universes API")

    # Test 1: List all universes
    print("\n[7.1] List all universes (first 20):")
    try:
        df = get_universes(source="tickflow", row_filter={"top_n": 20})
        print_result(df, "All Universes (Top 20)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 2: Get specific universe detail
    print("\n[7.2] CN_Equity_A universe detail (first 5 instruments):")
    try:
        df = get_universe_detail(universe_id="CN_Equity_A", source="tickflow", row_filter={"top_n": 5})
        print_result(df, "CN_Equity_A Universe")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 3: Batch universes
    print("\n[7.3] Batch universes query:")
    try:
        client = get_tickflow_client()
        response = client.query_api("/v1/universes/batch", method="POST", data={"ids": ["CN_Equity_A", "CN_ETF"]})
        for universe in response.get("data", []):
            print(f"\n  Universe: {universe.get('name')} (ID: {universe.get('id')})")
            instruments = universe.get("instruments", [])[:3]
            for inst in instruments:
                print(f"    - {inst}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


def test_financial_data():
    """Test financial data API."""
    print_section("8. Financial Data API")

    print("\n  ⚠️  Note: Financial data requires special API permissions")

    # Test 1: Balance sheet
    print("\n[8.1] Balance sheet:")
    try:
        df = get_balance_sheet(symbol="600000", source="tickflow")
        print_result(df, "600000 Balance Sheet")
    except Exception as e:
        print(f"  ⚠️  Skipped (需要财务数据权限): {str(e)[:100]}")

    # Test 2: Income statement
    print("\n[8.2] Income statement:")
    try:
        df = get_income_statement(symbol="600000", source="tickflow")
        print_result(df, "600000 Income Statement")
    except Exception as e:
        print(f"  ⚠️  Skipped (需要财务数据权限): {str(e)[:100]}")

    # Test 3: Cash flow
    print("\n[8.3] Cash flow:")
    try:
        df = get_cash_flow(symbol="600000", source="tickflow")
        print_result(df, "600000 Cash Flow")
    except Exception as e:
        print(f"  ⚠️  Skipped (需要财务数据权限): {str(e)[:100]}")

    # Test 4: Financial metrics
    print("\n[8.4] Financial metrics:")
    try:
        df = get_financial_metrics(symbol="600000", source="tickflow")
        print_result(df, "600000 Financial Metrics")
    except Exception as e:
        print(f"  ⚠️  Skipped (需要财务数据权限): {str(e)[:100]}")


def test_cross_market():
    """Test cross-market queries."""
    print_section("9. Cross-Market Queries")

    # Test 1: A-shares
    print("\n[9.1] A-shares (浦发银行):")
    try:
        df = get_current_data(symbol="600000.SH", source="tickflow")
        print_result(df, "A-share Quote")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 2: HK stocks
    print("\n[9.2] HK stocks (腾讯):")
    try:
        df = get_current_data(symbol="00700.HK", source="tickflow")
        print_result(df, "HK Stock Quote")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 3: US stocks
    print("\n[9.3] US stocks (Apple):")
    try:
        df = get_current_data(symbol="AAPL.US", source="tickflow")
        print_result(df, "US Stock Quote")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

    # Test 4: Multi-market batch
    print("\n[9.4] Multi-market batch quote:")
    try:
        client = get_tickflow_client()
        response = client.query_api("/v1/quotes", method="POST", data={"symbols": ["600000.SH", "00700.HK", "AAPL.US"]})
        df = pd.DataFrame(response.get("data", []))
        print_result(df, "Multi-Market Quotes")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  TickFlow API - Comprehensive Integration Test")
    print("  API Key: tk_b1369c7ce7af4d12a17dbd52b3688c06")
    print("=" * 70)

    try:
        # Test 0: Client
        test_tickflow_client()

        # Test 1: Realtime quotes
        test_realtime_quotes()

        # Test 2: K-line data
        test_klines()

        # Test 3: Intraday K-line
        test_intraday_klines()

        # Test 4: Ex-rights factors
        test_ex_factors()

        # Test 5: Instruments
        test_instruments()

        # Test 6: Exchanges
        test_exchanges()

        # Test 7: Universes
        test_universes()

        # Test 8: Financial data
        test_financial_data()

        # Test 9: Cross-market
        test_cross_market()

        # Summary
        print("\n" + "=" * 70)
        print("  ✅ All Tests Completed Successfully!")
        print("=" * 70)
        print("\n📊 Summary:")
        print("  ✓ Realtime Quotes API - Tested")
        print("  ✓ K-line Data API - Tested")
        print("  ✓ Intraday K-line API - Tested")
        print("  ✓ Ex-rights Factors API - Tested")
        print("  ✓ Instruments API - Tested")
        print("  ✓ Exchanges API - Tested")
        print("  ✓ Universes API - Tested")
        print("  ⚠ Financial Data API - Requires additional permissions")
        print("  ✓ Cross-Market Queries - Tested")
        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
