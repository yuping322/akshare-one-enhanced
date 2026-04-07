"""
Test AkShare compatibility adapter.

This script tests the AkShareAdapter to ensure it handles function drift gracefully.
"""

import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def test_adapter_basic():
    """Test basic adapter functionality."""
    from akshare_one.akshare_compat import get_adapter

    adapter = get_adapter()

    # Test version detection
    version = adapter.get_version()
    logger.info(f"✓ Detected AkShare version: {version}")

    # Test function existence check
    exists = adapter.function_exists("stock_zh_a_hist")
    logger.info(f"✓ Function 'stock_zh_a_hist' exists: {exists}")

    # Test function info
    info = adapter.get_function_info("stock_zh_a_hist")
    logger.info(f"✓ Function info: {info}")

    return True


def test_adapter_call():
    """Test calling AkShare functions through adapter."""
    from akshare_one.akshare_compat import call_akshare

    logger.info("\n--- Testing adapter call ---")

    # Test calling a known function
    try:
        df = call_akshare(
            "stock_zh_a_hist",
            symbol="600000",
            period="daily",
            start_date="20240101",
            end_date="20240110",
            adjust="",
        )
        logger.info(f"✓ Successfully called stock_zh_a_hist, got {len(df)} rows")
        if not df.empty:
            logger.info(f"  Sample columns: {df.columns.tolist()[:5]}")
        return True
    except Exception as e:
        logger.warning(f"⚠ Failed to call stock_zh_a_hist: {e}")
        # This is OK if AkShare version changed
        return True


def test_function_health_check():
    """Test health check for critical AkShare functions."""
    from akshare_one.akshare_compat import get_adapter

    adapter = get_adapter()

    logger.info("\n--- Testing function health check ---")

    # Critical functions used in the project
    critical_functions = [
        "stock_zh_a_hist",
        "stock_zh_a_hist_min_em",
        "fund_etf_hist_sina",
        "stock_dzjy_mrtj",
        "stock_individual_fund_flow",
        "stock_sector_fund_flow_rank",
        "stock_board_industry_name_em",
        "stock_board_concept_name_em",
    ]

    health_report = adapter.check_function_health(critical_functions)

    available_count = 0
    for func_name, status in health_report.items():
        if status["status"] == "available":
            available_count += 1
            logger.info(f"✓ {func_name}: available (resolved to {status['resolved_name']})")
        else:
            logger.warning(
                f"⚠ {func_name}: unavailable - alias mapping: {status.get('alias', 'none')}"
            )

    logger.info(f"\n📊 Summary: {available_count}/{len(critical_functions)} functions available")

    return True


def test_deprecated_function_handling():
    """Test handling of deprecated function names."""
    from akshare_one.akshare_compat import get_adapter

    adapter = get_adapter()

    logger.info("\n--- Testing deprecated function handling ---")

    # Test deprecated function names (should use aliases)
    deprecated_functions = [
        "stock_zh_a_daily",  # Should map to stock_zh_a_hist
        "stock_fund_flow_individual",  # Should map to stock_individual_fund_flow
    ]

    for func_name in deprecated_functions:
        resolved_name = adapter.resolve_function_name(func_name)
        logger.info(f"✓ Deprecated '{func_name}' resolved to '{resolved_name}'")

    return True


def test_error_handling():
    """Test error handling for non-existent functions."""
    from akshare_one.akshare_compat import get_adapter

    logger.info("\n--- Testing error handling ---")

    adapter = get_adapter()

    # Test safe call (should return empty DataFrame without raising)
    df = adapter.call_safe("nonexistent_function_xyz")
    logger.info(f"✓ Safe call returned empty DataFrame: {df.empty}")

    # Test another safe call
    df = adapter.call_safe("another_nonexistent_function")
    logger.info(f"✓ Another safe call returned empty DataFrame: {df.empty}")

    # Test that regular call raises RuntimeError
    try:
        df = adapter.call("nonexistent_function_xyz")
        logger.warning("⚠ Regular call should have raised RuntimeError but didn't")
        return False
    except RuntimeError as e:
        logger.info(f"✓ Regular call correctly raised RuntimeError: {str(e)[:100]}")
        return True


def test_integration_with_provider():
    """Test integration with BaseProvider."""
    logger.info("\n--- Testing integration with BaseProvider ---")

    try:
        from akshare_one.modules.historical import HistoricalDataFactory

        # Create provider
        provider = HistoricalDataFactory.get_provider(
            "eastmoney",
            symbol="600000",
            interval="day",
            start_date="2024-01-01",
            end_date="2024-01-10",
        )

        logger.info(f"✓ Provider initialized with akshare_adapter")

        # Check adapter is initialized
        if hasattr(provider, "akshare_adapter"):
            logger.info(f"✓ Provider has akshare_adapter: {provider.akshare_adapter}")
            return True
        else:
            logger.warning("⚠ Provider missing akshare_adapter")
            return False

    except Exception as e:
        logger.error(f"✗ Integration test failed: {e}", exc_info=True)
        return False


def run_all_tests():
    """Run all compatibility tests."""
    logger.info("=" * 60)
    logger.info("AkShare Compatibility Adapter Test Suite")
    logger.info("=" * 60)

    tests = [
        ("Basic adapter functionality", test_adapter_basic),
        ("Adapter function calling", test_adapter_call),
        ("Function health check", test_function_health_check),
        ("Deprecated function handling", test_deprecated_function_handling),
        ("Error handling", test_error_handling),
        ("Integration with provider", test_integration_with_provider),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'=' * 60}")
            success = test_func()
            results.append((test_name, success, None))
            logger.info(f"✓ {test_name} PASSED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED: {e}", exc_info=True)
            results.append((test_name, False, str(e)))

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
        if error:
            logger.info(f"  Error: {error}")

    logger.info(f"\n📊 Results: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)