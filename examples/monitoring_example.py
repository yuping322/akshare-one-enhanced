"""
Monitoring and observability example for akshare-one.

This example demonstrates:
1. Setting up structured logging
2. Using health checks
3. Collecting and viewing statistics
"""

from akshare_one.logging_config import setup_logging, get_logger
from akshare_one.health import create_default_health_checker
from akshare_one.metrics import get_stats_collector
from akshare_one import get_hist_data, get_realtime_data
import pandas as pd


def main():
    """Main example function."""

    print("=" * 60)
    print("AKSHARE-ONE MONITORING EXAMPLE")
    print("=" * 60)

    # 1. Setup logging
    print("\n1. Setting up structured logging...")
    setup_logging(log_level="INFO", log_dir="logs", enable_file=True, enable_console=True, json_format=True)
    logger = get_logger(__name__)
    logger.info("Monitoring example started")

    # 2. Fetch some data (this will be logged automatically)
    print("\n2. Fetching data (this will be logged)...")

    try:
        # Fetch realtime data (skip - eastmoney unavailable)
        realtime_df = pd.DataFrame()
        print("   Realtime data source unavailable, using empty DataFrame")

        # Fetch historical data using sina
        hist_df = get_hist_data(symbol="600000", start_date="2026-01-01", end_date="2026-02-18", source="sina")
        print(f"   Fetched {len(hist_df)} historical records")

    except Exception as e:
        logger.warning(f"Real data fetch failed, using demo data: {e}")
        import pandas as pd

        realtime_df = pd.DataFrame({"symbol": ["600000"], "name": ["浦发银行"], "price": [10.5], "change_pct": [1.25]})
        hist_df = pd.DataFrame(
            {
                "date": pd.date_range("2026-01-01", periods=10),
                "open": [10.0 + i * 0.1 for i in range(10)],
                "high": [10.5 + i * 0.1 for i in range(10)],
                "low": [9.5 + i * 0.1 for i in range(10)],
                "close": [10.2 + i * 0.1 for i in range(10)],
                "volume": [1000000 + i * 10000 for i in range(10)],
            }
        )
        print(f"   Using demo data: {len(realtime_df)} realtime records, {len(hist_df)} historical records")

    # 3. Check health of data sources
    print("\n3. Checking health of data sources...")
    checker = create_default_health_checker()
    results = checker.check_all()

    print("\n   Health Check Results:")
    for source, result in results.items():
        print(f"   {result}")

    # 4. View statistics
    print("\n4. Viewing collected statistics...")
    stats = get_stats_collector()

    print("\n   Statistics Summary:")
    summary = stats.get_summary_text()
    print(summary)

    # 5. Demonstrate error tracking
    print("\n5. Demonstrating error tracking...")
    try:
        # This will fail due to invalid source
        get_realtime_data(source="invalid_source")
    except Exception as e:
        logger.error(f"Expected error (invalid source): {e}")
        logger.info("Error handling demonstration: invalid source correctly caught")

    # 6. Show final statistics
    print("\n6. Final statistics:")
    all_stats = stats.get_all_stats()
    print(f"\n   Total sources tracked: {len(all_stats['sources'])}")

    for source, source_stats in all_stats["sources"].items():
        print(f"\n   {source}:")
        print(f"     Total requests: {source_stats['total_requests']}")
        print(f"     Success rate: {source_stats['success_rate']}")
        print(f"     Avg duration: {source_stats['avg_duration_ms']}")

    print("\n" + "=" * 60)
    print("Example completed. Check logs/akshare_one.log for detailed logs.")
    print("=" * 60)


if __name__ == "__main__":
    main()
