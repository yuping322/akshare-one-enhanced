"""Atomic writer for parquet files - write to temp then rename for crash safety."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


class AtomicWriter:
    """Crash-safe atomic write: write to temp file then rename."""

    @staticmethod
    def write_parquet(
        path: Path,
        df: pd.DataFrame,
        compression: str = "snappy",
        row_group_size: int = 100_000,
    ) -> Path:
        """Atomically write a single parquet file.

        Args:
            path: Target file path.
            df: DataFrame to write.
            compression: Parquet compression codec.
            row_group_size: Number of rows per row group.

        Returns:
            The target path after successful write.

        Raises:
            Exception: Original exception if write fails (temp file cleaned up).
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            table = pa.Table.from_pandas(df)
            pq.write_table(
                table,
                str(tmp_path),
                compression=compression,
                row_group_size=row_group_size,
            )
            os.replace(str(tmp_path), str(path))
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            raise
        return path

    @staticmethod
    def write_batch(
        operations: list[tuple[Path, pd.DataFrame]],
        compression: str = "snappy",
        row_group_size: int = 100_000,
    ) -> None:
        """Batch atomic write: all succeed or all rollback.

        Args:
            operations: List of (target_path, DataFrame) pairs.
            compression: Parquet compression codec.
            row_group_size: Number of rows per row group.

        Raises:
            Exception: Original exception if any write fails (all temp files cleaned up).
        """
        tmp_files: list[tuple[Path, Path]] = []
        try:
            for path, df in operations:
                path.parent.mkdir(parents=True, exist_ok=True)
                tmp = path.with_suffix(path.suffix + ".tmp")
                table = pa.Table.from_pandas(df)
                pq.write_table(
                    table,
                    str(tmp),
                    compression=compression,
                    row_group_size=row_group_size,
                )
                tmp_files.append((tmp, path))
            for tmp, path in tmp_files:
                os.replace(str(tmp), str(path))
        except Exception:
            for tmp, _ in tmp_files:
                tmp.unlink(missing_ok=True)
            raise
