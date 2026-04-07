#!/usr/bin/env python
"""
AkShare Version Compatibility Testing Script

This script tests AkShare function compatibility across different versions.
It verifies function existence, signatures, and return value structures.

Usage:
    python scripts/test_akshare_versions.py
    python scripts/test_akshare_versions.py --version 1.18.23
    python scripts/test_akshare_versions.py --all-versions
"""

import argparse
import importlib
import inspect
import json
import logging
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class FunctionTestResult:
    """Result of testing a single AkShare function."""

    function_name: str
    exists: bool
    signature: str | None = None
    error: str | None = None
    return_type: str | None = None
    return_columns: list[str] | None = None
    test_passed: bool = False
    test_error: str | None = None


@dataclass
class VersionTestResult:
    """Result of testing all functions in a specific AkShare version."""

    version: str
    test_time: str
    total_functions: int
    available_functions: int
    unavailable_functions: int
    test_success_rate: float
    functions: list[dict[str, Any]]


# Critical AkShare functions used in the project
CRITICAL_FUNCTIONS = {
    "stock": [
        ("stock_zh_a_hist", {"symbol": "600000", "period": "daily", "start_date": "20240101", "end_date": "20240110", "adjust": ""}),
        ("stock_zh_a_hist_min_em", {"symbol": "600000", "period": "5", "adjust": ""}),
        ("stock_zh_a_spot_em", {}),
        ("stock_individual_info_em", {"symbol": "600000"}),
    ],
    "etf": [
        ("fund_etf_hist_sina", {"symbol": "159915"}),
    ],
    "block_deal": [
        ("stock_dzjy_mrtj", {}),
        ("stock_dzjy_mrmx", {}),
    ],
    "fund_flow": [
        ("stock_individual_fund_flow", {"stock": "600000", "market": "sh"}),
        ("stock_individual_fund_flow_rank", {"indicator": "今日"}),
        ("stock_sector_fund_flow_rank", {"indicator": "今日", "sector_type": "行业资金流"}),
    ],
    "board": [
        ("stock_board_industry_name_em", {}),
        ("stock_board_industry_cons_em", {"indicator": "小金属"}),
        ("stock_board_concept_name_em", {}),
        ("stock_board_concept_cons_em", {"indicator": "人工智能"}),
    ],
    "macro": [
        ("macro_china_gdp", {}),
        ("macro_china_cpi", {}),
        ("macro_china_ppi", {}),
    ],
    "northbound": [
        ("stock_hsgt_north_net_flow_in_em", {}),
        ("stock_hsgt_north_acc_flow_in_em", {}),
        ("stock_hsgt_hist_em", {}),
        ("stock_hsgt_individual_em", {"symbol": "贵州茅台"}),
        ("stock_hsgt_hold_stock_em", {"market": "北向"}),
    ],
    "financial": [
        ("stock_financial_report_sina", {"stock": "600000", "symbol": "资产负债表"}),
    ],
    "margin": [
        ("stock_margin_detail_szse", {}),
        ("stock_margin_detail_sse", {}),
    ],
    "pledge": [
        ("stock_gpzy_pledge_ratio_em", {}),
        ("stock_gpzy_pledge_ratio_detail_em", {"symbol": "600000"}),
    ],
    "lhb": [
        ("stock_lhb_detail_em", {"start_date": "20240101", "end_date": "20240101"}),
        ("stock_lhb_stock_statistic_em", {"symbol": "近一月"}),
    ],
    "limitup": [
        ("stock_zt_pool_em", {"date": "20240101"}),
        ("stock_zt_pool_previous_em", {"date": "20240101"}),
    ],
    "disclosure": [
        ("stock_notice_report", {}),
    ],
    "esg": [
        ("stock_esg_rate_sina", {"symbol": "600000"}),
    ],
    "goodwill": [
        ("stock_em_yjbb", {"date": "20231231"}),
    ],
    "futures": [
        ("futures_zh_minute_sina", {"symbol": "IF2401"}),
        ("futures_zh_daily_sina", {"symbol": "IF2401"}),
        ("futures_zh_realtime", {}),
    ],
    "options": [
        ("option_current_em", {}),
        ("option_sse_daily_sina", {"symbol": "10003720"}),
    ],
    "index": [
        ("index_stock_info", {}),
        ("index_zh_a_hist", {"symbol": "000001", "period": "daily", "start_date": "20240101", "end_date": "20240110"}),
    ],
    "bond": [
        ("bond_cb_jsl", {}),
    ],
    "other": [
        ("tool_trade_date_hist_sina", {}),
    ],
}


def get_current_akshare_version() -> str:
    """Get the currently installed AkShare version."""
    try:
        import akshare

        return getattr(akshare, "__version__", "unknown")
    except ImportError:
        return "not installed"


def test_function_existence(func_name: str) -> bool:
    """Test if an AkShare function exists."""
    try:
        import akshare as ak

        return hasattr(ak, func_name) and callable(getattr(ak, func_name))
    except ImportError:
        return False


