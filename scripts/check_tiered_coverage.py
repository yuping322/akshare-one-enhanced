#!/usr/bin/env python3
"""
Check coverage levels with tiered thresholds for different module categories.

This script enforces different coverage thresholds for:
- Core modules (base, factory_base, client): 75%
- Important modules (etf, bond, futures, etc.): 60%
- Extension modules (all others): 50%
"""

import json
import subprocess
import sys
from pathlib import Path

# Define module categories with their coverage thresholds
CORE_MODULES = {
    "client.py": 75,
    "modules/base.py": 75,
    "modules/factory_base.py": 75,
}

IMPORTANT_MODULES = {
    "modules/etf": 60,
    "modules/bond": 60,
    "modules/futures": 60,
    "modules/index": 60,
    "modules/financial": 60,
    "modules/historical": 60,
    "modules/realtime": 60,
}

# Extension modules have a default threshold of 50%
EXTENSION_THRESHOLD = 50


def run_coverage():
    """Run pytest with coverage and return the coverage data."""
    result = subprocess.run(
        ["pytest", "--cov=akshare_one", "--cov-report=json", "-q", "tests/"],
        capture_output=True,
        text=True,
    )

    # Coverage JSON file is created by --cov-report=json
    coverage_file = Path("coverage.json")
    if not coverage_file.exists():
        print("Error: coverage.json not found")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)

    with open(coverage_file) as f:
        return json.load(f)


def categorize_file(file_path: str) -> tuple[str, int]:
    """Categorize a file and return its category and threshold."""
    # Check if it's a core module
    for core_pattern, threshold in CORE_MODULES.items():
        if core_pattern in file_path:
            return "core", threshold

    # Check if it's an important module
    for important_pattern, threshold in IMPORTANT_MODULES.items():
        if important_pattern in file_path:
            return "important", threshold

    # Default to extension module
    return "extension", EXTENSION_THRESHOLD


def check_tiered_coverage():
    """Check coverage levels for each tier."""
    print("Running coverage analysis...")
    coverage_data = run_coverage()

    files = coverage_data.get("files", {})
    totals = coverage_data.get("totals", {})

    # Group files by category
    categorized = {"core": {}, "important": {}, "extension": {}}

    for file_path, file_data in files.items():
        # Skip __init__.py files and omitted paths
        if "__init__.py" in file_path:
            continue
        if "mcp/" in file_path or "logging_config.py" in file_path or "health/" in file_path:
            continue

        category, threshold = categorize_file(file_path)
        covered_percent = file_data["summary"]["percent_covered"]

        categorized[category][file_path] = {
            "coverage": covered_percent,
            "threshold": threshold,
            "passed": covered_percent >= threshold,
        }

    # Print results
    print("\n" + "=" * 80)
    print("TIERED COVERAGE REPORT")
    print("=" * 80)

    exit_code = 0

    for category in ["core", "important", "extension"]:
        files_data = categorized[category]
        if not files_data:
            continue

        print(f"\n{category.upper()} MODULES:")
        print("-" * 80)

        failed_files = []
        for file_path, data in sorted(files_data.items()):
            status = "✓" if data["passed"] else "✗"
            coverage = data["coverage"]
            threshold = data["threshold"]

            # Only show files that are below threshold or close to it
            if coverage < threshold + 10:  # Show files within 10% of threshold
                print(f"{status} {file_path:60s} {coverage:5.1f}% (threshold: {threshold}%)")

            if not data["passed"]:
                failed_files.append((file_path, coverage, threshold))

        if failed_files:
            exit_code = 1
            print(f"\n  FAILED: {len(failed_files)} file(s) below threshold")
        else:
            print(f"\n  PASSED: All files meet threshold")

    # Print overall summary
    total_coverage = totals.get("percent_covered", 0)
    print("\n" + "=" * 80)
    print(f"OVERALL COVERAGE: {total_coverage:.2f}%")
    print("=" * 80)

    # Print category averages
    for category in ["core", "important", "extension"]:
        files_data = categorized[category]
        if files_data:
            avg_coverage = sum(f["coverage"] for f in files_data.values()) / len(files_data)
            avg_threshold = sum(f["threshold"] for f in files_data.values()) / len(files_data)
            print(f"{category.upper():12s} average: {avg_coverage:5.1f}% (threshold: {avg_threshold:.0f}%)")

    return exit_code


if __name__ == "__main__":
    sys.exit(check_tiered_coverage())