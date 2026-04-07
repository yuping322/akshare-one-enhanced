# Error Codes Reference

This document provides a comprehensive reference for all error codes in the akshare-one system.

## Error Code Format

Error codes follow the format: `E{Module}{Type}{Sequence}`

- **Module**: 3 digits (000-999) - Identifies the module/category
- **Type**: 2 digits (00-99) - Identifies the error type within the module
- **Sequence**: 2 digits (00-99) - Unique sequence number

Example: `E00101001`
- Module: `001` (Parameter Validation)
- Type: `01` (Invalid Format)
- Sequence: `001` (Symbol Format Error)

## Error Categories

| Category Code | Category Name          | Description                              |
|--------------|------------------------|------------------------------------------|
| E001xxx      | Parameter Validation   | Invalid input parameters                 |
| E002xxx      | Data Source            | Data source availability and response    |
| E003xxx      | Network                | Network connectivity and HTTP errors     |
| E004xxx      | Data Validation        | Data quality and integrity checks        |
| E005xxx      | Configuration          | Configuration and mapping errors         |
| E006xxx      | Cache                  | Cache read/write errors                  |
| E007xxx      | Rate Limiting          | API rate limit violations                |
| E008xxx      | Data Processing        | Data transformation errors               |

---

## E001xxx: Parameter Validation Errors

### E00101xxx: Symbol Validation

| Error Code  | Name                    | Description                                      | Solution                                      |
|------------|-------------------------|--------------------------------------------------|-----------------------------------------------|
| E00101001  | INVALID_SYMBOL_FORMAT   | Symbol format is invalid (expected 6 digits)     | Ensure symbol is 6-digit string (e.g., "600000") |
| E00101002  | INVALID_SYMBOL_EMPTY    | Symbol is empty or None                          | Provide a valid symbol parameter              |
| E00101003  | INVALID_SYMBOL_TYPE     | Symbol type is invalid (expected string)         | Pass symbol as string type                    |

**Example:**
```python
# ❌ Wrong: Invalid symbol format
get_hist_data("ABC")  # Raises E00101001

# ✅ Correct: Valid 6-digit symbol
get_hist_data("600000")
```

### E00102xxx: Date Validation

| Error Code  | Name                    | Description                                      | Solution                                      |
|------------|-------------------------|--------------------------------------------------|-----------------------------------------------|
| E00102001  | INVALID_DATE_FORMAT     | Date format is invalid (expected YYYY-MM-DD)     | Use YYYY-MM-DD format for dates               |
| E00102002  | INVALID_DATE_RANGE      | Date range is invalid (start_date > end_date)    | Ensure start_date <= end_date                 |
| E00102003  | INVALID_DATE_EMPTY      | Date is empty or None                            | Provide valid date strings                    |

**Example:**
```python
# ❌ Wrong: Invalid date format
get_hist_data("600000", start_date="2024/01/01")  # Raises E00102001

# ❌ Wrong: Invalid date range
get_hist_data("600000", start_date="2024-12-31", end_date="2024-01-01")  # Raises E00102002

# ✅ Correct: Valid date format and range
get_hist_data("600000", start_date="2024-01-01", end_date="2024-12-31")
```

### E00103xxx: General Parameter Validation

| Error Code  | Name                       | Description                                  | Solution                                  |
|------------|----------------------------|----------------------------------------------|-------------------------------------------|
| E00103001  | INVALID_PARAMETER_TYPE     | Parameter type is invalid                    | Check parameter type matches expectation  |
| E00103002  | INVALID_PARAMETER_VALUE    | Parameter value is invalid                   | Provide valid parameter value             |
| E00103003  | INVALID_PARAMETER_RANGE    | Parameter value is out of range              | Ensure parameter is within valid range    |
| E00103004  | MISSING_REQUIRED_PARAMETER | Required parameter is missing                | Provide all required parameters           |

**Example:**
```python
# ❌ Wrong: Missing required parameter
get_hist_data()  # Raises E00103004 (symbol required)

# ❌ Wrong: Invalid parameter range
get_hist_data("600000", interval_multiplier=-1)  # Raises E00103003

# ✅ Correct: All required parameters provided
get_hist_data("600000")
```

### E00104xxx: Type Validation

