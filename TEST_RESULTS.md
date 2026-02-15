# Test Results Summary

## Test Execution Date
2026-02-15

## Overall Results
- **Total Tests Run**: 185 (excluding MCP tests)
- **Passed**: 144
- **Failed**: 4
- **Skipped**: 37
- **Test Coverage**: 66%

## Failing Tests

### 1. `test_insider.py::TestInnerTradeData::test_basic_inner_trade`
**Status**: FAILED  
**Error**: `assert not True` (DataFrame is empty)  
**Root Cause**: The insider trade data API returned empty results for symbol "600405". This could be because:
- No recent insider trading activity for this stock
- API data availability issues
- Symbol-specific data limitation

**Impact**: Medium - The API works but may return empty data for certain stocks

### 2. `test_insider.py::TestInnerTradeData::test_transaction_value_calculation`
**Status**: FAILED  
**Error**: `IndexError: single positional indexer is out-of-bounds`  
**Root Cause**: Attempts to access first row (`df.iloc[0]`) when DataFrame is empty  
**Impact**: Medium - Cascading failure from test #1

### 3. `test_stock.py::TestRealtimeData::test_historical_data_api_error`
**Status**: FAILED  
**Error**: `Failed: DID NOT RAISE <class 'Exception'>`  
**Root Cause**: The test patches `EastMoneyHistorical.get_hist_data` but the default source for `get_hist_data` is `eastmoney_direct`, not `eastmoney`. The mock is targeting the wrong provider.  
**Impact**: Low - Test infrastructure issue, not a production code issue

### 4. `test_stock.py::TestRealtimeData::test_xueqiu_source`
**Status**: FAILED  
**Error**: `KeyError: 'data'`  
**Root Cause**: The upstream AKShare library's `stock_individual_spot_xq` function expects a specific JSON response format with a 'data' key, but the API response format has changed or is unavailable.  
**Impact**: High - Xueqiu data source is currently broken

## Examples Test Results

### Example 1: Batch Realtime Data ✓ PASS
- Successfully retrieved realtime data for 5 stocks
- Source: `eastmoney`
- All expected columns present

### Example 2: SMA Calculation ✓ PASS
- Historical data retrieved successfully (757 rows)
- SMA calculations working correctly for 5, 20, and 60-day windows
- Proper NaN handling for initial periods

### Example 3: Insider Trade Data ❌ FAIL
- API returns empty DataFrame for symbol "600405"
- Column structure is correct
- May be symbol-specific or time-dependent issue

### Example 4: Xueqiu Realtime Data ❌ FAIL
- KeyError: 'data' in upstream AKShare library
- API response format mismatch
- Requires error handling improvement

## Issues Identified

### Critical Issues
1. **Xueqiu realtime data source broken** - API format change in upstream akshare library
   - File: `src/akshare_one/modules/realtime/xueqiu.py`
   - Needs: Error handling for missing 'data' key

### Medium Issues
2. **Empty insider trade data** - Tests fail when no data available
   - Files: `tests/test_insider.py`
   - Needs: Better handling of empty results or different test symbol

3. **Incorrect mock target in test** - Test infrastructure issue
   - File: `tests/test_stock.py::test_historical_data_api_error`
   - Needs: Update mock path to match actual default source

### Low Issues
4. **MCP module import error** - Missing optional dependency
   - File: `tests/test_mcp.py`
   - Needs: Skip tests when fastmcp not installed

## Recommendations

### Immediate Fixes Needed
1. Add error handling in xueqiu.py for API format changes
2. Update test_stock.py to mock the correct provider
3. Update test_insider.py to handle empty data gracefully
4. Add pytest skip decorator for MCP tests when dependency missing

### Long-term Improvements
1. Add retry logic for API failures
2. Implement better error messages for data source issues
3. Add integration tests that can handle API unavailability
4. Document known limitations of different data sources

## Code Quality Metrics
- **Test Coverage**: 66%
- **Passed Test Rate**: 97.3% (144/148 non-skipped tests)
- **Code Complexity**: Within acceptable limits
- **Documentation**: Comprehensive docstrings present

## Conclusion
The codebase is generally in good shape with most functionality working correctly. The main issues are:
1. External API dependency issues (Xueqiu)
2. Test infrastructure improvements needed
3. Better handling of empty data scenarios

The core functionality (historical data, realtime data from eastmoney, indicators) all work correctly as demonstrated by the passing tests and examples.
