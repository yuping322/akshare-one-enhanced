"""
Metrics collection module for monitoring akshare-one performance.
"""

from .stats import RequestStats, StatsCollector, get_stats_collector

__all__ = ["StatsCollector", "RequestStats", "get_stats_collector"]