| Error Code  | Name                  | Description                              | Solution                              |
|------------|-----------------------|------------------------------------------|---------------------------------------|
| E00104001  | INVALID_MARKET_TYPE   | Market type is invalid                   | Use valid MarketType enum value       |
| E00104002  | INVALID_DATA_TYPE     | Data type is invalid                     | Use valid data type string            |
| E00104003  | INVALID_SOURCE_TYPE   | Source type is invalid                   | Use valid source name                 |

### E00105xxx: Filter/Column Validation

| Error Code  | Name            | Description                          | Solution                          |
|------------|-----------------|--------------------------------------|-----------------------------------|
| E00105001  | INVALID_COLUMNS | Columns parameter is invalid         | Provide valid column name list    |
| E00105002  | INVALID_FILTER  | Filter parameter is invalid          | Use valid filter dictionary       |

---

## E002xxx: Data Source Errors

### E00201xxx: Source Availability

| Error Code  | Name                      | Description                              | Solution                              |
|------------|---------------------------|------------------------------------------|---------------------------------------|
| E00201001  | SOURCE_UNAVAILABLE        | Data source is unavailable               | Check source status, try again later  |
| E00201002  | SOURCE_TIMEOUT            | Data source request timed out            | Increase timeout or try again         |
| E00201003  | SOURCE_CONNECTION_FAILED  | Failed to connect to data source         | Check network connection              |

**Solution Steps:**
1. Check if data source service is running
2. Verify network connectivity
3. Try alternative data source using multi-source API
4. Check firewall/proxy settings

### E00202xxx: Source Response

| Error Code  | Name                    | Description                              | Solution                              |
|------------|-------------------------|------------------------------------------|---------------------------------------|
| E00202001  | SOURCE_RESPONSE_ERROR   | Data source returned error response      | Check error message for details       |
| E00202002  | SOURCE_PARSE_ERROR      | Failed to parse data source response     | Data format changed, update needed    |
| E00202003  | SOURCE_SCHEMA_CHANGED   | Data source schema has changed           | Contact support for schema update     |

**When to contact support:**
- Repeated `E00202003` errors indicate upstream API changes
- Provide error code, symbol, and timestamp in support ticket

### E00203xxx: Data Availability

| Error Code  | Name                    | Description                              | Solution                              |
|------------|-------------------------|------------------------------------------|---------------------------------------|
| E00203001  | SOURCE_NO_DATA          | No data available from source            | Check symbol validity, try different date range |
| E00203002  | SOURCE_EMPTY_RESPONSE   | Data source returned empty response      | Verify request parameters             |
| E00203003  | SOURCE_INVALID_RESPONSE | Data source returned invalid response    | Try alternative data source           |

### E00204xxx: Authentication/Authorization

| Error Code  | Name               | Description                          | Solution                          |
|------------|--------------------|--------------------------------------|-----------------------------------|
| E00204001  | SOURCE_AUTH_FAILED | Authentication failed                | Check credentials/API key         |
| E00204002  | SOURCE_FORBIDDEN   | Access forbidden to data source      | Check permissions/access rights   |
| E00204003  | SOURCE_NOT_FOUND   | Resource not found in data source    | Verify symbol/resource exists     |

---

## E003xxx: Network Errors

### E00301xxx: Network Connectivity

| Error Code  | Name                      | Description                          | Solution                          |
|------------|---------------------------|--------------------------------------|-----------------------------------|
| E00301001  | NETWORK_TIMEOUT           | Network request timed out            | Increase timeout setting          |
| E00301002  | NETWORK_CONNECTION_ERROR  | Network connection failed            | Check internet connection         |
| E00301003  | NETWORK_DNS_ERROR         | DNS resolution failed                | Check DNS settings/hostname       |
| E00301004  | NETWORK_SSL_ERROR         | SSL/TLS error                        | Check SSL certificate/proxy       |

### E00302xxx: HTTP Status Codes

