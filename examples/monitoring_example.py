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
from akshare_one import get_realtime_data, get_hist_data


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
        # Fetch realtime data
        realtime_df = get_realtime_data(source="eastmoney", symbol="600000")
        print(f"   Fetched {len(realtime_df)} realtime records")

        # Fetch historical data
        hist_df = get_hist_data(symbol="600000", start_date="2026-01-01", end_date="2026-02-18", source="eastmoney")
        print(f"   Fetched {len(hist_df)} historical records")

    except Exception as e:
        logger.error(f"Failed to fetch data: {e}", exc_info=True)

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
        # This will fail
        get_realtime_data(source="invalid_source")
    except Exception as e:
        logger.error(f"Expected error: {e}")

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
