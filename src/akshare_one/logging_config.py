"""
Structured logging configuration for akshare-one.

This module provides a centralized logging system with JSON format output
for better observability and debugging capabilities.
"""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in structured JSON format.

    Example output:
    {
        "timestamp": "2026-02-18T10:30:45.123Z",
        "level": "INFO",
        "error_code": "E00101001",
        "logger": "akshare_one.modules.eastmoney",
        "message": "Fetching data completed",
        "context": {
            "source": "eastmoney",
            "endpoint": "get_realtime_data",
            "symbol": "600000",
            "duration_ms": 156,
            "status": "success"
        }
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add error code if present
        if hasattr(record, "error_code"):
            log_entry["error_code"] = record.error_code

        if hasattr(record, "context"):
            log_entry["context"] = record.context
        else:
            log_entry["context"] = {}

        if record.exc_info:
            exc_info = record.exc_info
            log_entry["exception"] = {
                "type": exc_info[0].__name__ if exc_info[0] else None,
                "message": str(exc_info[1]) if exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }
            # Extract error code from exception if it's a MarketDataError
            if exc_info[1] and hasattr(exc_info[1], "error_code") and exc_info[1].error_code:
                log_entry["error_code"] = exc_info[1].error_code.value

        log_entry["location"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class ContextFilter(logging.Filter):
    """
    Filter that adds default context to log records.

    This ensures all logs have a consistent structure with default fields.
    """

    def __init__(self, default_context: dict[str, Any] | None = None):
        super().__init__()
        self.default_context = default_context or {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Add default context to record."""
        if not hasattr(record, "context"):
            record.context = {}

        record.context = {**self.default_context, **record.context}
        return True


def _get_default_log_dir() -> Path:
    return Path("/tmp") / "akshare_one" / "logs"


def setup_logging(
    log_level: str = "INFO",
    log_dir: str | None = None,
    enable_console: bool = True,
    enable_file: bool = False,
    json_format: bool = True,
    default_context: dict[str, Any] | None = None,
) -> logging.Logger:
    """
    Set up structured logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_console: Whether to output to console
        enable_file: Whether to output to file (default: False for read-only environments)
        json_format: Whether to use JSON format (True) or plain text (False)
        default_context: Default context to add to all log records

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging(log_level="DEBUG", enable_file=True)
        >>> logger.info("Data fetched", extra={"context": {"rows": 100}})
    """
    if log_dir is None:
        log_dir = _get_default_log_dir()
    else:
        log_dir = Path(log_dir)

    file_logging_enabled = False
    if enable_file:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            # Test if directory is writable
            test_file = log_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
            file_logging_enabled = True
        except (PermissionError, OSError) as e:
            import warnings

            warnings.warn(
                f"Cannot create log directory '{log_dir}': {e}. Falling back to console-only logging.",
                RuntimeWarning,
                stacklevel=2,
            )

    logger = logging.getLogger("akshare_one")
    logger.setLevel(getattr(logging, log_level.upper()))

    logger.handlers = []

    if json_format:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    context_filter = ContextFilter(default_context)
    logger.addFilter(context_filter)

    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if file_logging_enabled:
        try:
            file_handler = TimedRotatingFileHandler(
                filename=str(log_dir / "akshare_one.log"),
                when="midnight",
                interval=1,
                backupCount=7,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (PermissionError, OSError) as e:
            import warnings

            warnings.warn(
                f"Cannot create log file in '{log_dir}': {e}. Falling back to console-only logging.",
                RuntimeWarning,
                stacklevel=2,
            )

    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Operation started")
    """
    if not name.startswith("akshare_one"):
        name = f"akshare_one.{name}"

    logger = logging.getLogger(name)

    root_logger = logging.getLogger("akshare_one")
    if not root_logger.handlers:
        try:
            setup_logging()
        except Exception:
            # Ensure a working logger even if setup fails
            # Add a basic console handler as fallback
            if not root_logger.handlers:
                handler = logging.StreamHandler(sys.stdout)
                handler.setLevel(logging.INFO)
                handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
                root_logger.addHandler(handler)
                root_logger.setLevel(logging.INFO)
                root_logger.propagate = False

    return logger


class LogContext:
    """
    Context manager for adding temporary context to logs.

    Example:
        >>> logger = get_logger(__name__)
        >>> with LogContext(logger, {"request_id": "123"}):
        ...     logger.info("Processing request")
    """

    def __init__(self, logger: logging.Logger, context: dict[str, Any]):
        self.logger = logger
        self.context = context
        self.old_context = None

    def __enter__(self):
        for filter_obj in self.logger.filters:
            if isinstance(filter_obj, ContextFilter):
                self.old_context = filter_obj.default_context.copy()
                filter_obj.default_context.update(self.context)
                break
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for filter_obj in self.logger.filters:
            if isinstance(filter_obj, ContextFilter):
                if self.old_context is not None:
                    filter_obj.default_context = self.old_context
                break
        return False


def log_api_request(
    logger: logging.Logger,
    source: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
    duration_ms: float | None = None,
    status: str = "success",
    rows: int | None = None,
    error: str | None = None,
    error_code: str | None = None,
) -> None:
    """
    Log an API request with structured context.

    Args:
        logger: Logger instance
        source: Data source name (e.g., "eastmoney")
        endpoint: API endpoint or function name
        params: Request parameters
        duration_ms: Request duration in milliseconds
        status: Request status ("success", "error", "timeout")
        rows: Number of rows returned
        error: Error message if failed
        error_code: Error code if failed
    """
    context = {"log_type": "api_request", "source": source, "endpoint": endpoint, "status": status}

    if params:
        context["params"] = params
    if duration_ms is not None:
        context["duration_ms"] = round(duration_ms, 2)
    if rows is not None:
        context["rows"] = rows
    if error:
        context["error"] = error

    extra = {"context": context}
    if error_code:
        extra["error_code"] = error_code

    if status == "success":
        logger.info(f"API request to {source} completed", extra=extra)
    elif status == "error":
        logger.error(f"API request to {source} failed: {error}", extra=extra)
    else:
        logger.warning(f"API request to {source} {status}", extra=extra)


def log_data_quality(
    logger: logging.Logger,
    source: str,
    data_type: str,
    issue: str,
    details: dict[str, Any] | None = None,
) -> None:
    """
    Log a data quality issue.

    Args:
        logger: Logger instance
        source: Data source name
        data_type: Type of data (e.g., "realtime", "historical")
        issue: Description of the issue
        details: Additional details about the issue
    """
    context = {"log_type": "data_quality", "source": source, "data_type": data_type, "issue": issue}

    if details:
        context["details"] = details

    logger.warning(f"Data quality issue: {issue}", extra={"context": context})


def log_exception(
    logger: logging.Logger,
    exception: Exception,
    source: str | None = None,
    endpoint: str | None = None,
    symbol: str | None = None,
    additional_context: dict[str, Any] | None = None,
) -> None:
    """
    Log an exception with structured context and error code.

    Args:
        logger: Logger instance
        exception: Exception to log
        source: Data source name (e.g., "eastmoney")
        endpoint: API endpoint or function name
        symbol: Symbol being processed
        additional_context: Additional context information
    """
    context: dict[str, Any] = {"log_type": "exception"}

    if source:
        context["source"] = source
    if endpoint:
        context["endpoint"] = endpoint
    if symbol:
        context["symbol"] = symbol
    if additional_context:
        context.update(additional_context)

    # Extract error code from MarketDataError
    error_code = None
    if hasattr(exception, "error_code") and exception.error_code:
        error_code = exception.error_code.value
        context["error_code"] = error_code

    # Extract context from MarketDataError
    if hasattr(exception, "context") and exception.context:
        context.update(exception.context)

    extra = {"context": context}
    if error_code:
        extra["error_code"] = error_code

    logger.error(
        f"Exception occurred: {exception}",
        extra=extra,
        exc_info=True,
    )