| Error Code  | Name              | Description                      | Solution                      |
|------------|-------------------|----------------------------------|-------------------------------|
| E00302001  | NETWORK_HTTP_400  | HTTP 400 Bad Request             | Fix request parameters        |
| E00302002  | NETWORK_HTTP_401  | HTTP 401 Unauthorized            | Provide valid credentials     |
| E00302003  | NETWORK_HTTP_403  | HTTP 403 Forbidden               | Check access permissions      |
| E00302004  | NETWORK_HTTP_404  | HTTP 404 Not Found               | Verify resource URL/symbol    |
| E00302005  | NETWORK_HTTP_429  | HTTP 429 Too Many Requests       | Implement retry with backoff  |
| E00302006  | NETWORK_HTTP_500  | HTTP 500 Internal Server Error   | Try again later               |
| E00302007  | NETWORK_HTTP_502  | HTTP 502 Bad Gateway             | Try alternative source        |
| E00302008  | NETWORK_HTTP_503  | HTTP 503 Service Unavailable     | Try again later               |

---

## E004xxx: Data Validation Errors

### E00401xxx: Value Validation

| Error Code  | Name                   | Description                          | Solution                          |
|------------|------------------------|--------------------------------------|-----------------------------------|
| E00401001  | VALIDATION_TYPE_ERROR  | Data type validation failed          | Check data type matches schema    |
| E00401002  | VALIDATION_VALUE_ERROR | Data value validation failed         | Check value is valid (e.g., non-negative) |
| E00401003  | VALIDATION_RANGE_ERROR | Data range validation failed         | Ensure value is within bounds     |

**Common causes:**
- Negative stock prices
- Out-of-range percentages (>100% or <-100%)
- Invalid data types (string where number expected)

### E00402xxx: Field Validation

| Error Code  | Name                      | Description                          | Solution                          |
|------------|---------------------------|--------------------------------------|-----------------------------------|
| E00402001  | VALIDATION_MISSING_FIELD  | Required field is missing            | Check data completeness           |
| E00402002  | VALIDATION_INVALID_FIELD  | Field value is invalid               | Validate field values             |
| E00402003  | VALIDATION_DUPLICATE_FIELD | Duplicate field found               | Check for duplicate columns       |

### E00403xxx: Integrity Validation

| Error Code  | Name                        | Description                      | Solution                      |
|------------|------------------------------|----------------------------------|-------------------------------|
| E00403001  | VALIDATION_INTEGRITY_ERROR   | Data integrity check failed      | Verify data relationships     |
| E00403002  | VALIDATION_CONSTRAINT_ERROR  | Data constraint violation        | Check business rules          |
| E00403003  | VALIDATION_SCHEMA_ERROR      | Data schema validation failed    | Verify data structure         |

---

## E005xxx: Configuration Errors

### E00501xxx: Configuration Missing/Invalid

| Error Code  | Name               | Description                      | Solution                      |
|------------|--------------------|----------------------------------|-------------------------------|
| E00501001  | CONFIG_MISSING     | Configuration is missing         | Check configuration file      |
| E00501002  | CONFIG_INVALID     | Configuration is invalid         | Validate config values        |
| E00501003  | CONFIG_PARSE_ERROR | Failed to parse configuration    | Fix config syntax errors      |

### E00502xxx: Mapping/Field Configuration

| Error Code  | Name                      | Description                          | Solution                          |
|------------|---------------------------|--------------------------------------|-----------------------------------|
| E00502001  | CONFIG_MAPPING_NOT_FOUND  | Field mapping not found              | Check mapping configuration       |
| E00502002  | CONFIG_FIELD_NOT_FOUND    | Field not found in configuration     | Verify field name in config       |
| E00502003  | CONFIG_ALIAS_NOT_FOUND    | Field alias not found                | Check alias definitions           |

---

## E006xxx: Cache Errors

| Error Code  | Name               | Description                      | Solution                      |
|------------|--------------------|----------------------------------|-------------------------------|
| E00601001  | CACHE_READ_ERROR   | Failed to read from cache        | Check cache permissions       |
| E00601002  | CACHE_WRITE_ERROR  | Failed to write to cache         | Check disk space/permissions  |
| E00601003  | CACHE_DELETE_ERROR | Failed to delete from cache      | Check cache file exists       |
| E00601004  | CACHE_EXPIRED      | Cached data has expired          | Refresh data from source      |

---

## E007xxx: Rate Limiting Errors

