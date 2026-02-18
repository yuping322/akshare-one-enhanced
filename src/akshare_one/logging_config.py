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
        "logger": "akshare_one.modules.eastmoney",
        "message": "Fetching data completed",
        "context": {
            "source": "eastmoney",
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

        if hasattr(record, "context"):
            log_entry["context"] = record.context
        else:
            log_entry["context"] = {}

        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

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


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    json_format: bool = True,
    default_context: dict[str, Any] | None = None,
) -> logging.Logger:
    """
    Set up structured logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_console: Whether to output to console
        enable_file: Whether to output to file
        json_format: Whether to use JSON format (True) or plain text (False)
        default_context: Default context to add to all log records

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging(log_level="DEBUG", enable_file=True)
        >>> logger.info("Data fetched", extra={"context": {"rows": 100}})
    """
    if enable_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

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

    if enable_file:
        file_handler = TimedRotatingFileHandler(
            filename=f"{log_dir}/akshare_one.log",
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

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
        setup_logging()

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

    if status == "success":
        logger.info(f"API request to {source} completed", extra={"context": context})
    elif status == "error":
        logger.error(f"API request to {source} failed: {error}", extra={"context": context})
    else:
        logger.warning(f"API request to {source} {status}", extra={"context": context})


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
