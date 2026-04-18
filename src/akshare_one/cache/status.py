"""Cache status checker - inspect cache coverage and health."""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .duckdb_engine import DuckDBEngine
from .parquet_store import ParquetStore
from .schema import SCHEMA_REGISTRY

logger = logging.getLogger(__name__)


@dataclass
class CacheStatus:
    """缓存状态"""

    table: str
    has_data: bool
    partition_count: int
    file_count: int
    date_range: tuple[str, str] | None
    size_mb: float
    record_count: int


class CacheStatusChecker:
    """缓存状态检查"""

    def __init__(self, store: ParquetStore, engine: DuckDBEngine):
        self.store = store
        self.engine = engine

    def check_table(self, table: str, symbol: str | None = None) -> CacheStatus:
        """检查单个表的状态"""
        table_dir = self.store.base_dir / table
        has_data = table_dir.exists() and any(table_dir.rglob("*.parquet"))

        partitions = self.store.list_partitions(table)
        files = list(table_dir.rglob("*.parquet")) if table_dir.exists() else []
        date_range = self.store.get_date_range(table)

        size_mb = sum(f.stat().st_size for f in files) / 1024 / 1024 if files else 0.0
        record_count = self.engine.count(table, symbol) if has_data else 0

        return CacheStatus(
            table=table,
            has_data=has_data,
            partition_count=len(partitions),
            file_count=len(files),
            date_range=date_range,
            size_mb=round(size_mb, 2),
            record_count=record_count,
        )

    def check_coverage(
        self,
        table: str,
        symbol: str,
        start: str,
        end: str,
    ) -> dict:
        """检查缓存覆盖度

        Returns:
            {
                "has_data": True,
                "is_complete": False,
                "cached_count": 150,
                "total_count": 250,
                "missing_days": ["2024-02-01", ...],
                "coverage_pct": 0.60,
            }
        """
        df = self.engine.query(table, symbol=symbol, start=start, end=end)
        if df.empty:
            return {
                "has_data": False,
                "is_complete": False,
                "cached_count": 0,
                "total_count": 0,
                "missing_days": [],
                "coverage_pct": 0.0,
            }

        if "date" not in df.columns:
            return {
                "has_data": True,
                "is_complete": True,
                "cached_count": len(df),
                "total_count": len(df),
                "missing_days": [],
                "coverage_pct": 1.0,
            }

        cached_dates = set(df["date"].astype(str))

        start_dt = datetime.datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(end, "%Y-%m-%d")
        trading_days = set()
        current = start_dt
        while current <= end_dt:
            if current.weekday() < 5:
                trading_days.add(current.strftime("%Y-%m-%d"))
            current += datetime.timedelta(days=1)

        missing = sorted(trading_days - cached_dates)
        coverage = len(cached_dates) / len(trading_days) if trading_days else 1.0

        return {
            "has_data": True,
            "is_complete": len(missing) == 0,
            "cached_count": len(cached_dates),
            "total_count": len(trading_days),
            "missing_days": missing[:10],
            "coverage_pct": round(coverage, 4),
        }

    def validate_for_offline(
        self,
        symbols: list[str],
        start: str,
        end: str,
        table: str = "stock_daily",
    ) -> tuple[bool, dict]:
        """验证离线模式是否可用

        Returns:
            (is_valid, report)
            is_valid: True if all symbols have complete coverage
            report: {"missing": [...], "incomplete": [(symbol, coverage), ...]}
        """
        missing = []
        incomplete = []

        for symbol in symbols:
            coverage = self.check_coverage(table, symbol, start, end)
            if not coverage["has_data"]:
                missing.append(symbol)
            elif not coverage["is_complete"]:
                incomplete.append((symbol, coverage["coverage_pct"]))

        is_valid = not missing and not incomplete
        return is_valid, {
            "missing": missing,
            "incomplete": incomplete,
        }

    def get_summary(self) -> dict:
        """获取所有表的缓存摘要"""
        tables = {}
        total_size = 0.0
        total_records = 0

        for table_name in SCHEMA_REGISTRY:
            status = self.check_table(table_name)
            if status.has_data:
                tables[table_name] = {
                    "partition_count": status.partition_count,
                    "file_count": status.file_count,
                    "date_range": status.date_range,
                    "size_mb": status.size_mb,
                    "record_count": status.record_count,
                }
                total_size += status.size_mb
                total_records += status.record_count

        return {
            "tables": tables,
            "total_size_mb": round(total_size, 2),
            "total_records": total_records,
        }
