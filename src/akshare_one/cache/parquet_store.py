"""Parquet partitioned storage - write path for cache data.

Different partitions write to different files, avoiding write conflicts.
Uses AtomicWriter for crash-safe writes.
"""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path

import pandas as pd

from .atomic_writer import AtomicWriter
from .config import CacheConfig
from .schema import SCHEMA_REGISTRY

logger = logging.getLogger(__name__)


class ParquetStore:
    """Write partitioned Parquet files — concurrent reads/writes without lock conflicts."""

    def __init__(self, base_dir: str | Path, config: CacheConfig | None = None):
        self.base_dir = Path(base_dir).expanduser()
        self.config = config or CacheConfig()

    def _partition_path(self, table: str, partition_value: str | None = None) -> Path:
        """Generate partition directory path.

        Examples:
            stock_daily/date=2024-01-15/part_xxx.parquet
            stock_minute/week=2024-W03/part_xxx.parquet
            financial_metrics/symbol=600000/part_xxx.parquet
            trade_calendar/trade_calendar.parquet  (no partition)

        Args:
            table: Table name.
            partition_value: Partition value (e.g. "2024-01-15").

        Returns:
            Path to the partition directory.
        """
        schema = SCHEMA_REGISTRY.get(table)
        if schema and schema.partition_by and partition_value:
            return self.base_dir / table / f"{schema.partition_by}={partition_value}"
        return self.base_dir / table

    def write(
        self,
        table: str,
        df: pd.DataFrame,
        partition_value: str | None = None,
    ) -> Path:
        """Write DataFrame to a partition.

        Different partition_value writes go to different directories,
        avoiding lock conflicts naturally.

        Args:
            table: Table name.
            df: DataFrame to write.
            partition_value: Partition value (e.g. date string).

        Returns:
            Path to the written parquet file, or empty Path if df is empty.

        Raises:
            ValueError: If table is not registered in SCHEMA_REGISTRY.
        """
        schema = SCHEMA_REGISTRY.get(table)
        if not schema:
            raise ValueError(f"Unknown table: {table}")

        if df.empty:
            logger.debug("Empty DataFrame for table=%s, skipping write", table)
            return Path()

        expected_cols = list(schema.schema.keys())
        df = df[[c for c in expected_cols if c in df.columns]].copy()
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        partition_path = self._partition_path(table, partition_value)
        partition_path.mkdir(parents=True, exist_ok=True)

        filename = f"part_{table}.parquet"
        target_path = partition_path / filename

        return AtomicWriter.write_parquet(
            target_path,
            df,
            compression=self.config.compression,
            row_group_size=self.config.row_group_size,
        )

    def write_batch(
        self,
        table: str,
        df: pd.DataFrame,
        partition_col: str,
    ) -> int:
        """Split DataFrame by a column and write to multiple partitions atomically.

        Example: write_batch("stock_daily", df, "date")
        Automatically splits by date, each date writes to its own directory.

        Args:
            table: Table name.
            df: DataFrame to write.
            partition_col: Column name to split by.

        Returns:
            Number of partitions written.

        Raises:
            ValueError: If table is not registered in SCHEMA_REGISTRY.
        """
        schema = SCHEMA_REGISTRY.get(table)
        if not schema:
            raise ValueError(f"Unknown table: {table}")

        if df.empty:
            return 0

        expected_cols = list(schema.schema.keys())
        df = df[[c for c in expected_cols if c in df.columns]].copy()
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        operations = []
        for partition_value, group_df in df.groupby(partition_col):
            pv_str = str(partition_value)
            if hasattr(partition_value, "strftime"):
                pv_str = partition_value.strftime("%Y-%m-%d")

            partition_path = self._partition_path(table, pv_str)
            filename = f"part_{table}.parquet"
            target_path = partition_path / filename
            operations.append((target_path, group_df))

        AtomicWriter.write_batch(
            operations,
            compression=self.config.compression,
            row_group_size=self.config.row_group_size,
        )
        return len(operations)

    def has_data(self, table: str, partition_value: str | None = None) -> bool:
        """Check if a partition has data.

        Args:
            table: Table name.
            partition_value: Partition value to check.

        Returns:
            True if parquet files exist in the partition.
        """
        path = self._partition_path(table, partition_value)
        if not path.exists():
            return False
        return any(path.glob("*.parquet"))

    def get_date_range(self, table: str) -> tuple[str, str] | None:
        """Get date range for a table by scanning partition directory names.

        Args:
            table: Table name.

        Returns:
            Tuple of (min_date, max_date) strings, or None if no date partitions found.
        """
        table_dir = self.base_dir / table
        if not table_dir.exists():
            return None

        dates = []
        for d in table_dir.iterdir():
            if d.is_dir():
                match = re.search(r"(\d{4}-\d{2}-\d{2})", d.name)
                if match:
                    dates.append(match.group(1))

        if not dates:
            return None
        return min(dates), max(dates)

    def list_partitions(self, table: str) -> list[str]:
        """List all partition names for a table.

        Args:
            table: Table name.

        Returns:
            List of partition directory names.
        """
        table_dir = self.base_dir / table
        if not table_dir.exists():
            return []
        return [d.name for d in table_dir.iterdir() if d.is_dir()]

    def delete_partition(self, table: str, partition_value: str) -> None:
        """Delete a partition directory.

        Args:
            table: Table name.
            partition_value: Partition value to delete.
        """
        path = self._partition_path(table, partition_value)
        if path.exists():
            shutil.rmtree(path)
