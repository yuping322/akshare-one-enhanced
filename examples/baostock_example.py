#!/usr/bin/env python
"""
Baostock data source usage example.

This example demonstrates how to use Baostock as a data source
for historical stock data.
"""

import sys

sys.path.insert(0, "src")

from akshare_one.modules.historical import HistoricalDataFactory


def main():
    """Example usage of Baostock historical data provider."""

    # Example 1: Basic usage with symbol in baostock format
    print("Example 1: Basic usage (sh.600000)")
    provider1 = HistoricalDataFactory.get_provider(
        "baostock",
        symbol="sh.600000",  # Baostock format: sh/sz + symbol
        interval="day",
        start_date="2024-01-01",
        end_date="2024-01-10",
    )
    df1 = provider1.get_hist_data()
    print(f"Data fetched: {len(df1)} rows")
    print(df1.head())
    print()

    # Example 2: Using symbol without prefix (auto-conversion)
    print("Example 2: Auto symbol conversion (600000)")
    from akshare_one.modules.historical.baostock import BaostockHistorical

    provider2 = BaostockHistorical(
        symbol="600000",  # Will be converted to sh.600000
        interval="day",
        start_date="2024-01-01",
        end_date="2024-01-10",
    )
    df2 = provider2.get_hist_data()
    print(f"Data fetched: {len(df2)} rows")
    print(df2.head())
    print()

    # Example 3: Weekly data
    print("Example 3: Weekly data")
    provider3 = HistoricalDataFactory.get_provider(
        "baostock",
        symbol="sz.000001",  # 平安银行
        interval="week",
        start_date="2024-01-01",
        end_date="2024-03-31",
    )
    df3 = provider3.get_hist_data()
    print(f"Weekly data fetched: {len(df3)} rows")
    print(df3.head())
    print()

    # Example 4: Price adjustment (前复权)
    print("Example 4: Price adjustment (qfq)")
    provider4 = HistoricalDataFactory.get_provider(
        "baostock",
        symbol="sh.600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-01-10",
        adjust="qfq",  # 前复权
    )
    df4 = provider4.get_hist_data()
    print(f"Adjusted data fetched: {len(df4)} rows")
    print(df4.head())
    print()

    # Example 5: List available sources
    print("Example 5: Available sources")
    sources = HistoricalDataFactory.list_sources()
    print(f"Available historical data sources: {sources}")
    print()


if __name__ == "__main__":
    main()
