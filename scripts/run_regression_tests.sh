#!/bin/bash
# Helper script to run regression tests
#
# Usage:
#   bash scripts/run_regression_tests.sh              # Run tests normally
#   bash scripts/run_regression_tests.sh --update     # Update snapshots
#   bash scripts/run_regression_tests.sh --details    # Show snapshot details/diffs

set -e

UPDATE_MODE=""
DETAILS_MODE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --update)
            UPDATE_MODE="--snapshot-update"
            shift
            ;;
        --details)
            DETAILS_MODE="--snapshot-details"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: bash scripts/run_regression_tests.sh [--update] [--details]"
            exit 1
            ;;
    esac
done

echo "=== Running Regression Tests ==="

if [ -n "$UPDATE_MODE" ]; then
    echo "Mode: UPDATE SNAPSHOTS"
    echo "Warning: This will update all snapshot baselines!"
    echo ""
elif [ -n "$DETAILS_MODE" ]; then
    echo "Mode: SHOW DETAILS"
    echo ""
else
    echo "Mode: NORMAL TEST RUN"
    echo ""
fi

# Run tests with appropriate flags
pytest tests/test_regression.py $UPDATE_MODE $DETAILS_MODE -v --tb=short

echo ""
if [ -n "$UPDATE_MODE" ]; then
    echo "=== Snapshots Updated ==="
    echo "Please review changes in tests/snapshots/"
    echo "Commit with: git commit tests/snapshots/ tests/test_regression.py"
else
    echo "=== Tests Complete ==="
    if [ -n "$DETAILS_MODE" ]; then
        echo "Review the details above to understand any differences"
    fi
fi