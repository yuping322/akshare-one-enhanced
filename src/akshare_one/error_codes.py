"""
Unified error code system for akshare-one.

This module defines a comprehensive error code enumeration that provides
unique identifiers for all error scenarios in the system.

Error code format: E{Module}{Type}{Sequence}
- Module: 3 digits (000-999)
- Type: 2 digits (00-99)
- Sequence: 2 digits (00-99)

Example: E00101001
- Module: 001 (Parameter validation)
- Type: 01 (Invalid format)
- Sequence: 001 (Symbol format error)
"""

from enum import Enum


class ErrorCode(Enum):
    """
    Error code enumeration for all error scenarios.

    Error codes are organized by module and type:
    - E001xxxx: Parameter validation errors
    - E002xxxx: Data source errors
    - E003xxxx: Network errors
    - E004xxxx: Data validation errors
    - E005xxxx: Configuration errors
    - E006xxxx: Cache errors
    - E007xxxx: Rate limiting errors
    - E008xxxx: Data processing errors
    """

    # E001xxxx: Parameter validation errors
    INVALID_SYMBOL_FORMAT = "E00101001"
    INVALID_SYMBOL_EMPTY = "E00101002"
    INVALID_SYMBOL_TYPE = "E00101003"

    INVALID_DATE_FORMAT = "E00102001"
    INVALID_DATE_RANGE = "E00102002"
    INVALID_DATE_EMPTY = "E00102003"

    INVALID_PARAMETER_TYPE = "E00103001"
    INVALID_PARAMETER_VALUE = "E00103002"
    INVALID_PARAMETER_RANGE = "E00103003"
    MISSING_REQUIRED_PARAMETER = "E00103004"

    INVALID_MARKET_TYPE = "E00104001"
    INVALID_DATA_TYPE = "E00104002"
    INVALID_SOURCE_TYPE = "E00104003"

    INVALID_COLUMNS = "E00105001"
    INVALID_FILTER = "E00105002"

    # E002xxxx: Data source errors
    SOURCE_UNAVAILABLE = "E00201001"
    SOURCE_TIMEOUT = "E00201002"
    SOURCE_CONNECTION_FAILED = "E00201003"

    SOURCE_RESPONSE_ERROR = "E00202001"
    SOURCE_PARSE_ERROR = "E00202002"
    SOURCE_SCHEMA_CHANGED = "E00202003"

    SOURCE_NO_DATA = "E00203001"
    SOURCE_EMPTY_RESPONSE = "E00203002"
    SOURCE_INVALID_RESPONSE = "E00203003"

    SOURCE_AUTH_FAILED = "E00204001"
    SOURCE_FORBIDDEN = "E00204002"
    SOURCE_NOT_FOUND = "E00204003"

    # E003xxxx: Network errors
    NETWORK_TIMEOUT = "E00301001"
    NETWORK_CONNECTION_ERROR = "E00301002"
    NETWORK_DNS_ERROR = "E00301003"
    NETWORK_SSL_ERROR = "E00301004"

    NETWORK_HTTP_400 = "E00302001"
    NETWORK_HTTP_401 = "E00302002"
    NETWORK_HTTP_403 = "E00302003"
    NETWORK_HTTP_404 = "E00302004"
    NETWORK_HTTP_429 = "E00302005"
    NETWORK_HTTP_500 = "E00302006"
    NETWORK_HTTP_502 = "E00302007"
    NETWORK_HTTP_503 = "E00302008"

    # E004xxxx: Data validation errors
    VALIDATION_TYPE_ERROR = "E00401001"
    VALIDATION_VALUE_ERROR = "E00401002"
    VALIDATION_RANGE_ERROR = "E00401003"

    VALIDATION_MISSING_FIELD = "E00402001"
    VALIDATION_INVALID_FIELD = "E00402002"
    VALIDATION_DUPLICATE_FIELD = "E00402003"

    VALIDATION_INTEGRITY_ERROR = "E00403001"
    VALIDATION_CONSTRAINT_ERROR = "E00403002"
    VALIDATION_SCHEMA_ERROR = "E00403003"

    # E005xxxx: Configuration errors
    CONFIG_MISSING = "E00501001"
    CONFIG_INVALID = "E00501002"
    CONFIG_PARSE_ERROR = "E00501003"

    CONFIG_MAPPING_NOT_FOUND = "E00502001"
    CONFIG_FIELD_NOT_FOUND = "E00502002"
    CONFIG_ALIAS_NOT_FOUND = "E00502003"

    # E006xxxx: Cache errors
    CACHE_READ_ERROR = "E00601001"
    CACHE_WRITE_ERROR = "E00601002"
    CACHE_DELETE_ERROR = "E00601003"
    CACHE_EXPIRED = "E00601004"

    # E007xxxx: Rate limiting errors
    RATE_LIMIT_EXCEEDED = "E00701001"
    RATE_LIMIT_RETRY_AFTER = "E00701002"
    RATE_LIMIT_QUOTA_EXCEEDED = "E00701003"

    # E008xxxx: Data processing errors
    PROCESSING_STANDARDIZATION_ERROR = "E00801001"
    PROCESSING_CONVERSION_ERROR = "E00801002"
    PROCESSING_FILTER_ERROR = "E00801003"

    PROCESSING_NULL_VALUE = "E00802001"
    PROCESSING_INVALID_TYPE = "E00802002"
    PROCESSING_OUT_OF_RANGE = "E00802003"

    @property
    def category(self) -> str:
        """Get the error category (first 3 digits)."""
        return self.value[1:4]

    @property
    def type_code(self) -> str:
        """Get the error type (digits 4-5)."""
        return self.value[4:6]

    @property
    def sequence(self) -> str:
        """Get the error sequence (last 3 digits)."""
        return self.value[6:]

    def __str__(self) -> str:
        """Return the error code as string."""
        return self.value


