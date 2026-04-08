"""
Baostock Macro Economic Data Usage Examples

This example demonstrates how to use the Baostock macro provider
to fetch Chinese macro economic data including deposit rates, loan rates,
reserve ratios, and money supply data.
"""

import sys

sys.path.insert(0, "../src")

from akshare_one.modules.macro import (
    MacroFactory,
    get_deposit_rate_data,
    get_loan_rate_data,
    get_required_reserve_ratio_data,
    get_money_supply_data_month,
    get_money_supply_data_year,
)
from akshare_one.modules.macro.baostock import BaostockMacroProvider


def example_using_provider():
    """Example using the provider directly"""
    provider = MacroFactory.get_provider("baostock")

    print("=== Deposit Rate Data ===")
    df = provider.get_deposit_rate_data("2024-01-01", "2024-12-31")
    print(f"Rows: {len(df)}, Columns: {list(df.columns)}")
    if not df.empty:
        print(df.head(3))

    print("\n=== Loan Rate Data ===")
    df = provider.get_loan_rate_data("2024-01-01", "2024-12-31")
    print(f"Rows: {len(df)}, Columns: {list(df.columns)}")
    if not df.empty:
        print(df.head(3))

    print("\n=== Reserve Ratio Data ===")
    df = provider.get_required_reserve_ratio_data("2024-01-01", "2024-12-31")
    print(f"Rows: {len(df)}, Columns: {list(df.columns)}")
    if not df.empty:
        print(df.head(3))

    print("\n=== Monthly Money Supply ===")
    df = provider.get_money_supply_data_month("2024-01-01", "2024-12-31")
    print(f"Rows: {len(df)}, Columns: {list(df.columns)}")
    if not df.empty:
        print(df.head(3))

    print("\n=== Yearly Money Supply ===")
    df = provider.get_money_supply_data_year("2020-01-01", "2024-12-31")
    print(f"Rows: {len(df)}, Columns: {list(df.columns)}")
    if not df.empty:
        print(df.head(5))

    BaostockMacroProvider.logout()


def example_using_api_functions():
    """Example using the convenience API functions"""
    print("=== Using API Functions ===")

    print("\n1. Deposit Rate Data:")
    df = get_deposit_rate_data(source="baostock")
    print(f"Rows: {len(df)}")

    print("\n2. Loan Rate Data:")
    df = get_loan_rate_data(source="baostock")
    print(f"Rows: {len(df)}")

    print("\n3. Reserve Ratio Data:")
    df = get_required_reserve_ratio_data(source="baostock")
    print(f"Rows: {len(df)}")

    print("\n4. Monthly Money Supply:")
    df = get_money_supply_data_month(source="baostock")
    print(f"Rows: {len(df)}")

    print("\n5. Yearly Money Supply:")
    df = get_money_supply_data_year(source="baostock")
    print(f"Rows: {len(df)}")


def example_with_filters():
    """Example with column and row filters"""
    print("=== With Filters ===")

    provider = MacroFactory.get_provider("baostock")

    print("\n1. Only specific columns:")
    df = provider.get_deposit_rate_data("2024-01-01", "2024-12-31", columns=["date", "deposit_rate"])
    print(f"Columns: {list(df.columns)}")

    print("\n2. Filter by rate type (using row_filter in API call):")
    df = get_deposit_rate_data(source="baostock", row_filter={"query": "deposit_rate_type == '活期存款'", "top_n": 5})
    print(f"Rows: {len(df)}")

    BaostockMacroProvider.logout()


if __name__ == "__main__":
    print("Baostock Macro Economic Data Examples")
    print("=" * 50)

    example_using_provider()
    print("\n" + "=" * 50)
    example_using_api_functions()
    print("\n" + "=" * 50)
    example_with_filters()
