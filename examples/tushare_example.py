"""
Example: Using Tushare Pro as a data source.

This example demonstrates how to configure and use Tushare Pro API
as a data source in akshare-one.
"""

from akshare_one.tushare_config import set_tushare_api_key
from akshare_one.modules.financial import FinancialDataFactory
from akshare_one.modules.historical import HistoricalDataFactory


def main():
    # Step 1: Set your Tushare API key
    # Replace with your actual API key from https://tushare.pro
    API_KEY = "4b33969578cd316eb788f60605711745360834aded78ac672f2a0537"
    set_tushare_api_key(API_KEY)

    print("=== Tushare Integration Example ===")
    print("\n1. Check available sources:")
    print(f"   Financial sources: {FinancialDataFactory.list_sources()}")
    print(f"   Historical sources: {HistoricalDataFactory.list_sources()}")

    # Step 2: Get financial data from Tushare
    print("\n2. Get financial data from Tushare:")
    symbol = "600000"  # 浦发银行

    provider = FinancialDataFactory.get_provider("tushare", symbol=symbol)

    # Get balance sheet
    print(f"\n   Getting balance sheet for {symbol}...")
    balance_df = provider.get_balance_sheet()
    print(f"   Found {len(balance_df)} records")
    if not balance_df.empty:
        print(f"   Columns: {balance_df.columns.tolist()}")
        print(f"   Latest record:\n{balance_df.head(1)}")

    # Get income statement
    print(f"\n   Getting income statement for {symbol}...")
    income_df = provider.get_income_statement()
    print(f"   Found {len(income_df)} records")
    if not income_df.empty:
        print(f"   Columns: {income_df.columns.tolist()}")
        print(f"   Latest record:\n{income_df.head(1)}")

    # Get cash flow
    print(f"\n   Getting cash flow for {symbol}...")
    cashflow_df = provider.get_cash_flow()
    print(f"   Found {len(cashflow_df)} records")
    if not cashflow_df.empty:
        print(f"   Columns: {cashflow_df.columns.tolist()}")
        print(f"   Latest record:\n{cashflow_df.head(1)}")

    # Get financial metrics
    print(f"\n   Getting financial metrics for {symbol}...")
    metrics_df = provider.get_financial_metrics()
    print(f"   Found {len(metrics_df)} records")
    if not metrics_df.empty:
        print(f"   Columns: {metrics_df.columns.tolist()}")
        print(f"   Latest record:\n{metrics_df.head(1)}")

    # Step 3: Get historical data from Tushare
    print("\n3. Get historical price data from Tushare:")
    hist_provider = HistoricalDataFactory.get_provider(
        "tushare", symbol=symbol, interval="day", start_date="2024-01-01", end_date="2024-01-31"
    )

    hist_df = hist_provider.get_hist_data()
    print(f"   Found {len(hist_df)} daily records")
    if not hist_df.empty:
        print(f"   Columns: {hist_df.columns.tolist()}")
        print(f"   Sample data:\n{hist_df.head()}")

    # Step 4: Use multi-source routing (try Tushare first, fallback to others)
    print("\n4. Use multi-source routing:")
    print("   Creating router with Tushare and other sources...")

    router = FinancialDataFactory.create_router(sources=["tushare", "sina", "eastmoney"], symbol=symbol)

    result_df = router.execute("get_balance_sheet")
    print(f"   Router returned {len(result_df)} records from combined sources")

    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