| Error Code  | Name                       | Description                              | Solution                              |
|------------|----------------------------|------------------------------------------|---------------------------------------|
| E00701001  | RATE_LIMIT_EXCEEDED        | Rate limit exceeded                      | Implement retry with exponential backoff |
| E00701002  | RATE_LIMIT_RETRY_AFTER     | Rate limit retry required                | Wait specified retry_after duration   |
| E00701003  | RATE_LIMIT_QUOTA_EXCEEDED  | Rate limit quota exceeded                | Reduce request frequency              |

**Best practices:**
1. Use multi-source API to distribute load across sources
2. Implement request caching for frequently accessed data
3. Add retry logic with exponential backoff
4. Monitor quota usage and adjust request patterns

---

## E008xxx: Data Processing Errors

### E00801xxx: Processing Failures

| Error Code  | Name                              | Description                          | Solution                          |
|------------|-----------------------------------|--------------------------------------|-----------------------------------|
| E00801001  | PROCESSING_STANDARDIZATION_ERROR  | Data standardization failed          | Check data format                 |
| E00801002  | PROCESSING_CONVERSION_ERROR       | Data conversion failed               | Verify conversion logic           |
| E00801003  | PROCESSING_FILTER_ERROR           | Data filtering failed                | Check filter syntax               |

### E00802xxx: Value Processing

| Error Code  | Name                      | Description                          | Solution                          |
|------------|---------------------------|--------------------------------------|-----------------------------------|
| E00802001  | PROCESSING_NULL_VALUE     | Unexpected null value                | Handle null values in data        |
| E00802002  | PROCESSING_INVALID_TYPE   | Invalid data type during processing  | Check type conversions            |
| E00802003  | PROCESSING_OUT_OF_RANGE   | Value out of range during processing | Validate value ranges             |

---

## Usage Examples

### Example 1: Catching Specific Error Codes

```python
from akshare_one import get_hist_data
from akshare_one.modules.exceptions import InvalidParameterError

try:
    df = get_hist_data("ABC")  # Invalid symbol format
except InvalidParameterError as e:
    if e.error_code and e.error_code.value == "E00101001":
        print(f"Invalid symbol format: {e}")
        # Handle symbol format error specifically
    else:
        print(f"Other parameter error: {e}")
```

### Example 2: Multi-Source Error Handling

```python
from akshare_one import get_hist_data_multi_source
from akshare_one.modules.exceptions import DataSourceUnavailableError

try:
    df = get_hist_data_multi_source("600000")
except DataSourceUnavailableError as e:
    print(f"Error code: {e.error_code}")
    print(f"Context: {e.context}")
    # Error code: E00201001
    # Context: {'source': 'eastmoney', 'endpoint': 'get_hist_data'}
```

### Example 3: Logging with Error Codes

```python
from akshare_one import get_realtime_data
from akshare_one.logging_config import get_logger, log_exception

logger = get_logger(__name__)

try:
    df = get_realtime_data("600000")
except Exception as e:
    # Log exception with error code
    log_exception(
        logger,
        e,
        source="eastmoney",
        endpoint="get_realtime_data",
        symbol="600000"
    )
    # Log entry includes error_code field for tracking
```

### Example 4: Checking Error Category

```python
from akshare_one.error_codes import ErrorCode, get_error_category_name

error_code = ErrorCode.INVALID_SYMBOL_FORMAT

# Get category name
category = get_error_category_name(error_code)
print(category)  # "Parameter Validation"

# Get description
from akshare_one.error_codes import get_error_description
description = get_error_description(error_code)
print(description)  # "Symbol format is invalid (expected 6 digits)"
```

---

## Error Handling Best Practices

1. **Always check error_code**: Use error codes to identify specific error types
2. **Use multi-source APIs**: Automatically fallback to alternative sources
3. **Log error codes**: Include error codes in logs for better debugging
4. **Handle by category**: Group error handling by category (network, validation, etc.)
5. **Provide context**: Include symbol, source, endpoint in error context

---

## Support

When contacting support about an error:
1. Provide the **error code** (e.g., `E00202003`)
2. Include **context** (symbol, source, endpoint)
3. Share **timestamp** when error occurred
4. Attach **full error message** with stack trace

This information helps quickly identify and resolve the issue.