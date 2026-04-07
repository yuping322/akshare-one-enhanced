#!/usr/bin/env python3
"""
CI Configuration Validation Script

This script validates the CI workflow configuration and tests setup.
Run it locally to verify CI configuration before pushing changes.

Usage:
    python scripts/validate_ci_config.py
"""

import sys
import yaml
from pathlib import Path


def validate_workflow_syntax():
    """Validate YAML syntax of workflow files."""
    print("=" * 60)
    print("Validating Workflow YAML Syntax")
    print("=" * 60)

    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("❌ Workflow directory not found: .github/workflows/")
        return False

    workflows = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
    if not workflows:
        print("❌ No workflow files found")
        return False

    all_valid = True
    for workflow in workflows:
        try:
            with open(workflow) as f:
                yaml.safe_load(f)
            print(f"✅ {workflow.name} - Valid YAML syntax")
        except yaml.YAMLError as e:
            print(f"❌ {workflow.name} - YAML syntax error:")
            print(f"   {e}")
            all_valid = False

    return all_valid


def validate_pytest_markers():
    """Validate pytest markers configuration."""
    print("\n" + "=" * 60)
    print("Validating Pytest Markers")
    print("=" * 60)

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return False

    import tomli
    with open(pyproject_path, "rb") as f:
        config = tomli.load(f)

    pytest_config = config.get("tool", {}).get("pytest", {}).get("ini_options", {})
    markers = pytest_config.get("markers", [])

    expected_markers = ["integration", "contract", "slow"]
    found_markers = []

    for marker_line in markers:
        marker_name = marker_line.split(":")[0].strip()
        found_markers.append(marker_name)

    print(f"Expected markers: {expected_markers}")
    print(f"Found markers: {found_markers}")

    missing_markers = set(expected_markers) - set(found_markers)
    if missing_markers:
        print(f"❌ Missing markers: {missing_markers}")
        return False

    print("✅ All required pytest markers are configured")
    return True


def validate_test_structure():
    """Validate test directory structure."""
    print("\n" + "=" * 60)
    print("Validating Test Structure")
    print("=" * 60)

    test_dir = Path("tests")
    if not test_dir.exists():
        print("❌ tests/ directory not found")
        return False

    conftest = test_dir / "conftest.py"
    if not conftest.exists():
        print("❌ tests/conftest.py not found")
        return False

    print("✅ tests/conftest.py exists")

    # Check for marker usage
    import re
    marker_pattern = re.compile(r"@pytest\.mark\.(integration|contract|slow)")

    test_files = list(test_dir.glob("test_*.py"))
    marker_usage = {}

    for test_file in test_files:
        with open(test_file) as f:
            content = f.read()
            markers_found = marker_pattern.findall(content)
            if markers_found:
                marker_usage[test_file.name] = markers_found

    print(f"\n✅ Found {len(test_files)} test files")
    print(f"✅ {len(marker_usage)} files use test markers")

    for filename, markers in marker_usage.items():
        unique_markers = set(markers)
        print(f"   {filename}: {', '.join(unique_markers)}")

    return True


def validate_coverage_config():
    """Validate coverage configuration."""
    print("\n" + "=" * 60)
    print("Validating Coverage Configuration")
    print("=" * 60)

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return False

    import tomli
    with open(pyproject_path, "rb") as f:
        config = tomli.load(f)

    coverage_config = config.get("tool", {}).get("coverage", {})

    if not coverage_config:
        print("❌ No coverage configuration found")
        return False

    run_config = coverage_config.get("run", {})
    report_config = coverage_config.get("report", {})

    # Check source
    source = run_config.get("source", [])
    if not source:
        print("❌ Coverage source not configured")
        return False
    print(f"✅ Coverage source: {source}")

    # Check fail_under threshold
    fail_under = report_config.get("fail_under", 0)
    print(f"✅ Coverage threshold: {fail_under}%")

    # Check omit patterns
    omit = run_config.get("omit", [])
    print(f"✅ Coverage omit patterns: {len(omit)} files/directories")

    return True


def validate_python_versions():
    """Validate Python version configuration."""
    print("\n" + "=" * 60)
    print("Validating Python Version Configuration")
    print("=" * 60)

    workflow_path = Path(".github/workflows/test.yml")
    if not workflow_path.exists():
        print("❌ test.yml workflow not found")
        return False

    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    # Find test-offline job
    offline_job = workflow.get("jobs", {}).get("test-offline", {})
    matrix = offline_job.get("strategy", {}).get("matrix", {})
    python_versions = matrix.get("python-version", [])
    os_list = matrix.get("os", [])

    print(f"✅ Python versions: {python_versions}")
    print(f"✅ Platforms: {os_list}")

    # Check excludes
    excludes = matrix.get("exclude", [])
    if excludes:
        print(f"✅ Excluded combinations: {len(excludes)}")
        for exclude in excludes:
            print(f"   - {exclude}")

    return True


def validate_requirements():
    """Validate requirements file exists."""
    print("\n" + "=" * 60)
    print("Validating Requirements Files")
    print("=" * 60)

    dev_req = Path("requirements-dev.txt")
    if dev_req.exists():
        print("✅ requirements-dev.txt exists")
        with open(dev_req) as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"   {len(lines)} packages listed")
    else:
        print("⚠️ requirements-dev.txt not found (optional)")

    # Check pyproject.toml dependency groups
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        import tomli
        with open(pyproject_path, "rb") as f:
            config = tomli.load(f)

        dev_deps = config.get("dependency-groups", {}).get("dev", [])
        if dev_deps:
            print(f"✅ pyproject.toml dev dependencies: {len(dev_deps)} packages")
        else:
            print("❌ No dev dependencies in pyproject.toml")
            return False

    return True


def main():
    """Run all validation checks."""
    print("CI Configuration Validation")
    print("=" * 60)
    print()

    checks = [
        ("Workflow Syntax", validate_workflow_syntax),
        ("Pytest Markers", validate_pytest_markers),
        ("Test Structure", validate_test_structure),
        ("Coverage Config", validate_coverage_config),
        ("Python Versions", validate_python_versions),
        ("Requirements", validate_requirements),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} - Validation failed with error:")
            print(f"   {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print()
    print(f"Total: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All CI configuration checks passed!")
        return 0
    else:
        print("\n⚠️ Some checks failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())