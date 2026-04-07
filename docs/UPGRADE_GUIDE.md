# Upgrade Guide

This guide provides detailed instructions for upgrading between major versions of AKShare One, including breaking changes, migration examples, and best practices.

## Overview

AKShare One follows [Semantic Versioning](https://semver.org/):
- **Patch upgrades** (0.5.1 → 0.5.2): No migration needed, backward compatible
- **Minor upgrades** (0.4.0 → 0.5.0): Usually backward compatible, review deprecations
- **Major upgrades** (0.x → 1.0): Breaking changes, follow migration guide

## Upgrade Checklist

Before upgrading, always:

1. **Read the CHANGELOG.md** for the version you're upgrading to
2. **Check this upgrade guide** for breaking changes and migration steps
3. **Backup your code** or use version control (git)
4. **Test in a separate environment** before upgrading production
5. **Run tests** after upgrade to ensure compatibility

## Version-specific Upgrade Guides

### Upgrading to v0.5.0 (from v0.4.x or earlier)

#### Summary

Version 0.5.0 is a **significant minor release** with major architectural improvements. While mostly backward compatible, it includes some breaking changes that require migration.

**Key changes**:
- Factory pattern refactoring (19 factory files removed)
- New `@api_endpoint` decorator for automatic routing
- Unified filtering API (`columns`, `row_filter` parameters)
- Multi-source data routing system
- Comprehensive exception hierarchy
- 14 new market data modules

#### Breaking Changes

#### 1. Factory Pattern Refactoring

**Impact**: HIGH - All module usage affected

**Before (v0.4.x)**:

```python
from akshare_one.modules.historical import HistoricalDataFactory

# Direct factory instantiation
factory = HistoricalDataFactory()
provider = factory.get_provider("eastmoney", symbol="600000")
df = provider.get_hist_data()
```

**After (v0.5.0)**:

```python
from akshare_one import get_hist_data

# Direct function call (recommended)
df = get_hist_data(
    symbol="600000",
    source="eastmoney"
)

# Or use decorator-based routing (internal)
from akshare_one.modules.historical import HistoricalDataFactory

# Factory now uses call_provider_method
df = HistoricalDataFactory.call_provider_method(
    "get_hist_data",
    source="eastmoney",
    symbol="600000"
)
```

**Migration steps**:

1. Replace direct provider instantiation with high-level API functions
2. Update imports from `modules.*` to top-level imports
3. Use `source` parameter instead of passing source to factory

**Why changed**:
- Simplified API for users
- Reduced code duplication (19 factory files deleted)
- Automatic routing and error handling

#### 2. Unified Filtering API

**Impact**: MEDIUM - New parameters added to all APIs

**Before (v0.4.x)**:

```python
# Manual filtering
df = get_hist_data(symbol="600000")
df = df[['timestamp', 'close', 'volume']]  # Column selection
df = df.head(100)  # Row filtering
df = df.sort_values('close', ascending=False)
```

**After (v0.5.0)**:

```python
# Built-in filtering (recommended)
df = get_hist_data(
    symbol="600000",
    columns=['timestamp', 'close', 'volume'],
    row_filter={
        'top_n': 100,
        'sort_by': 'close',
        'ascending': False
    }
)
```

**New parameters**:

- `columns`: List of column names to select
- `row_filter`: Dict with filtering options:
  - `top_n`: Return first N rows
  - `sort_by`: Sort by column name
  - `ascending`: Sort order (default False)
  - `query`: Pandas query expression
  - `sample`: Random sampling fraction (0-1)

**Migration steps**:

1. Review your data filtering patterns
2. Identify opportunities to use built-in filtering
3. Replace manual filtering with `columns` and `row_filter`
4. Test to ensure same results

**Benefits**:
- Cleaner code
- Better performance (filtering happens before data transfer)
- Easier integration with LLM skills

#### 3. Multi-source API Endpoints

**Impact**: LOW - New optional feature

**Before (v0.4.x)**:

```python
# Manual failover
try:
    df = get_hist_data(symbol="600000", source="eastmoney")
except Exception:
    df = get_hist_data(symbol="600000", source="sina")
```

**After (v0.5.0)**:

```python
# Automatic failover (recommended)
df = get_hist_data_multi_source(
    symbol="600000",
    sources=["eastmoney", "sina"]  # Try in order
)

# Or use router for advanced control
from akshare_one import create_historical_router

router = create_historical_router(
    symbol="600000",
    sources=["eastmoney", "sina"]
)
result = router.execute("get_hist_data")
df = result.data
print(f"Used source: {result.source}")
```

**New functions**:

- `get_hist_data_multi_source()`
- `get_realtime_data_multi_source()`
- `get_financial_data_multi_source()`
- `get_northbound_flow_multi_source()`
- And 10+ more...

**Migration steps**:

1. Identify critical data fetching points
2. Replace with multi-source endpoints for reliability
3. Configure source priority order
4. Monitor which source is actually used

**Benefits**:
- Automatic failover
- Better reliability
- Execution tracking

#### 4. Exception Handling

**Impact**: LOW - Exception types changed

**Before (v0.4.x)**:

```python
try:
    df = get_hist_data(symbol="600000")
except Exception as e:
    print(f"Error: {e}")
```

**After (v0.5.0)**:

```python
try:
    df = get_hist_data(symbol="600000")
except ValueError as e:
    # Invalid parameters (symbol format, dates)
    print(f"Parameter error: {e}")
except ConnectionError as e:
    # Network/data source issues
    print(f"Network error: {e}")
except KeyError as e:
    # Upstream API changed
    print(f"API change: {e}")
except RuntimeError as e:
    # Other errors
    print(f"General error: {e}")
```

**New exception hierarchy**:

Internal exceptions (for developers):
- `InvalidParameterError`
- `DataSourceUnavailableError`
- `NoDataError`
- `UpstreamChangedError`
- `RateLimitError`
- `DataValidationError`

Public exceptions (for users):
- `ValueError` (mapped from `InvalidParameterError`, `NoDataError`)
- `ConnectionError` (mapped from `DataSourceUnavailableError`)
- `KeyError` (mapped from `UpstreamChangedError`)
- `RuntimeError` (mapped from others)

**Migration steps**:

1. Update exception handling code
2. Use specific exception types for better error handling
3. Map errors to appropriate user messages

**Why changed**:
- Better error categorization
- Clearer debugging
- Public API stability

#### 5. Standardized Parameter Names

**Impact**: LOW - Some parameter names changed

**Before (v0.4.x)**:

```python
# Inconsistent naming across modules
df = get_hist_data(
    symbol="600000",
    start="2024-01-01",  # ❌ Old name
    end="2024-12-31"     # ❌ Old name
)
```

**After (v0.5.0)**:

```python
# Consistent naming everywhere
df = get_hist_data(
    symbol="600000",
    start_date="2024-01-01",  # ✅ Standard name
    end_date="2024-12-31"     # ✅ Standard name
)
```

**Standard parameter names**:

- `symbol`: Stock/asset code (6-digit format)
- `start_date`, `end_date`: Date range (YYYY-MM-DD)
- `source`: Single data source name
- `sources`: List of data sources (multi-source)
- `columns`: Column selection
- `row_filter`: Row filtering config

**Migration steps**:

1. Check function signatures for parameter name changes
2. Update calls to use standard names
3. Old names may still work (deprecated) but will be removed

#### Deprecations in v0.5.0

The following are deprecated but still work:

| Deprecated | Replacement | Removal Version |
|-----------|-------------|-----------------|
| Direct factory instantiation | Use top-level functions | v0.7.0 |
| Manual data source switching | Use multi-source APIs | v0.7.0 |
| Old parameter names | Use standard names | v0.6.0 |
| Implicit field naming | Use field naming standards | v1.0.0 |

#### New Features in v0.5.0 (No Migration Needed)

These are new features that don't require migration:

- **14 new market data modules**: northbound, fundflow, lhb, limitup, blockdeal, disclosure, macro, margin, pledge, restricted, goodwill, esg, analyst, sentiment
- **Dynamic field mapping**: Automatic standardization
- **AkShare compatibility adapter**: Handle upstream drift
- **Monitoring and observability**: Logging, metrics, health checks
- **Enhanced test infrastructure**: Timeout, contract tests

#### Full Migration Example

**Complete example of upgrading a script**:

**Before (v0.4.x)**:

```python
# old_script.py
from akshare_one.modules.historical import HistoricalDataFactory
from akshare_one.modules.realtime import RealtimeDataFactory
import pandas as pd

# Get historical data
factory = HistoricalDataFactory()
try:
    provider = factory.get_provider("eastmoney", symbol="600000")
    hist_df = provider.get_hist_data(start="2024-01-01", end="2024-12-31")
except Exception:
    provider = factory.get_provider("sina", symbol="600000")
    hist_df = provider.get_hist_data(start="2024-01-01", end="2024-12-31")

# Manual filtering
hist_df = hist_df[['timestamp', 'close', 'volume']]
hist_df = hist_df.head(100)

# Get realtime data
rt_factory = RealtimeDataFactory()
rt_provider = rt_factory.get_provider("eastmoney", symbol="600000")
rt_df = rt_provider.get_current_data()
```

**After (v0.5.0)**:

```python
# new_script.py
from akshare_one import get_hist_data_multi_source, get_realtime_data

# Get historical data with auto failover
hist_df = get_hist_data_multi_source(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31",
    sources=["eastmoney", "sina"],
    columns=['timestamp', 'close', 'volume'],
    row_filter={'top_n': 100}
)

# Get realtime data
rt_df = get_realtime_data(symbol="600000")
```

**Benefits**:
- 50% less code
- Automatic failover
- Built-in filtering
- Clearer error messages

### Upgrading to Future Versions

#### Upgrading to v0.6.0 (Planned)

**Expected changes**:

- Removal of deprecated parameter names
- Async data fetching support (optional)
- Enhanced field mapping system
- More multi-source endpoints

**Preparation**:

1. Update parameter names to standard format now
2. Test with Python 3.11+ for async compatibility
3. Review field naming in your data processing

#### Upgrading to v1.0.0 (Future Major Release)

**Expected breaking changes**:

- Complete removal of factory pattern legacy code
- Async-only API for some endpoints
- Strict field naming enforcement
- New data source architecture

**Preparation**:

1. Use top-level functions exclusively
2. Adopt multi-source routing
3. Follow field naming standards
4. Review exception handling

## General Best Practices

### 1. Pin Your Dependencies

For production code, always pin versions:

```toml
# pyproject.toml or requirements.txt
akshare-one = "0.5.0"  # Exact version
```

Or use version ranges carefully:

```toml
akshare-one = ">=0.5.0,<0.6.0"  # Allow patches only
```

**Why**:
- Avoid unexpected breaking changes
- Reproducible deployments
- Easier debugging

### 2. Use Version Control

```bash
# Before upgrade
git checkout -b upgrade-to-0.5.0

# After upgrade and testing
git commit -m "Upgrade to akshare-one 0.5.0"
git merge upgrade-to-0.5.0
```

### 3. Test in Isolation

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate

# Install new version
pip install akshare-one==0.5.0

# Run your tests
python your_script.py
pytest tests/
```

### 4. Monitor Deprecation Warnings

```python
# Run with warnings enabled
python -W all your_script.py
```

Look for:
- `DeprecationWarning: ...`
- `FutureWarning: ...`

Update code to avoid these warnings.

### 5. Read Documentation

Before upgrading:
- Read CHANGELOG.md
- Check VERSION_MATRIX.md for compatibility
- Review this UPGRADE_GUIDE.md
- Read new API documentation

## Troubleshooting

### Common Upgrade Issues

#### Issue 1: Import Errors

**Symptom**:
```python
ImportError: cannot import name 'HistoricalDataFactory' from 'akshare_one.modules.historical'
```

**Solution**:
```python
# Don't import factory directly
# Use top-level function instead
from akshare_one import get_hist_data
```

#### Issue 2: Parameter Name Errors

**Symptom**:
```python
TypeError: get_hist_data() got an unexpected keyword argument 'start'
```

**Solution**:
```python
# Use standard parameter names
df = get_hist_data(
    symbol="600000",
    start_date="2024-01-01",  # Not 'start'
    end_date="2024-12-31"     # Not 'end'
)
```

#### Issue 3: Field Name Changes

**Symptom**:
```python
KeyError: 'date'  # Field not found
```

**Solution**:
```python
# Use standardized field names
# 'date' → 'timestamp'
# 'close_price' → 'close'
df['timestamp']  # Not 'date'
df['close']      # Not 'close_price'
```

#### Issue 4: Multi-source Not Working

**Symptom**:
```python
# All sources failing, no fallback
RuntimeError: All data sources failed
```

**Solution**:
```python
# Check source availability
# Add more sources as fallback
df = get_hist_data_multi_source(
    symbol="600000",
    sources=["eastmoney", "sina", "eastmoney_direct"]  # More sources
)

# Check logs for which sources tried
import logging
logging.basicConfig(level=logging.INFO)
```

#### Issue 5: Performance Degradation

**Symptom**: Slower data fetching after upgrade

**Solution**:
```python
# Use filtering to reduce data transfer
df = get_hist_data(
    symbol="600000",
    columns=['timestamp', 'close'],  # Only needed columns
    row_filter={'top_n': 100}        # Limit rows
)

# Enable caching (default is enabled)
from akshare_one import get_hist_data_multi_source
# Daily data is cached for 24 hours
```

## Rollback Procedure

If upgrade causes issues:

### Quick Rollback

```bash
# Pin to previous version
pip install akshare-one==0.4.2

# Or in pyproject.toml
akshare-one = "0.4.2"
```

### Git Rollback

```bash
# Revert code changes
git log --oneline
git revert <upgrade-commit>

# Or reset to previous state
git reset --hard <previous-commit>
```

### Partial Rollback

If only some features cause issues:

```python
# Use old-style API for problematic parts
# (if still available)
from akshare_one.modules.historical import HistoricalDataFactory

# Keep rest of code with new API
```

## Getting Help

If you encounter issues during upgrade:

1. **Search existing issues**: [GitHub Issues](https://github.com/zwldarren/akshare-one/issues)
2. **Check documentation**: This guide, CHANGELOG, VERSION_MATRIX
3. **Ask for help**: [GitHub Discussions](https://github.com/zwldarren/akshare-one/discussions)
4. **Report bugs**: Open a new issue with:
   - Your version (`pip show akshare-one`)
   - Python version (`python --version`)
   - Error message and traceback
   - Minimal reproducing code

## Version History

| Version | Release Date | Upgrade Difficulty | Key Changes |
|---------|-------------|-------------------|-------------|
| 0.5.0 | 2026-04-04 | Medium | Factory refactor, multi-source, filtering |
| 0.4.0 | 2026-02-15 | Low | Market data extensions |
| 0.3.0 | 2026-01-20 | Low | New modules (ETF, Bond, Index) |
| 0.2.0 | 2025-12-15 | Low | Financial data, HK/US stocks |
| 0.1.0 | 2025-11-10 | Initial | Core modules |

---

**Recommendation**: Always upgrade to the latest version for best features, performance, and bug fixes. Follow this guide for smooth migration.