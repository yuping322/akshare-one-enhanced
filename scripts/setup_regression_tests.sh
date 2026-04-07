#!/bin/bash
# Setup script for regression testing with snapshots
#
# This script installs dependencies and creates initial snapshots for regression tests.
#
# Usage: bash scripts/setup_regression_tests.sh

set -e

echo "=== Setting up Regression Testing Environment ==="
echo ""

# Step 1: Install pytest-snapshot
echo "Step 1: Installing pytest-snapshot..."
pip install pytest-snapshot

echo ""
echo "Step 2: Running regression tests to create initial snapshots..."
echo "This may take a few minutes as it will call real APIs."
echo ""

# Step 3: Create initial snapshots
pytest tests/test_regression.py --snapshot-update -v

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Snapshots have been created in: tests/snapshots/"
echo ""
echo "Next steps:"
echo "1. Review generated snapshots in tests/snapshots/"
echo "2. Run tests normally: pytest tests/test_regression.py -v"
echo "3. Update snapshots (when needed): pytest tests/test_regression.py --snapshot-update -v"
echo "4. Read documentation: docs/regression_testing.md"
echo ""