"""
Example usage of efinance wrapper module
"""

from src.efinance_wrapper import efinance_api
import pandas as pd


def example_stock_usage():
    """Stock API usage examples"""

    # 1. Get stock historical data
    stock_data = efinance_api.stock.get_quote_history(
        "600519",  # Stock code
        beg="20240101",  # Start date
        end="20240408",  # End date
        klt=101,  # Daily frequency
        fqt=1,  # Forward adjustment
    )
    print("Stock historical data:")
    print(stock_data.head())

    # 2. Get realtime quotes
    realtime_quotes = efinance_api.stock.get_realtime_quotes()
    print("\nRealtime quotes:")
    print(realtime_quotes.head())

    # 3. Get stock basic info
    stock_info = efinance_api.stock.get_base_info("600519")
    print("\nStock basic info:")
    print(stock_info)

    # 4. Get dragon-tiger list
    billboard = efinance_api.stock.get_daily_billboard(start_date="2024-03-01", end_date="2024-03-31")
    print("\nDragon-tiger list:")
    print(billboard.head())

    # 5. Get fund flow data
    history_bill = efinance_api.stock.get_history_bill("300750")
    print("\nHistorical fund flow:")
    print(history_bill.head())

    today_bill = efinance_api.stock.get_today_bill("300750")
    print("\nToday's fund flow:")
    print(today_bill.head())


def example_fund_usage():
    """Fund API usage examples"""

    # 1. Get fund historical net value
    fund_history = efinance_api.fund.get_quote_history("161725")
    print("Fund historical net value:")
    print(fund_history.head())

    # 2. Get fund basic info
    fund_info = efinance_api.fund.get_base_info("161725")
    print("\nFund basic info:")
    print(fund_info)

    # 3. Get fund holdings
    holdings = efinance_api.fund.get_invest_position("161725")
    print("\nFund holdings:")
    print(holdings)

    # 4. Get fund industry distribution
    industry = efinance_api.fund.get_industry_distribution("161725")
    print("\nIndustry distribution:")
    print(industry)

    # 5. Get multiple funds data
    multi_fund_data = efinance_api.fund.get_quote_history_multi(["161725", "005827"])
    print("\nMultiple funds data:")
    for code, data in multi_fund_data.items():
        print(f"\n{code}:")
        print(data.head())


def example_bond_usage():
    """Bond API usage examples"""

    # 1. Get bond historical data
    bond_history = efinance_api.bond.get_quote_history("123111")
    print("Bond historical data:")
    print(bond_history.head())

    # 2. Get realtime bond quotes
    realtime_bonds = efinance_api.bond.get_realtime_quotes()
    print("\nRealtime bond quotes:")
    print(realtime_bonds.head())

    # 3. Get all bonds info
    all_bonds = efinance_api.bond.get_all_base_info()
    print("\nAll bonds info:")
    print(all_bonds.head())

    # 4. Get specific bond info
    bond_info = efinance_api.bond.get_base_info("123111")
    print("\nSpecific bond info:")
    print(bond_info)


def example_futures_usage():
    """Futures API usage examples"""

    # 1. Get futures base info
    futures_info = efinance_api.futures.get_futures_base_info()
    print("Futures base info:")
    print(futures_info.head())

    # 2. Get realtime futures quotes
    realtime_futures = efinance_api.futures.get_realtime_quotes()
    print("\nRealtime futures quotes:")
    print(realtime_futures.head())

    # 3. Get futures historical data (need quote_id)
    # quote_id format: e.g. '115.ZCM' for Zhengzhou Commodity Exchange
    futures_history = efinance_api.futures.get_quote_history("115.ZCM")
    print("\nFutures historical data:")
    print(futures_history.head())


def batch_query_example():
    """Batch query multiple stocks"""

    stock_codes = ["600519", "000001", "000002"]

    # Get batch historical data
    batch_data = efinance_api.stock.get_quote_history(stock_codes, beg="20240101", end="20240408")

    # If single code, returns DataFrame
    # If multiple codes, returns Dict[str, DataFrame]
    if isinstance(batch_data, dict):
        for code, data in batch_data.items():
            print(f"\n{code} historical data:")
            print(data.head())
    else:
        print("\nBatch historical data:")
        print(batch_data.head())


def minute_level_data_example():
    """Get minute level data"""

    # 5-minute data (klt=5)
    min5_data = efinance_api.stock.get_quote_history("600519", klt=5, beg="20240401", end="20240408")
    print("5-minute data:")
    print(min5_data.head())

    # 15-minute data (klt=15)
    min15_data = efinance_api.stock.get_quote_history("600519", klt=15, beg="20240401", end="20240408")
    print("\n15-minute data:")
    print(min15_data.head())


if __name__ == "__main__":
    print("=== Efinance Wrapper Usage Examples ===\n")

    # Uncomment to run specific examples
    # Note: Network connection is required to fetch data from eastmoney.com

    # example_stock_usage()
    # example_fund_usage()
    # example_bond_usage()
    # example_futures_usage()
    # batch_query_example()
    # minute_level_data_example()

    print("\nPlease uncomment specific example functions to run.")
    print("Note: Ensure network connectivity to eastmoney.com")
