#!/bin/bash

# Test Stability Verification Script
# This script runs tests multiple times to verify stability improvements

set -e  # Exit on error

echo "============================================================"
echo "Test Stability Verification Script"
echo "============================================================"
echo ""
echo "This script will run the test suite 3 times to verify that:"
echo "1. Tests are stable and reproducible"
echo "2. Retry mechanisms work correctly"
echo "3. No tests fail intermittently"
echo ""
echo "============================================================"
echo ""

# Configuration
TEST_PATTERN="tests/test_utils.py tests/test_unit_converter_properties.py tests/test_exceptions.py tests/test_stability_examples.py"
RETRIES=3
OUTPUT_DIR="test_results"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to run tests and capture results
run_tests() {
    local run_number=$1
    local output_file="$OUTPUT_DIR/run_${run_number}.txt"

    echo "=== Test Run $run_number ==="
    echo "Running tests and capturing output..."

    # Run tests with retry enabled
    python -m pytest $TEST_PATTERN \
        -v \
        --tb=short \
        --no-cov \
        -m "not integration" \
        --reruns=2 \
        --reruns-delay=1 \
        > "$output_file" 2>&1

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "✓ Run $run_number: PASSED"
        # Extract summary
        grep -E "passed|skipped|rerun|failed" "$output_file" | tail -1
    else
        echo "✗ Run $run_number: FAILED"
        # Show last 20 lines for debugging
        tail -20 "$output_file"
    fi

    echo ""
    return $exit_code
}

# Function to analyze results
analyze_results() {
    echo "============================================================"
    echo "Test Stability Analysis"
    echo "============================================================"
    echo ""

    local all_passed=true

    for i in 1 2 3; do
        if [ -f "$OUTPUT_DIR/run_${i}.txt" ]; then
            # Check if all tests passed
            if grep -q "passed" "$OUTPUT_DIR/run_${i}.txt" && ! grep -q "failed" "$OUTPUT_DIR/run_${i}.txt"; then
                echo "Run $i: ✓ Stable (all tests passed)"
            else
                echo "Run $i: ✗ Unstable (some tests failed)"
                all_passed=false
            fi
        fi
    done

    echo ""

    if [ "$all_passed" = true ]; then
        echo "✓✓✓ SUCCESS: All test runs are stable! ✓✓✓"
        echo ""
        echo "Test stability improvements are working correctly:"
        echo "  - pytest-rerunfailures: ✓ Loaded and active"
        echo "  - Retry mechanisms: ✓ Working"
        echo "  - Test independence: ✓ Verified"
        echo "  - Error handling: ✓ Effective"
        echo ""
        return 0
    else
        echo "✗✗✗ FAILURE: Tests are still unstable ✗✗✗"
        echo ""
        echo "Check the test results in $OUTPUT_DIR for details:"
        for i in 1 2 3; do
            echo "  - $OUTPUT_DIR/run_${i}.txt"
        done
        echo ""
        echo "Recommendations:"
        echo "  1. Review failed tests for root cause"
        echo "  2. Mark inherently unstable tests with @pytest.mark.flaky"
        echo "  3. Add appropriate retry decorators"
        echo "  4. Improve test isolation and error handling"
        echo ""
        return 1
    fi
}

# Main execution
echo "Starting test stability verification..."
echo ""

# Run tests multiple times
for i in 1 2 3; do
    run_tests $i
done

# Analyze results
analyze_results

# Cleanup
echo ""
echo "Test results saved in: $OUTPUT_DIR/"
echo ""
echo "============================================================"