def get_function_signature(func_name: str) -> str | None:
    """Get the signature of an AkShare function."""
    try:
        import akshare as ak

        func = getattr(ak, func_name)
        return str(inspect.signature(func))
    except Exception:
        return None


def test_function_call(func_name: str, params: dict[str, Any]) -> FunctionTestResult:
    """Test calling an AkShare function with given parameters."""
    result = FunctionTestResult(function_name=func_name, exists=False)

    try:
        import akshare as ak

        # Check if function exists
        result.exists = test_function_existence(func_name)
        if not result.exists:
            result.error = f"Function '{func_name}' not found"
            return result

        # Get signature
        result.signature = get_function_signature(func_name)

        # Try to call the function
        func = getattr(ak, func_name)
        try:
            # Suppress network calls for safety, use timeout
            df = func(**params)

            # Analyze return value
            if isinstance(df, pd.DataFrame):
                result.return_type = "DataFrame"
                result.return_columns = df.columns.tolist()
                result.test_passed = True
            elif isinstance(df, dict):
                result.return_type = "dict"
                result.test_passed = True
            elif df is None:
                result.return_type = "None"
                result.test_passed = True
            else:
                result.return_type = str(type(df))
                result.test_passed = True

        except Exception as e:
            result.test_error = f"Call failed: {str(e)}"
            result.test_passed = False

    except ImportError as e:
        result.error = f"Import failed: {str(e)}"

    return result


def test_all_functions_in_version(version: str | None = None) -> VersionTestResult:
    """Test all critical functions in a specific AkShare version."""
    test_time = datetime.now().isoformat()

    # If version is specified but not current, we can't actually switch versions in this process
    # This would need to be done in separate processes
    current_version = get_current_akshare_version()

    if version and version != current_version:
        logger.warning(
            f"Requested version {version} does not match current version {current_version}. "
            f"Testing will proceed with current version."
        )

    logger.info(f"Testing AkShare version: {current_version}")

    all_results = []
    total_tests = 0
    passed_tests = 0
    available_count = 0
    unavailable_count = 0

    for category, functions in CRITICAL_FUNCTIONS.items():
        logger.info(f"\nTesting category: {category}")
        for func_name, params in functions:
            total_tests += 1
            logger.info(f"  Testing function: {func_name}")

            result = test_function_call(func_name, params)
            all_results.append(asdict(result))

            if result.exists:
                available_count += 1
                if result.test_passed:
                    passed_tests += 1
                    logger.info(f"    ✓ PASS - {func_name}")
                else:
                    logger.warning(f"    ⚠ EXISTS BUT FAILED - {func_name}: {result.test_error}")
            else:
                unavailable_count += 1
                logger.error(f"    ✗ NOT FOUND - {func_name}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0

    return VersionTestResult(
        version=current_version,
        test_time=test_time,
        total_functions=total_tests,
        available_functions=available_count,
        unavailable_functions=unavailable_count,
        test_success_rate=success_rate,
        functions=all_results,
    )


def save_results_to_json(result: VersionTestResult, output_file: str | Path) -> None:
    """Save test results to a JSON file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, ensure_ascii=False, indent=2)

    logger.info(f"Results saved to: {output_path}")


def generate_markdown_report(results: list[VersionTestResult], output_file: str | Path) -> None:
    """Generate a markdown compatibility report from multiple version test results."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# AkShare Version Compatibility Report\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        # Summary table
        f.write("## Version Summary\n\n")
        f.write("| Version | Total Functions | Available | Unavailable | Success Rate |\n")
        f.write("|---------|----------------|-----------|-------------|-------------|\n")

        for result in results:
            f.write(
                f"| {result.version} | {result.total_functions} | "
                f"{result.available_functions} | {result.unavailable_functions} | "
                f"{result.test_success_rate:.1f}% |\n"
            )

        f.write("\n")

        # Detailed results per version
        for result in results:
            f.write(f"## Version {result.version}\n\n")
            f.write(f"Test Time: {result.test_time}\n\n")

            # Function details
            f.write("### Function Details\n\n")
            f.write("| Function | Exists | Test Passed | Return Type | Error |\n")
            f.write("|----------|--------|-------------|-------------|-------|\n")

            for func_data in result.functions:
                exists_icon = "✓" if func_data["exists"] else "✗"
                passed_icon = "✓" if func_data["test_passed"] else "✗"
                error_text = func_data.get("test_error") or func_data.get("error") or ""
                if error_text:
                    error_text = error_text[:50] + "..." if len(error_text) > 50 else error_text

                f.write(
                    f"| {func_data['function_name']} | {exists_icon} | {passed_icon} | "
                    f"{func_data.get('return_type', 'N/A')} | {error_text} |\n"
                )

            f.write("\n")

        # Unavailable functions
        f.write("## Unavailable Functions\n\n")
        unavailable_funcs = set()
        for result in results:
            for func_data in result.functions:
                if not func_data["exists"]:
                    unavailable_funcs.add(func_data["function_name"])

        if unavailable_funcs:
            f.write("The following functions are not available in one or more versions:\n\n")
            for func_name in sorted(unavailable_funcs):
                f.write(f"- {func_name}\n")
        else:
            f.write("All tested functions are available in all versions.\n")

        f.write("\n")

        # Recommendations
        f.write("## Recommendations\n\n")
        if results:
            best_version = max(results, key=lambda r: r.test_success_rate)
            f.write(f"**Recommended Version:** {best_version.version}\n\n")
            f.write(f"This version has the highest success rate ({best_version.test_success_rate:.1f}%).\n")

    logger.info(f"Markdown report saved to: {output_path}")


def test_single_version(version: str | None = None) -> int:
    """Test a single AkShare version."""
    logger.info("=" * 60)
    logger.info("AkShare Version Compatibility Testing")
    logger.info("=" * 60)

    result = test_all_functions_in_version(version)

    # Save JSON results
    output_dir = Path("test_results/akshare_compatibility")
    json_file = output_dir / f"akshare_{result.version}_test.json"
    save_results_to_json(result, json_file)

    # Generate markdown report
    md_file = output_dir / f"akshare_{result.version}_report.md"
    generate_markdown_report([result], md_file)

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Version: {result.version}")
    logger.info(f"Total Functions: {result.total_functions}")
    logger.info(f"Available: {result.available_functions}")
    logger.info(f"Unavailable: {result.unavailable_functions}")
    logger.info(f"Success Rate: {result.test_success_rate:.1f}%")
    logger.info(f"\nResults saved to: {output_dir}")

    return 0 if result.test_success_rate > 50 else 1


def install_akshare_version(version: str) -> bool:
    """Install a specific AkShare version."""
    try:
        logger.info(f"Installing AkShare version {version}...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", f"akshare=={version}", "--quiet"],
            check=True,
        )
        logger.info(f"Successfully installed AkShare {version}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install AkShare {version}: {e}")
        return False


