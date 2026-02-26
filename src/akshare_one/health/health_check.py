"""
Health check system for monitoring data source availability.

This module provides functionality to check the health status of various
data sources used by akshare-one.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class HealthStatus(Enum):
    """Health status levels for data sources."""

    HEALTHY = "healthy"
    """Data source is working normally (latency < 1000ms)"""

    DEGRADED = "degraded"
    """Data source is slow but functional (1000ms < latency < 5000ms)"""

    UNHEALTHY = "unhealthy"
    """Data source is not responding or returning errors"""

    UNKNOWN = "unknown"
    """Health status has not been checked yet"""


@dataclass
class HealthResult:
    """
    Result of a health check for a data source.

    Attributes:
        source: Name of the data source
        status: Current health status
        latency_ms: Response time in milliseconds
        timestamp: When the check was performed
        error: Error message if unhealthy
        details: Additional details about the check
        rows_returned: Number of rows returned (if applicable)
    """

    source: str
    status: HealthStatus
    latency_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    rows_returned: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert health result to dictionary."""
        result = {
            "source": self.source,
            "status": self.status.value,
            "latency_ms": round(self.latency_ms, 2),
            "timestamp": self.timestamp,
        }

        if self.error:
            result["error"] = self.error
        if self.details:
            result["details"] = self.details
        if self.rows_returned is not None:
            result["rows_returned"] = self.rows_returned

        return result

    def __str__(self) -> str:
        """String representation of health result."""
        status_emoji = {
            HealthStatus.HEALTHY: "✓",
            HealthStatus.DEGRADED: "⚠",
            HealthStatus.UNHEALTHY: "✗",
            HealthStatus.UNKNOWN: "?",
        }
        emoji = status_emoji.get(self.status, "?")
        return f"{emoji} {self.source}: {self.status.value} ({self.latency_ms:.0f}ms)"


