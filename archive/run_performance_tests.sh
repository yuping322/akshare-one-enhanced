#!/bin/bash
# Performance Tests Runner Script for akshare-one
# This script runs various performance and reliability tests

echo "========================================"
echo "akshare-one Performance Test Runner"
echo "========================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest is not installed. Please install it first:"
    echo "  pip install pytest pytest-timeout psutil"
    exit 1
fi

echo "Test Options:"
echo "1. Run all performance tests (--run-performance)"
echo "2. Run response time tests only"
echo "3. Run concurrency tests only"
echo "4. Run memory usage tests only"
echo "5. Run resource management tests only"
echo "6. Run stability tests only"
echo "7. Run with integration tests (--run-integration)"
echo ""
echo "Choose option (1-7): "
read -r option

case $option in
    1)
        echo "Running all performance tests..."
        pytest tests/test_performance.py -v --no-cov --run-performance -s
        ;;
    2)
        echo "Running response time tests..."
        pytest tests/test_performance.py::TestResponseTime -v --no-cov --run-performance -s
        ;;
    3)
        echo "Running concurrency tests..."
        pytest tests/test_performance.py::TestConcurrency -v --no-cov --run-performance -s
        ;;
    4)
        echo "Running memory usage tests..."
        pytest tests/test_performance.py::TestMemoryUsage -v --no-cov --run-performance -s
        ;;
    5)
        echo "Running resource management tests..."
        pytest tests/test_performance.py::TestResourceManagement -v --no-cov --run-performance -s
        ;;
    6)
        echo "Running stability tests..."
        pytest tests/test_performance.py::TestStabilityUnderLoad -v --no-cov --run-performance -s
        ;;
    7)
        echo "Running with integration tests (includes network calls)..."
        pytest tests/test_performance.py -v --no-cov --run-integration -s
        ;;
    *)
        echo "Invalid option. Running default (all performance tests)..."
        pytest tests/test_performance.py -v --no-cov --run-performance -s
        ;;
esac

echo ""
echo "========================================"
echo "Performance tests completed!"
echo "========================================"