# Error code category names
ERROR_CATEGORIES = {
    "001": "Parameter Validation",
    "002": "Data Source",
    "003": "Network",
    "004": "Data Validation",
    "005": "Configuration",
    "006": "Cache",
    "007": "Rate Limiting",
    "008": "Data Processing",
}

# Error code descriptions
ERROR_DESCRIPTIONS = {
    # Parameter validation
    ErrorCode.INVALID_SYMBOL_FORMAT: "Symbol format is invalid (expected 6 digits)",
    ErrorCode.INVALID_SYMBOL_EMPTY: "Symbol is empty or None",
    ErrorCode.INVALID_SYMBOL_TYPE: "Symbol type is invalid (expected string)",
    ErrorCode.INVALID_DATE_FORMAT: "Date format is invalid (expected YYYY-MM-DD)",
    ErrorCode.INVALID_DATE_RANGE: "Date range is invalid (start_date > end_date)",
    ErrorCode.INVALID_DATE_EMPTY: "Date is empty or None",
    ErrorCode.INVALID_PARAMETER_TYPE: "Parameter type is invalid",
    ErrorCode.INVALID_PARAMETER_VALUE: "Parameter value is invalid",
    ErrorCode.INVALID_PARAMETER_RANGE: "Parameter value is out of range",
    ErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter is missing",
    ErrorCode.INVALID_MARKET_TYPE: "Market type is invalid",
    ErrorCode.INVALID_DATA_TYPE: "Data type is invalid",
    ErrorCode.INVALID_SOURCE_TYPE: "Source type is invalid",
    ErrorCode.INVALID_COLUMNS: "Columns parameter is invalid",
    ErrorCode.INVALID_FILTER: "Filter parameter is invalid",

    # Data source
    ErrorCode.SOURCE_UNAVAILABLE: "Data source is unavailable",
    ErrorCode.SOURCE_TIMEOUT: "Data source request timed out",
    ErrorCode.SOURCE_CONNECTION_FAILED: "Failed to connect to data source",
    ErrorCode.SOURCE_RESPONSE_ERROR: "Data source returned error response",
    ErrorCode.SOURCE_PARSE_ERROR: "Failed to parse data source response",
    ErrorCode.SOURCE_SCHEMA_CHANGED: "Data source schema has changed",
    ErrorCode.SOURCE_NO_DATA: "No data available from source",
    ErrorCode.SOURCE_EMPTY_RESPONSE: "Data source returned empty response",
    ErrorCode.SOURCE_INVALID_RESPONSE: "Data source returned invalid response",
    ErrorCode.SOURCE_AUTH_FAILED: "Authentication failed with data source",
    ErrorCode.SOURCE_FORBIDDEN: "Access forbidden to data source",
    ErrorCode.SOURCE_NOT_FOUND: "Resource not found in data source",

    # Network
    ErrorCode.NETWORK_TIMEOUT: "Network request timed out",
    ErrorCode.NETWORK_CONNECTION_ERROR: "Network connection failed",
    ErrorCode.NETWORK_DNS_ERROR: "DNS resolution failed",
    ErrorCode.NETWORK_SSL_ERROR: "SSL/TLS error",
    ErrorCode.NETWORK_HTTP_400: "HTTP 400 Bad Request",
    ErrorCode.NETWORK_HTTP_401: "HTTP 401 Unauthorized",
    ErrorCode.NETWORK_HTTP_403: "HTTP 403 Forbidden",
    ErrorCode.NETWORK_HTTP_404: "HTTP 404 Not Found",
    ErrorCode.NETWORK_HTTP_429: "HTTP 429 Too Many Requests",
    ErrorCode.NETWORK_HTTP_500: "HTTP 500 Internal Server Error",
    ErrorCode.NETWORK_HTTP_502: "HTTP 502 Bad Gateway",
    ErrorCode.NETWORK_HTTP_503: "HTTP 503 Service Unavailable",

    # Data validation
    ErrorCode.VALIDATION_TYPE_ERROR: "Data type validation failed",
    ErrorCode.VALIDATION_VALUE_ERROR: "Data value validation failed",
    ErrorCode.VALIDATION_RANGE_ERROR: "Data range validation failed",
    ErrorCode.VALIDATION_MISSING_FIELD: "Required field is missing",
    ErrorCode.VALIDATION_INVALID_FIELD: "Field value is invalid",
    ErrorCode.VALIDATION_DUPLICATE_FIELD: "Duplicate field found",
    ErrorCode.VALIDATION_INTEGRITY_ERROR: "Data integrity check failed",
    ErrorCode.VALIDATION_CONSTRAINT_ERROR: "Data constraint violation",
    ErrorCode.VALIDATION_SCHEMA_ERROR: "Data schema validation failed",

    # Configuration
    ErrorCode.CONFIG_MISSING: "Configuration is missing",
    ErrorCode.CONFIG_INVALID: "Configuration is invalid",
    ErrorCode.CONFIG_PARSE_ERROR: "Failed to parse configuration",
    ErrorCode.CONFIG_MAPPING_NOT_FOUND: "Field mapping not found",
    ErrorCode.CONFIG_FIELD_NOT_FOUND: "Field not found in configuration",
    ErrorCode.CONFIG_ALIAS_NOT_FOUND: "Field alias not found",

    # Cache
    ErrorCode.CACHE_READ_ERROR: "Failed to read from cache",
    ErrorCode.CACHE_WRITE_ERROR: "Failed to write to cache",
    ErrorCode.CACHE_DELETE_ERROR: "Failed to delete from cache",
    ErrorCode.CACHE_EXPIRED: "Cached data has expired",

    # Rate limiting
    ErrorCode.RATE_LIMIT_EXCEEDED: "Rate limit exceeded",
    ErrorCode.RATE_LIMIT_RETRY_AFTER: "Rate limit retry required",
    ErrorCode.RATE_LIMIT_QUOTA_EXCEEDED: "Rate limit quota exceeded",

    # Data processing
    ErrorCode.PROCESSING_STANDARDIZATION_ERROR: "Data standardization failed",
    ErrorCode.PROCESSING_CONVERSION_ERROR: "Data conversion failed",
    ErrorCode.PROCESSING_FILTER_ERROR: "Data filtering failed",
    ErrorCode.PROCESSING_NULL_VALUE: "Unexpected null value",
    ErrorCode.PROCESSING_INVALID_TYPE: "Invalid data type during processing",
    ErrorCode.PROCESSING_OUT_OF_RANGE: "Value out of range during processing",
}


def get_error_description(error_code: ErrorCode | str) -> str:
    """
    Get human-readable description for an error code.

    Args:
        error_code: ErrorCode enum or error code string

    Returns:
        Human-readable description

    Example:
        >>> get_error_description(ErrorCode.INVALID_SYMBOL_FORMAT)
        'Symbol format is invalid (expected 6 digits)'
    """
    if isinstance(error_code, str):
        # Find matching ErrorCode
        for ec in ErrorCode:
            if ec.value == error_code:
                return ERROR_DESCRIPTIONS.get(ec, "Unknown error")
        return "Unknown error"
    else:
        return ERROR_DESCRIPTIONS.get(error_code, "Unknown error")


def get_error_category_name(error_code: ErrorCode | str) -> str:
    """
    Get category name for an error code.

    Args:
        error_code: ErrorCode enum or error code string

    Returns:
        Category name

    Example:
        >>> get_error_category_name(ErrorCode.INVALID_SYMBOL_FORMAT)
        'Parameter Validation'
    """
    if isinstance(error_code, str):
        category = error_code[1:4]
    else:
        category = error_code.category

    return ERROR_CATEGORIES.get(category, "Unknown")