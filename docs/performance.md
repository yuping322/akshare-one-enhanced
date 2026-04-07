# Performance Guidelines and Benchmarks

This document provides performance baselines, optimization recommendations, and resource usage guidelines for akshare-one.

## Performance Baselines

### Key Interface Response Times

All performance tests are conducted under normal network conditions. Response times may vary based on:
- Network latency and bandwidth
- Server load and response time
- Cache status (cached requests are faster)
- Data size and complexity

| Interface | Baseline (seconds) | Notes |
|-----------|-------------------|-------|
| `get_basic_info()` | < 2.0s | Single stock basic information |
| `get_hist_data()` | < 3.0s | 1 year of daily OHLCV data (~250 rows) |
| `get_realtime_data()` | < 1.0s | Real-time quote for single symbol |
| `get_etf_hist_data()` | < 2.0s | ETF historical data |
| `get_etf_realtime_data()` | < 1.5s | All ETF realtime quotes |
| `get_fund_manager_info()` | < 2.0s | Fund manager information |
| `get_stock_fund_flow()` | < 3.0s | Stock fund flow data |

### Running Performance Tests

```bash
# Run all performance tests
pytest tests/test_performance.py -v -m performance

# Run specific performance test class
pytest tests/test_performance.py::TestResponseTime -v

# Run with detailed output
pytest tests/test_performance.py -v -s -m performance
```

## Concurrency and Thread Safety

### Concurrent Access Testing

akshare-one supports concurrent access from multiple threads. Performance tests verify:

- **10 concurrent requests**: At least 80% success rate
- **Thread safety**: Multiple threads accessing same symbol work correctly
- **Mixed concurrent requests**: Different endpoints can be called concurrently

### Best Practices for Concurrent Usage

1. **Use ThreadPoolExecutor** for concurrent requests:
```python
from concurrent.futures import ThreadPoolExecutor
from akshare_one import get_basic_info

symbols = ["600000", "600001", "600002", "600003"]

def fetch_data(symbol):
    return get_basic_info(symbol)

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_data, symbols))
```

2. **Limit concurrent workers**: Recommended 5-10 workers for most use cases
3. **Handle errors gracefully**: Network failures can occur during concurrent access
4. **Use caching**: Cache improves concurrent performance significantly

## Memory Usage

### Memory Baselines

| Operation | Memory Usage | Notes |
|-----------|--------------|-------|
| Single `get_basic_info()` | < 5 MB | One stock info |
| Large dataset (1 year daily) | < 10 MB | ~250 rows of OHLCV data |
| 20 repeated calls | < 1 MB growth | No memory leaks |
| Cache (10 symbols) | Configurable | See cache configuration |

### Memory Best Practices

1. **Explicit cleanup for large datasets**:
```python
# Process large dataset
df = get_hist_data("600000", start_date="2020-01-01", end_date="2024-12-31")
# Process data...
result = df.mean()

# Explicitly release memory
del df
```

2. **Use row_filter to limit data size**:
```python
# Get only recent data
df = get_hist_data(
    "600000",
    start_date="2024-01-01",
    end_date="2024-12-31",
    row_filter={"top_n": 100}  # Only first 100 rows
)
```

3. **Disable cache for one-time large queries**:
```python
import os
os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "false"
df = get_hist_data("600000", start_date="2010-01-01", end_date="2024-12-31")
```

4. **Monitor memory usage**:
```python
import tracemalloc
import gc

tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

# Perform operations
df = get_basic_info("600000")

gc.collect()
snapshot2 = tracemalloc.take_snapshot()
top_stats = snapshot2.compare_to(snapshot1, 'lineno')

for stat in top_stats[:10]:
    print(stat)
```

## Resource Management

### Cache Configuration

Cache is managed by `cachetools.TTLCache` with configurable limits:

```python
from akshare_one.modules.cache import CACHE_CONFIG

# Check cache status
cache = CACHE_CONFIG["info_cache"]
print(f"Cache size: {cache.currsize} / {cache.maxsize}")
print(f"Cache TTL: {cache.ttl} seconds")

# Clear cache if needed
cache.clear()
```

Default cache configurations:
- **info_cache**: maxsize=1000, ttl=3600s (1 hour)
- **hist_cache**: maxsize=500, ttl=86400s (24 hours for daily data)
- **realtime_cache**: maxsize=100, ttl=60s (1 minute)

### HTTP Connection Management

akshare-one uses a shared HTTP client with connection pooling:

```python
from akshare_one.http_client import get_http_client

# Get shared client
client = get_http_client()

# Connections are automatically managed
# No need to manually close connections
```

### Under Load Performance

System stability under sustained load (50 requests):
- **Memory growth**: < 50 MB
- **Thread growth**: < 5 threads
- **Success rate**: > 90%

## Performance Optimization Tips

### 1. Use Caching Effectively

Caching is the most effective optimization:

