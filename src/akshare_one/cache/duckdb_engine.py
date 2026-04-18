"""DuckDB query engine - read path for parquet cache data.

Uses DuckDB to query parquet files with SQL.
Each query creates a new in-memory connection (no concurrency conflicts).
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb
import pandas as pd

from .config import CacheConfig
from .schema import SCHEMA_REGISTRY

logger = logging.getLogger(__name__)


class DuckDBEngine:
    """DuckDB 查询引擎 — 跨分区查询 + 长期缓存

    不存储数据，只读取 Parquet 文件。
    每次查询创建独立连接（:memory:），无并发冲突。
    """

    def __init__(self, base_dir: str | Path, config: CacheConfig | None = None):
        self.base_dir = Path(base_dir).expanduser()
        self.config = config or CacheConfig()

    def query(
        self,
        table: str,
        symbol: str | None = None,
        start: str | None = None,
        end: str | None = None,
        columns: list[str] | None = None,
        order_by: str | None = "date",
        limit: int | None = None,
    ) -> pd.DataFrame:
        """查询表数据，自动处理多分区

        例：query("stock_daily", symbol="600000",
                   start="2024-01-01", end="2024-12-31")
        → SELECT * FROM read_parquet('stock_daily/**/*.parquet')
          WHERE symbol='600000' AND date BETWEEN ...
          ORDER BY date

        Args:
            table: Table name.
            symbol: Stock symbol filter.
            start: Start date filter (inclusive).
            end: End date filter (inclusive).
            columns: Column list to select, or None for all.
            order_by: Order by column, or None.
            limit: Max rows to return, or None.

        Returns:
            DataFrame with query results, or empty DataFrame if no data.
        """
        table_dir = self.base_dir / table
        if not table_dir.exists():
            return pd.DataFrame()

        parquet_files = list(table_dir.rglob("*.parquet"))
        parquet_files = [f for f in parquet_files if not f.name.endswith(".tmp")]

        if not parquet_files:
            return pd.DataFrame()

        cols = ", ".join(columns) if columns else "*"
        files_str = ", ".join(f"'{f}'" for f in parquet_files)
        sql = f"SELECT {cols} FROM read_parquet([{files_str}])"

        conditions = []
        params = []
        if symbol:
            conditions.append("symbol = ?")
            params.append(symbol)
        if start:
            conditions.append("date >= ?")
            params.append(start)
        if end:
            conditions.append("date <= ?")
            params.append(end)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit:
            sql += f" LIMIT {limit}"

        return self._execute(sql, params)

    def query_raw(self, sql: str, params: list | None = None) -> pd.DataFrame:
        """执行原始 SQL

        Args:
            sql: Raw SQL query string.
            params: Optional query parameters.

        Returns:
            DataFrame with query results, or empty DataFrame on error.
        """
        return self._execute(sql, params or [])

    def aggregate(
        self,
        table: str,
        agg_expr: str,
        group_by: str | None = None,
        where: str | None = None,
    ) -> pd.DataFrame:
        """聚合查询

        例：aggregate("stock_daily", "AVG(close) as avg_close",
                      group_by="symbol", where="date >= '2024-01-01'")

        Args:
            table: Table name.
            agg_expr: Aggregation expression (e.g. "AVG(close) as avg_close").
            group_by: Optional GROUP BY clause.
            where: Optional WHERE clause.

        Returns:
            DataFrame with aggregation results, or empty DataFrame if no data.
        """
        table_dir = self.base_dir / table
        parquet_files = list(table_dir.rglob("*.parquet"))
        parquet_files = [f for f in parquet_files if not f.name.endswith(".tmp")]

        if not parquet_files:
            return pd.DataFrame()

        files_str = ", ".join(f"'{f}'" for f in parquet_files)
        sql = f"SELECT {agg_expr} FROM read_parquet([{files_str}])"
        if where:
            sql += f" WHERE {where}"
        if group_by:
            sql += f" GROUP BY {group_by}"

        return self._execute(sql)

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
            True if any matching data exists.
        """
        df = self.query(table, symbol, start, end, columns=["1"], limit=1)
        return not df.empty

    def count(
        self,
        table: str,
        symbol: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> int:
        """统计记录数

        Args:
            table: Table name.
            symbol: Optional symbol filter.
            start: Optional start date filter.
            end: Optional end date filter.

        Returns:
            Number of matching records, or 0 if no data.
        """
        table_dir = self.base_dir / table
        if not table_dir.exists():
            return 0

        parquet_files = list(table_dir.rglob("*.parquet"))
        parquet_files = [f for f in parquet_files if not f.name.endswith(".tmp")]

        if not parquet_files:
            return 0

        files_str = ", ".join(f"'{f}'" for f in parquet_files)
        sql = f"SELECT COUNT(*) FROM read_parquet([{files_str}])"

        conditions = []
        params = []
        if symbol:
            conditions.append("symbol = ?")
            params.append(symbol)
        if start:
            conditions.append("date >= ?")
            params.append(start)
        if end:
            conditions.append("date <= ?")
            params.append(end)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        result = self._execute(sql, params)
        if result.empty:
            return 0
        return int(result.iloc[0, 0])

    def _execute(self, sql: str, params: list) -> pd.DataFrame:
        """执行 SQL（每次创建独立连接，无并发冲突）

        Args:
            sql: SQL query string.
            params: Query parameters.

        Returns:
            DataFrame with query results, or empty DataFrame on error.
        """
        conn = duckdb.connect(":memory:")
        try:
            conn.execute(f"SET threads={self.config.duckdb_threads}")
            conn.execute(f"SET memory_limit='{self.config.duckdb_memory_limit}'")
            return conn.execute(sql, params).fetchdf()
        except Exception as e:
            logger.error("Query failed: %s\nSQL: %s", e, sql)
            return pd.DataFrame()
        finally:
            conn.close()
