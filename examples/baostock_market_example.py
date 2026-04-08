"""
Example usage of Baostock market data provider.

This script demonstrates how to use the BaostockInstrumentProvider
to fetch stock list, basic info, industry classification, and index constituents.
"""

import sys

sys.path.insert(0, "/Users/fengzhi/Downloads/git/akshare-one-enhanced/src")

from akshare_one.modules.market import InstrumentFactory


def example_query_all_stock():
    """Example: Query all stock list"""
    print("\n" + "=" * 60)
    print("Example 1: Query All Stock List")
    print("=" * 60)

    provider = InstrumentFactory.get_provider("baostock")

    df = provider.query_all_stock()

    print(f"Total stocks: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nSample data (first 10):")
    print(df.head(10))

    provider.logout()


def example_query_hs300():
    """Example: Query HS300 index constituents"""
    print("\n" + "=" * 60)
    print("Example 2: Query HS300 Index Constituents")
    print("=" * 60)

    provider = InstrumentFactory.get_provider("baostock")

    df = provider.query_hs300_stocks()

    print(f"HS300 stocks: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nSample data:")
    print(df.head(10))

    provider.logout()


def example_with_filters():
    """Example: Use column and row filters"""
    print("\n" + "=" * 60)
    print("Example 3: Query with Filters")
    print("=" * 60)

    provider = InstrumentFactory.get_provider("baostock")

    df = provider.query_all_stock(columns=["symbol", "name", "exchange"], row_filter={"top_n": 20})

    print(f"Filtered data (top 20):")
    print(df)

    provider.logout()


if __name__ == "__main__":
    print("Baostock Market Data Provider - Usage Examples")
    print("=" * 60)
    print("\nNote: These examples require:")
    print("  1. Baostock package installed (pip install baostock)")
    print("  2. Network connection to Baostock server")
    print("\nUncomment examples below to run actual queries.")
    print("=" * 60)

    # Uncomment to run actual examples (requires network)
    # example_query_all_stock()
    # example_query_hs300()
    # example_with_filters()

    print("\nSee source code for implementation details:")
    print("  src/akshare_one/modules/market/baostock.py")