```python
import os

# Enable cache (default)
os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "true"

# First call - slower (cache miss)
df1 = get_basic_info("600000")  # ~2s

# Second call - faster (cache hit)
df2 = get_basic_info("600000")  # < 0.1s
```

### 2. Batch Requests

For multiple symbols, use concurrent requests:

```python
from concurrent.futures import ThreadPoolExecutor

def batch_get_info(symbols):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_basic_info, symbols))
    return results

# Faster than sequential requests
symbols = ["600000", "600001", "600002", "600003", "600004"]
results = batch_get_info(symbols)  # ~2-3s total vs ~10s sequential
```

### 3. Limit Data Size

Use appropriate date ranges and filters:

```python
# Bad: Requesting 5 years of data
df = get_hist_data("600000", start_date="2019-01-01", end_date="2024-12-31")

# Good: Request only needed period
df = get_hist_data("600000", start_date="2024-01-01", end_date="2024-12-31")

# Better: Use row_filter for recent data
df = get_hist_data(
    "600000",
    start_date="2024-01-01",
    end_date="2024-12-31",
    row_filter={"sort_by": "timestamp", "top_n": 30}
)
```

### 4. Use Multi-Source API for Reliability

Multi-source API automatically fails over to backup sources:

```python
from akshare_one import get_hist_data_multi_source

# Automatically tries: eastmoney_direct -> eastmoney -> sina
df = get_hist_data_multi_source("600000", interval="day")
```

### 5. Choose Appropriate Data Source

Different sources have different performance characteristics:

| Source | Performance | Reliability | Data Quality |
|--------|-------------|-------------|--------------|
| eastmoney_direct | Fast | High | Excellent |
| eastmoney | Medium | High | Good |
| sina | Medium | Medium | Good |
| xueqiu | Slow | Medium | Good |

## Troubleshooting Performance Issues

### Slow Response Times

1. **Check network connectivity**: Poor network increases latency
2. **Verify cache status**: Cache miss is slower than cache hit
3. **Monitor server response**: Data source servers may be slow
4. **Reduce data size**: Large datasets take longer to transfer

### Memory Issues

1. **Monitor memory usage**: Use tracemalloc or psutil
2. **Clear large objects**: Explicitly `del` large DataFrames
3. **Disable cache**: For one-time large queries
4. **Check for leaks**: Run memory leak tests

### Connection Errors

1. **Check SSL verification**: May need to configure SSL settings
2. **Use retry logic**: Implement retry with exponential backoff
3. **Use multi-source API**: Automatic failover handles errors
4. **Reduce concurrency**: Too many concurrent requests may fail

## Performance Monitoring

### Running Performance Tests Regularly

```bash
# Run full performance suite
pytest tests/test_performance.py -v -m performance

# Check specific metrics
pytest tests/test_performance.py::TestResponseTime -v
pytest tests/test_performance.py::TestMemoryUsage -v
pytest tests/test_performance.py::TestConcurrency -v
```

### Integration with CI/CD

Add performance tests to CI pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Performance Tests
  run: pytest tests/test_performance.py -v -m performance --tb=short
  continue-on-error: true  # Don't fail build on performance test failures
```

## Future Performance Improvements

### Planned Optimizations

1. **Async support**: Add async/await for better concurrency
2. **Batch API**: Single request for multiple symbols
3. **Compression**: Compress large data transfers
4. **Connection pooling**: Improve HTTP connection reuse
5. **Query optimization**: Reduce data transfer size

### Performance Testing Roadmap

1. **Add benchmark comparisons**: Compare versions
2. **Stress testing**: Higher load scenarios
3. **Long-running tests**: Extended stability tests
4. **Performance regression detection**: Automated alerts

## Performance Test Results Template

When running performance tests, document results:

```
Performance Test Results - [Date]
==================================

Test Environment:
- Python: [version]
- Platform: [OS]
- Network: [connection type]

Response Time Results:
- get_basic_info: [time]s (baseline: 2.0s) [PASS/FAIL]
- get_hist_data: [time]s (baseline: 3.0s) [PASS/FAIL]
- get_realtime_data: [time]s (baseline: 1.0s) [PASS/FAIL]

Concurrency Results:
- 10 concurrent requests: [success_rate]% success
- Thread safety: [PASS/FAIL]

Memory Usage:
- Single request: [memory] MB
- Large dataset: [memory] MB
- Memory leak test: [PASS/FAIL]

Notes:
- [Any observations or issues]
```

## Conclusion

akshare-one provides reliable performance for financial data access:
- Response times meet baselines for most operations
- Thread-safe concurrent access
- Reasonable memory usage with no leaks
- Effective caching for improved performance

For optimal performance:
- Use caching effectively
- Batch concurrent requests appropriately
- Limit data size when possible
- Monitor performance regularly

For questions or issues, refer to test results and troubleshooting guide above.