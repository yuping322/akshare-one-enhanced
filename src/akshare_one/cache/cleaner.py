"""TTL cleaner - remove expired cache partitions."""

from __future__ import annotations

import logging
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from .config import DEFAULT_CONFIG
from .parquet_store import ParquetStore
from .schema import SCHEMA_REGISTRY

logger = logging.getLogger(__name__)


class TTLCleaner:
    """清理过期分区"""

    def __init__(self, store: ParquetStore):
        self.store = store

    def clean_table(self, table: str, now: datetime | None = None) -> int:
        """清理表的过期分区"""
        table_config = DEFAULT_CONFIG.get_table_config(table)

        if table_config.ttl_hours == 0:
            return 0

        now = now or datetime.now()
        cutoff = now - timedelta(hours=table_config.ttl_hours)
        cutoff_str = cutoff.strftime("%Y-%m-%d")

        cleaned = 0
        table_dir = self.store.base_dir / table
        if not table_dir.exists():
            return 0

        for partition_dir in table_dir.iterdir():
            if not partition_dir.is_dir():
                continue

            match = re.search(r"(\d{4}-\d{2}-\d{2})", partition_dir.name)
            if not match:
                continue

            partition_date = match.group(1)
            if partition_date < cutoff_str:
                shutil.rmtree(partition_dir)
                cleaned += 1
                logger.info("Cleaned expired partition: %s/%s", table, partition_dir.name)

        return cleaned

    def clean_all(self) -> dict[str, int]:
        """清理所有表的过期分区"""
        results = {}
        for table_name in SCHEMA_REGISTRY:
            cleaned = self.clean_table(table_name)
            if cleaned > 0:
                results[table_name] = cleaned
        return results

    def clean_directory(self, directory: Path, max_age_hours: int) -> int:
        """清理目录下超过指定时间的文件"""
        if not directory.exists():
            return 0

        now = datetime.now()
        cutoff = now - timedelta(hours=max_age_hours)
        cleaned = 0

        for f in directory.rglob("*.parquet"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                f.unlink()
                cleaned += 1

        for d in sorted(directory.rglob("*"), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()

        return cleaned
