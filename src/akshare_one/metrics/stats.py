"""
Simple statistics collection for monitoring akshare-one usage.

This module provides lightweight statistics tracking for requests,
errors, and cache performance.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class RequestStats:
    """
    Statistics for a single data source.

    Tracks request counts, success rates, latencies, and errors.
    """

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration_ms: float = 0.0
    errors: dict[str, int] = field(default_factory=dict)
    min_duration_ms: float | None = None
    max_duration_ms: float | None = None

    @property
    def avg_duration_ms(self) -> float:
        """Average request duration in milliseconds."""
        if self.total_requests == 0:
            return 0.0
        return self.total_duration_ms / self.total_requests

    @property
    def success_rate(self) -> float:
        """Success rate as percentage (0-100)."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def error_rate(self) -> float:
        """Error rate as percentage (0-100)."""
        return 100.0 - self.success_rate

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{self.success_rate:.2f}%",
            "error_rate": f"{self.error_rate:.2f}%",
            "avg_duration_ms": f"{self.avg_duration_ms:.2f}ms",
            "min_duration_ms": f"{self.min_duration_ms:.2f}ms" if self.min_duration_ms else "N/A",
            "max_duration_ms": f"{self.max_duration_ms:.2f}ms" if self.max_duration_ms else "N/A",
            "errors_by_type": dict(self.errors),
        }