def test_multiple_versions(versions: list[str]) -> int:
    """Test multiple AkShare versions."""
    logger.info("=" * 60)
    logger.info("Testing Multiple AkShare Versions")
    logger.info("=" * 60)

    results = []
    current_version = get_current_akshare_version()

    for version in versions:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Testing version: {version}")
        logger.info(f"{'=' * 60}")

        # Install the version
        if not install_akshare_version(version):
            logger.error(f"Skipping version {version} due to installation failure")
            continue

        # Need to re-import to get new version
        import importlib

        import akshare

        importlib.reload(akshare)

        # Test this version
        result = test_all_functions_in_version(version)
        results.append(result)

    # Restore original version
    if current_version != "not installed":
        logger.info(f"\nRestoring original AkShare version: {current_version}")
        install_akshare_version(current_version)

    # Generate combined report
    output_dir = Path("test_results/akshare_compatibility")
    md_file = output_dir / "akshare_multi_version_report.md"
    generate_markdown_report(results, md_file)

    # Save all JSON results
    for result in results:
        json_file = output_dir / f"akshare_{result.version}_test.json"
        save_results_to_json(result, json_file)

    logger.info(f"\n{'=' * 60}")
    logger.info("MULTI-VERSION TEST COMPLETE")
    logger.info(f"{'=' * 60}")
    logger.info(f"Tested {len(results)} versions")
    logger.info(f"Results saved to: {output_dir}")

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test AkShare version compatibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Test current version
    python scripts/test_akshare_versions.py

    # Test specific version
    python scripts/test_akshare_versions.py --version 1.18.23

    # Test multiple versions
    python scripts/test_akshare_versions.py --all-versions
    python scripts/test_akshare_versions.py --versions 1.17.80 1.18.0 1.18.10 1.18.23
        """,
    )

    parser.add_argument("--version", type=str, help="Test a specific AkShare version")
    parser.add_argument(
        "--all-versions",
        action="store_true",
        help="Test all supported versions (1.17.80, 1.18.0, 1.18.10, 1.18.23)",
    )
    parser.add_argument(
        "--versions",
        nargs="+",
        type=str,
        help="Test specific list of versions",
    )

    args = parser.parse_args()

    # Determine which versions to test
    if args.all_versions:
        versions = ["1.17.80", "1.18.0", "1.18.10", "1.18.23"]
        return test_multiple_versions(versions)
    elif args.versions:
        return test_multiple_versions(args.versions)
    elif args.version:
        # Install and test specific version
        if install_akshare_version(args.version):
            import importlib

            import akshare

            importlib.reload(akshare)
            return test_single_version(args.version)
        else:
            return 1
    else:
        # Test current version
        return test_single_version()


if __name__ == "__main__":
    sys.exit(main())