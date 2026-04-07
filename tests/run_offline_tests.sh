#!/bin/bash
# Offline test runner for akshare-one
# This script runs tests in offline mode to ensure they don't fail due to network issues

set -e

echo "=== Running Offline Test Suite ==="
echo "This test run uses --offline flag to gracefully handle network errors"
echo ""

# Run tests with offline mode
python -m pytest tests/ \
  --offline \
  --tb=short \
  --maxfail=5 \
  -x \
  --ignore=tests/test_performance.py \
  --ignore=tests/mcp/test_mcp_p1_p2.py \
  -q

echo ""
echo "=== Offline Test Summary ==="
echo "Tests completed successfully in offline mode!"
echo ""
echo "Note: Network-dependent tests were automatically skipped."
echo "To run integration tests (requires network):"
echo "  pytest tests/ --run-integration"
echo ""