@dataclass
class CacheStats:
    """Statistics for cache performance."""

    hits: int = 0
    misses: int = 0

    @property
    def total_requests(self) -> int:
        """Total cache requests."""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Cache hit rate as percentage (0-100)."""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": self.total_requests,
            "hit_rate": f"{self.hit_rate:.2f}%",
        }


class StatsCollector:
    """
    Collector for runtime statistics.

    Collects and aggregates statistics about:
    - API requests by source
    - Success/error rates
    - Response latencies
    - Cache hit rates

    Statistics can be output to logs on a daily basis.

    Example:
        >>> collector = StatsCollector()
        >>>
        >>> # Record requests
        >>> collector.record_request("eastmoney", 150.5, success=True)
        >>> collector.record_request("eastmoney", 200.0, success=False, error_type="TimeoutError")
        >>>
        >>> # Get stats
        >>> stats = collector.get_source_stats("eastmoney")
        >>> print(stats.avg_duration_ms)
        175.25
        >>>
        >>> # Print daily summary
        >>> collector.print_daily_summary()
    """

    _instance: Optional["StatsCollector"] = None

    def __new__(cls) -> "StatsCollector":
        """Singleton pattern for global stats collector."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize stats collector."""
        if self._initialized:
            return

        self._initialized = True
        self._source_stats: dict[str, RequestStats] = defaultdict(RequestStats)
        self._cache_stats: dict[str, CacheStats] = defaultdict(CacheStats)
        self._start_time = datetime.now()
        self._last_daily_summary = datetime.now()

        # Import logger
        from ..logging_config import get_logger

        self.logger = get_logger(__name__)

    def record_request(
        self,
        source: str,
        duration_ms: float,
        success: bool,
        error_type: str | None = None,
        endpoint: str | None = None,
    ) -> None:
        """
        Record a request to a data source.

        Args:
            source: Data source name (e.g., "eastmoney")
            duration_ms: Request duration in milliseconds
            success: Whether the request succeeded
            error_type: Error type if failed (e.g., "TimeoutError")
            endpoint: Optional endpoint name
        """
        stats = self._source_stats[source]
        stats.total_requests += 1
        stats.total_duration_ms += duration_ms

        # Update min/max
        if stats.min_duration_ms is None or duration_ms < stats.min_duration_ms:
            stats.min_duration_ms = duration_ms
        if stats.max_duration_ms is None or duration_ms > stats.max_duration_ms:
            stats.max_duration_ms = duration_ms

        if success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
            if error_type:
                stats.errors[error_type] = stats.errors.get(error_type, 0) + 1

        # Log at debug level
        self.logger.debug(
            f"Recorded request to {source}",
            extra={
                "context": {
                    "source": source,
                    "endpoint": endpoint,
                    "duration_ms": round(duration_ms, 2),
                    "success": success,
                    "error_type": error_type,
                }
            },
        )

    def record_cache_hit(self, cache_name: str) -> None:
        """
        Record a cache hit.

        Args:
            cache_name: Name of the cache (e.g., "realtime_cache")
        """
        self._cache_stats[cache_name].hits += 1

    def record_cache_miss(self, cache_name: str) -> None:
        """
        Record a cache miss.

        Args:
            cache_name: Name of the cache
        """
        self._cache_stats[cache_name].misses += 1

    def get_source_stats(self, source: str) -> dict[str, Any]:
        """
        Get statistics for a specific source.

        Args:
            source: Data source name

        Returns:
            Dictionary of statistics
        """
        if source not in self._source_stats:
            return {"message": f"No statistics available for '{source}'"}
        return self._source_stats[source].to_dict()

    def get_cache_stats(self, cache_name: str) -> dict[str, Any]:
        """
        Get statistics for a specific cache.

        Args:
            cache_name: Cache name

        Returns:
            Dictionary of statistics
        """
        if cache_name not in self._cache_stats:
            return {"message": f"No statistics available for cache '{cache_name}'"}
        return self._cache_stats[cache_name].to_dict()

    def get_all_stats(self) -> dict[str, Any]:
        """
        Get all collected statistics.

        Returns:
            Dictionary with all statistics
        """
        uptime = datetime.now() - self._start_time

        return {
            "uptime": str(uptime),
            "uptime_seconds": int(uptime.total_seconds()),
            "start_time": self._start_time.isoformat(),
            "sources": {
                name: stats.to_dict() for name, stats in sorted(self._source_stats.items())
            },
            "cache": {name: stats.to_dict() for name, stats in sorted(self._cache_stats.items())},
        }

    def get_summary_text(self) -> str:
        """
        Get a text summary of statistics.

        Returns:
            Formatted text summary
        """
        stats = self.get_all_stats()
        lines = [
            "=" * 60,
            "AKSHARE-ONE DAILY STATISTICS SUMMARY",
            "=" * 60,
            f"Uptime: {stats['uptime']}",
            f"Start Time: {stats['start_time']}",
            "",
            "DATA SOURCES:",
            "-" * 60,
        ]

        for source, source_stats in stats["sources"].items():
            lines.extend(
                [
                    f"\n{source}:",
                    f"  Total Requests: {source_stats['total_requests']}",
                    f"  Success Rate: {source_stats['success_rate']}",
                    f"  Avg Duration: {source_stats['avg_duration_ms']}",
                    f"  Min Duration: {source_stats['min_duration_ms']}",
                    f"  Max Duration: {source_stats['max_duration_ms']}",
                ]
            )

            if source_stats["errors_by_type"]:
                lines.append("  Errors:")
                for error_type, count in source_stats["errors_by_type"].items():
                    lines.append(f"    - {error_type}: {count}")

        if stats["cache"]:
            lines.extend(["", "CACHE PERFORMANCE:", "-" * 60])

            for cache_name, cache_stats in stats["cache"].items():
                lines.extend(
                    [
                        f"\n{cache_name}:",
                        f"  Hit Rate: {cache_stats['hit_rate']}",
                        f"  Hits: {cache_stats['hits']}",
                        f"  Misses: {cache_stats['misses']}",
                    ]
                )

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def print_daily_summary(self, force: bool = False) -> None:
        """
        Print daily statistics summary to log.

        Args:
            force: Print even if not yet 24 hours since last summary
        """
        now = datetime.now()
        hours_since_last = (now - self._last_daily_summary).total_seconds() / 3600

        if not force and hours_since_last < 24:
            self.logger.debug(
                "Daily summary not yet due",
                extra={
                    "context": {
                        "hours_since_last": round(hours_since_last, 2),
                        "hours_until_next": round(24 - hours_since_last, 2),
                    }
                },
            )
            return

        summary_text = self.get_summary_text()
        stats = self.get_all_stats()

        self.logger.info(
            "Daily Statistics Summary", extra={"context": {"type": "daily_summary", "data": stats}}
        )

        # Also print to stdout for visibility
        print(summary_text)

        # Update last summary time
        self._last_daily_summary = now

    def reset(self) -> None:
        """
        Reset all statistics.

        This is useful for testing or when starting a new monitoring period.
        """
        self._source_stats.clear()
        self._cache_stats.clear()
        self._start_time = datetime.now()
        self._last_daily_summary = datetime.now()

        self.logger.info("Statistics reset")


# Global stats collector instance
_global_collector: StatsCollector | None = None


def get_stats_collector() -> StatsCollector:
    """
    Get the global statistics collector instance.

    Returns:
        StatsCollector singleton instance
    """
    global _global_collector
    if _global_collector is None:
        _global_collector = StatsCollector()
    return _global_collector
