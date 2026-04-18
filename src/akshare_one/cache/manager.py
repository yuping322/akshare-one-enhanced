"""CacheManager - unified entry point for memory + parquet + DuckDB cache."""

from __future__ import annotations

import logging
import shutil
import threading
from pathlib import Path

import pandas as pd
from cachetools import TTLCache

from .config import CacheConfig
from .duckdb_engine import DuckDBEngine
from .normalizer import SymbolNormalizer
from .parquet_store import ParquetStore
from .schema import SCHEMA_REGISTRY

logger = logging.getLogger(__name__)


class CacheManager:
    """统一缓存管理器 — 组合 Memory + Parquet + DuckDB"""

    _instance: CacheManager | None = None
    _lock = threading.Lock()

    def __init__(self, config: CacheConfig | None = None):
        self.config = config or CacheConfig()

        self.memory: TTLCache = TTLCache(
            maxsize=self.config.memory_cache_max_items,
            ttl=self.config.memory_cache_default_ttl_seconds,
        )
        self.memory_lock = threading.Lock()

        self.store = ParquetStore(self.config.base_dir, self.config)
        self.engine = DuckDBEngine(self.config.base_dir, self.config)

    @classmethod
    def get_instance(cls, config: CacheConfig | None = None) -> CacheManager:
        """Get or create singleton CacheManager instance.

        Args:
            config: Optional cache configuration.

        Returns:
            CacheManager singleton instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        with cls._lock:
            cls._instance = None

    def get(
        self,
        table: str,
        symbol: str | None = None,
        start: str | None = None,
        end: str | None = None,
        columns: list[str] | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """查询：Memory → DuckDB(Parquet) → 空

        Args:
            table: Table name.
            symbol: Stock symbol filter.
            start: Start date filter.
            end: End date filter.
            columns: Column list to select.
            force_refresh: Skip memory cache if True.

        Returns:
            DataFrame with cached data, or empty DataFrame.
        """
        if not force_refresh:
            key = self._make_key(table, symbol, start, end)
            with self.memory_lock:
                try:
                    result = self.memory[key]
                    logger.debug("Memory cache hit for table=%s", table)
                    return result.copy()
                except KeyError:
                    pass

        if symbol:
            symbol = SymbolNormalizer.normalize(symbol)

        df = self.engine.query(table, symbol, start, end, columns)

        if not df.empty:
            key = self._make_key(table, symbol, start, end)
            with self.memory_lock:
                self.memory[key] = df

        return df

    def put(
        self,
        table: str,
        data: pd.DataFrame,
        partition_value: str | None = None,
    ) -> str:
        """写入：Parquet + 内存

        Args:
            table: Table name.
            data: DataFrame to write.
            partition_value: Partition value (e.g. date string).

        Returns:
            Path to written file, or empty string if data is empty.
        """
        if data.empty:
            logger.debug("Empty DataFrame for table=%s, skipping write", table)
            return ""

        path = self.store.write(table, data, partition_value)

        key = self._make_key(table, None, None, None)
        with self.memory_lock:
            self.memory[key] = data

        logger.info("Wrote table=%s to %s", table, path)
        return str(path)

    def put_batch(
        self,
        table: str,
        data: pd.DataFrame,
        partition_col: str,
    ) -> int:
        """批量写入：按某列拆分到多个分区

        Args:
            table: Table name.
            data: DataFrame to write.
            partition_col: Column name to split by.

        Returns:
            Number of partitions written.
        """
        if data.empty:
            return 0

        count = self.store.write_batch(table, data, partition_col)

        key = f"{table}:batch:{partition_col}"
        with self.memory_lock:
            self.memory[key] = data

        return count

    def invalidate(
        self,
        table: str | None = None,
        symbol: str | None = None,
    ) -> int:
        """失效内存缓存和持久化文件

        Args:
            table: Table name to invalidate, or None for all.
            symbol: Optional symbol filter.

        Returns:
            Number of cache entries invalidated.
        """
        count = 0
        with self.memory_lock:
            if table:
                prefix = table
                if symbol:
                    prefix += f":{SymbolNormalizer.normalize(symbol)}"
                keys_to_remove = [k for k in self.memory if k.startswith(prefix)]
                for k in keys_to_remove:
                    del self.memory[k]
                    count += 1
            else:
                count = len(self.memory)
                self.memory.clear()

        if table:
            table_dir = Path(self.config.base_dir) / table
            if table_dir.exists():
                shutil.rmtree(table_dir)

        return count

    def exists(
        self,
        table: str,
        symbol: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> bool:
        """检查是否有数据

        Args:
            table: Table name.
            symbol: Optional symbol filter.
            start: Optional start date filter.
            end: Optional end date filter.

        Returns:
            True if matching data exists.
        """
        if symbol:
            symbol = SymbolNormalizer.normalize(symbol)
        return self.engine.exists(table, symbol, start, end)

    def has_data_range(
        self,
        table: str,
        symbol: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> bool:
        """检查数据是否覆盖指定日期范围

        Args:
            table: Table name.
            symbol: Optional symbol filter.
            start: Start date to check.
            end: End date to check.

        Returns:
            True if data covers the specified date range.
        """
        df = self.get(table, symbol, start, end, columns=["date"])
        if df.empty:
            return False

        min_date = pd.to_datetime(df["date"].min())
        max_date = pd.to_datetime(df["date"].max())

        if start and min_date > pd.to_datetime(start):
            return False
        if end and max_date < pd.to_datetime(end):
            return False

        return True

    def table_info(self, table: str) -> dict:
        """获取表信息

        Args:
            table: Table name.

        Returns:
            Dictionary with table statistics.
        """
        table_dir = Path(self.config.base_dir) / table
        if not table_dir.exists():
            return {"name": table, "file_count": 0, "size_mb": 0, "partition_count": 0}

        files = list(table_dir.rglob("*.parquet"))
        total_size = sum(f.stat().st_size for f in files)
        partitions = [d for d in table_dir.iterdir() if d.is_dir()]

        return {
            "name": table,
            "file_count": len(files),
            "size_mb": round(total_size / (1024 * 1024), 2),
            "partition_count": len(partitions),
        }

    def list_tables(self) -> list[str]:
        """列出所有有数据的表

        Returns:
            List of table names.
        """
        base = Path(self.config.base_dir)
        if not base.exists():
            return []
        return [d.name for d in base.iterdir() if d.is_dir()]

    def get_stats(self) -> dict:
        """获取缓存统计

        Returns:
            Dictionary with cache statistics.
        """
        tables = {}
        for table_name in self.list_tables():
            tables[table_name] = self.table_info(table_name)

        return {
            "memory_cache_size": len(self.memory),
            "tables": tables,
        }

    def _make_key(
        self,
        table: str,
        symbol: str | None,
        start: str | None,
        end: str | None,
    ) -> str:
        parts = [table]
        if symbol:
            parts.append(SymbolNormalizer.normalize(symbol))
        if start:
            parts.append(start)
        if end:
            parts.append(end)
        return ":".join(parts)


def get_cache_manager(config: CacheConfig | None = None) -> CacheManager:
    """Get or create the singleton CacheManager.

    Args:
        config: Optional cache configuration.

    Returns:
        CacheManager singleton instance.
    """
    return CacheManager.get_instance(config)


def reset_cache_manager() -> None:
    """Reset the singleton CacheManager instance."""
    CacheManager.reset_instance()