class HealthChecker:
    """
    Health checker for monitoring data source availability.

    This class provides methods to check the health status of various
    data sources and maintain a history of health checks.

    Example:
        >>> checker = HealthChecker()
        >>>
        >>> # Register health check functions
        >>> checker.register_check("eastmoney", check_eastmoney_health)
        >>> checker.register_check("sina", check_sina_health)
        >>>
        >>> # Check all sources
        >>> results = checker.check_all()
        >>> for result in results.values():
        ...     print(result)
        ✓ eastmoney: healthy (156ms)
        ⚠ sina: degraded (2345ms)
    """

    def __init__(self):
        """Initialize health checker."""
        self._checks: dict[str, Callable[[], HealthResult]] = {}
        self._results: dict[str, list[HealthResult]] = {}
        self._max_history = 100

        self.logger = logging.getLogger("akshare_one.health")

    def register_check(self, source: str, check_func: Callable[[], HealthResult]) -> None:
        """
        Register a health check function for a data source.

        Args:
            source: Name of the data source
            check_func: Function that performs the health check

        Example:
            >>> def check_eastmoney():
            ...     # Perform health check
            ...     return HealthResult(...)
            >>> checker.register_check("eastmoney", check_eastmoney)
        """
        self._checks[source] = check_func
        self._results[source] = []
        self.logger.debug(
            f"Registered health check for {source}",
            extra={"context": {"source": source, "action": "register_check"}},
        )

    def check_source(self, source: str) -> HealthResult:
        """
        Check health of a specific data source.

        Args:
            source: Name of the data source

        Returns:
            HealthResult: Result of the health check

        Raises:
            KeyError: If source is not registered
        """
        if source not in self._checks:
            raise KeyError(f"No health check registered for '{source}'")

        self.logger.info(
            f"Checking health of {source}",
            extra={"context": {"source": source, "action": "health_check_start"}},
        )

        try:
            result = self._checks[source]()

            if source not in self._results:
                self._results[source] = []
            self._results[source].append(result)

            if len(self._results[source]) > self._max_history:
                self._results[source] = self._results[source][-self._max_history :]

            self.logger.info(f"Health check completed for {source}", extra={"context": result.to_dict()})

            return result

        except Exception as e:
            result = HealthResult(
                source=source,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                error=f"Health check failed: {str(e)}",
            )

            self.logger.error(
                f"Health check failed for {source}",
                extra={"context": result.to_dict()},
                exc_info=True,
            )

            return result

    def check_all(self) -> dict[str, HealthResult]:
        """
        Check health of all registered data sources.

        Returns:
            Dict mapping source names to HealthResult
        """
        results = {}

        self.logger.info(
            "Starting health check for all sources",
            extra={"context": {"sources": list(self._checks.keys())}},
        )

        for source in self._checks:
            results[source] = self.check_source(source)

        healthy_count = sum(1 for r in results.values() if r.status == HealthStatus.HEALTHY)
        total_count = len(results)

        self.logger.info(
            f"Health check completed: {healthy_count}/{total_count} sources healthy",
            extra={
                "context": {
                    "healthy": healthy_count,
                    "total": total_count,
                    "results": {k: v.to_dict() for k, v in results.items()},
                }
            },
        )

        return results

    def get_status(self, source: str) -> HealthStatus | None:
        """
        Get the last known health status of a source.

        Args:
            source: Name of the data source

        Returns:
            Last known HealthStatus or None if never checked
        """
        if source not in self._results or not self._results[source]:
            return HealthStatus.UNKNOWN
        return self._results[source][-1].status

    def get_history(self, source: str, limit: int = 10) -> list[HealthResult]:
        """
        Get health check history for a source.

        Args:
            source: Name of the data source
            limit: Maximum number of results to return

        Returns:
            List of HealthResult objects (most recent first)
        """
        if source not in self._results:
            return []
        return self._results[source][-limit:][::-1]

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of all health checks.

        Returns:
            Dict with summary statistics
        """
        summary = {"total_sources": len(self._checks), "sources": {}}

        for source, results in self._results.items():
            if results:
                latest = results[-1]
                summary["sources"][source] = {
                    "status": latest.status.value,
                    "latency_ms": round(latest.latency_ms, 2),
                    "last_check": latest.timestamp,
                    "error": latest.error,
                }
            else:
                summary["sources"][source] = {
                    "status": HealthStatus.UNKNOWN.value,
                    "last_check": None,
                }

        return summary


def create_eastmoney_health_check() -> Callable[[], HealthResult]:
    """
    Create a health check function for EastMoney data source.

    Returns:
        Health check function
    """

    def check() -> HealthResult:
        start_time = time.time()

        try:
            import akshare as ak

            raw_df = ak.stock_zh_a_spot_em()

            latency_ms = (time.time() - start_time) * 1000

            if raw_df.empty:
                return HealthResult(
                    source="eastmoney",
                    status=HealthStatus.DEGRADED,
                    latency_ms=latency_ms,
                    error="Empty data returned",
                    rows_returned=0,
                )

            if latency_ms < 1000:
                status = HealthStatus.HEALTHY
            elif latency_ms < 5000:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY

            return HealthResult(
                source="eastmoney",
                status=status,
                latency_ms=latency_ms,
                rows_returned=len(raw_df),
                details={"sample_symbols": list(raw_df["代码"].head(5)) if "代码" in raw_df.columns else []},
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthResult(
                source="eastmoney",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                error=str(e),
            )

    return check


def create_sina_health_check() -> Callable[[], HealthResult]:
    """
    Create a health check function for Sina data source.

    Returns:
        Health check function
    """

    def check() -> HealthResult:
        start_time = time.time()

        try:
            import akshare as ak

            raw_df = ak.stock_zh_a_hist(
                symbol="600000",
                period="daily",
                start_date="20260101",
                end_date="20260218",
                adjust="",
            )

            latency_ms = (time.time() - start_time) * 1000

            if raw_df.empty:
                return HealthResult(
                    source="sina",
                    status=HealthStatus.DEGRADED,
                    latency_ms=latency_ms,
                    error="Empty data returned",
                    rows_returned=0,
                )

            if latency_ms < 1000:
                status = HealthStatus.HEALTHY
            elif latency_ms < 5000:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY

            return HealthResult(source="sina", status=status, latency_ms=latency_ms, rows_returned=len(raw_df))

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthResult(source="sina", status=HealthStatus.UNHEALTHY, latency_ms=latency_ms, error=str(e))

    return check


def create_default_health_checker() -> HealthChecker:
    """
    Create a health checker with default checks for common data sources.

    Returns:
        Configured HealthChecker instance
    """
    checker = HealthChecker()

    checker.register_check("eastmoney", create_eastmoney_health_check())
    checker.register_check("sina", create_sina_health_check())

    return checker
