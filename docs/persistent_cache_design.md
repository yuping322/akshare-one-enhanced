# akshare_one 持久化缓存层设计文档

> 将 jk2bt 的 DuckDB + SharedMemoryCache + Schema/TTL 能力迁移到 akshare_one，**一次重构，不留旧代码**。

---

## 1. 核心定位

### ParquetStore — 多读多写，减少冲突

- **分区文件天然支持并发写**：不同日期/不同 symbol 写入不同文件，互不阻塞
- **原子写入**：写临时文件再 rename，崩溃安全
- **轻量级**：无需数据库进程，直接操作文件系统
- **适合场景**：Provider 方法返回数据后的持久化写入

### DuckDB Engine — 高效查询 + 长期缓存

- **跨分区查询**：一条 SQL 扫描多个 parquet 分区，自动合并
- **长期存储**：历史数据（日线、财务、宏观）持久保存，进程重启不丢失
- **复杂查询**：支持 WHERE/ORDER BY/GROUP BY/JOIN，适合分析场景
- **适合场景**：多日期范围查询、跨 symbol 聚合、离线分析

### 两者关系

```
写入路径：Provider → ParquetStore (分区写入，无锁冲突)
                              │
                              ▼
查询路径：Provider → DuckDB Engine → read_parquet('多分区/*') → 合并返回
                              │
                              ▼
                         内存缓存 (热数据)
```

**Parquet 是存储格式，DuckDB 是查询引擎。两者不是竞争关系，而是互补。**

---

## 2. 目标架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Provider 层                               │
│  @cache("stock_daily")  /  @cache("financial_cache")         │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              统一缓存层 (akshare_one.cache)                   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  CacheManager                         │   │
│  │                                                      │   │
│  │  get(table, symbol, start, end)                      │   │
│  │  set(table, df, symbol, partition)                   │   │
│  │  invalidate(table, symbol)                           │   │
│  │  status(table)                                       │   │
│  └───────┬──────────────┬───────────────┬───────────────┘   │
│          │              │               │                   │
│   ┌──────▼──────┐ ┌────▼─────┐  ┌──────▼────────┐          │
│   │ MemoryCache │ │Parquet   │  │  DuckDB       │          │
│   │ (热数据)     │ │Store     │  │  Engine       │          │
│   │ TTLCache    │ │(分区写入) │  │  (跨分区查询)  │          │
│   └─────────────┘ └──────────┘  └───────────────┘          │
│          │              │               │                   │
│          ▼              ▼               ▼                   │
│     进程内存       .parquet 文件     DuckDB in-              │
│     (重启丢失)     (按分区组织)       process                │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│              基础设施层                                       │
│                                                             │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │ SchemaRegistry│ │CachePolicy   │ │ SymbolNormalizer     │  │
│  │ (表结构定义)  │ │ (TTL/分区策略)│ │ (6位/前缀/jq 互转)    │  │
│  └─────────────┘ └──────────────┘ └──────────────────────┘  │
│                                                             │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │AtomicWriter │ │CacheStatus   │ │ TTL Cleaner          │  │
│  │ (原子写入)   │ │ (状态检查)    │ │ (过期分区清理)        │  │
│  └─────────────┘ └──────────────┘ └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**核心原则：**
1. **一次重构** — 替换现有 TTLCache 体系，不留旧代码
2. **Parquet 存储 + DuckDB 查询** — 各司其职
3. **分区写入无冲突** — 不同日期/symbol 写入不同文件
4. **进程安全** — 支持多进程并发读写
5. **零新增依赖** — 只用 duckdb/pandas/cachetools（已有）

---

## 3. 模块设计

### 3.1 目录结构

```
src/akshare_one/
├── cache/                          # 新增：统一缓存层
│   ├── __init__.py                 # 导出统一 API
│   ├── config.py                   # 缓存配置（路径/TTL/分区策略）
│   ├── schema.py                   # 表结构定义 + SchemaRegistry
│   ├── manager.py                  # CacheManager 统一入口
│   ├── parquet_store.py            # Parquet 分区存储（写路径）
│   ├── duckdb_engine.py            # DuckDB 查询引擎（读路径）
│   ├── atomic_writer.py            # 原子写入（写临时文件再 rename）
│   ├── status.py                   # 缓存状态检查
│   ├── normalizer.py               # 符号标准化
│   └── cleaner.py                  # TTL 过期清理
│
├── modules/
│   ├── cache.py                    # 重写：装饰器接入持久化层
│   └── ...                         # 其他模块不变
```

### 3.2 `cache/config.py` — 配置中心

```python
@dataclass
class CacheConfig:
    """全局缓存配置"""

    # 路径
    cache_dir: str = "~/.akshare_one/cache"
    parquet_dir: str = "{cache_dir}/parquet"

    # 内存缓存（热数据）
    memory_max_items: int = 5000
    memory_default_ttl: int = 3600  # 1小时

    # DuckDB
    duckdb_threads: int = 4
    duckdb_memory_limit: str = "2GB"

    # Parquet
    compression: str = "snappy"
    row_group_size: int = 100_000

    # 分区策略
    partition_by_date: set[str] = field(default_factory=lambda: {
        "stock_daily", "etf_daily", "index_daily", "futures_daily",
    })
    partition_by_week: set[str] = field(default_factory=lambda: {
        "stock_minute", "etf_minute",
    })
    partition_by_symbol: set[str] = field(default_factory=lambda: {
        "balance_sheet", "income_statement", "cash_flow",
        "financial_metrics", "shareholder_top10",
    })
    no_partition: set[str] = field(default_factory=lambda: {
        "securities", "trade_days", "macro_data",
    })

    # TTL 策略（秒，0 = 永久）
    ttl_map: dict[str, int] = field(default_factory=lambda: {
        "stock_daily": 0,           # 历史数据永久
        "etf_daily": 0,
        "index_daily": 0,
        "financial_metrics": 86400,  # 24小时
        "securities": 604800,        # 7天
        "trade_days": 604800,
        "macro_data": 2592000,       # 30天
        "realtime": 60,              # 1分钟
        "minute_data": 3600,         # 1小时
    })

    @classmethod
    def from_env(cls) -> "CacheConfig":
        return cls(
            cache_dir=os.getenv("AKSHARE_ONE_CACHE_DIR", cls.cache_dir),
            memory_max_items=int(os.getenv("AKSHARE_ONE_CACHE_MAX_ITEMS", "5000")),
        )
```

### 3.3 `cache/schema.py` — 表结构注册

```python
@dataclass
class TableSchema:
    """表结构定义"""
    name: str
    columns: list[tuple[str, str]]      # [(列名, DuckDB类型), ...]
    primary_key: list[str]
    partition_key: str | None = None     # "date" | "week" | "symbol" | None
    ttl_seconds: int = 0
    description: str = ""


class SchemaRegistry:
    """全局表结构注册表"""
    _schemas: dict[str, TableSchema] = {}

    @classmethod
    def register(cls, schema: TableSchema) -> None: ...
    @classmethod
    def get(cls, table_name: str) -> TableSchema | None: ...
    @classmethod
    def list_tables(cls) -> list[str]: ...


# ── 预定义表结构 ──

SCHEMAS = [
    TableSchema(
        name="stock_daily",
        columns=[
            ("symbol", "VARCHAR(10)"),
            ("date", "DATE"),
            ("open", "DOUBLE"),
            ("high", "DOUBLE"),
            ("low", "DOUBLE"),
            ("close", "DOUBLE"),
            ("volume", "BIGINT"),
            ("amount", "DOUBLE"),
            ("turnover_rate", "DOUBLE"),
        ],
        primary_key=["symbol", "date"],
        partition_key="date",
        ttl_seconds=0,
    ),
    TableSchema(
        name="etf_daily",
        columns=[
            ("symbol", "VARCHAR(10)"),
            ("date", "DATE"),
            ("open", "DOUBLE"), ("high", "DOUBLE"),
            ("low", "DOUBLE"), ("close", "DOUBLE"),
            ("volume", "BIGINT"), ("amount", "DOUBLE"),
        ],
        primary_key=["symbol", "date"],
        partition_key="date",
    ),
    TableSchema(
        name="index_daily",
        columns=[
            ("symbol", "VARCHAR(10)"),
            ("date", "DATE"),
            ("open", "DOUBLE"), ("high", "DOUBLE"),
            ("low", "DOUBLE"), ("close", "DOUBLE"),
            ("volume", "BIGINT"), ("amount", "DOUBLE"),
        ],
        primary_key=["symbol", "date"],
        partition_key="date",
    ),
    TableSchema(
        name="financial_metrics",
        columns=[
            ("symbol", "VARCHAR(10)"),
            ("date", "DATE"),
            ("pe", "DOUBLE"), ("pe_ttm", "DOUBLE"),
            ("pb", "DOUBLE"), ("ps", "DOUBLE"),
            ("roe", "DOUBLE"), ("roa", "DOUBLE"),
            ("gross_profit_margin", "DOUBLE"),
            ("net_profit_margin", "DOUBLE"),
            ("revenue_yoy", "DOUBLE"),
            ("net_profit_yoy", "DOUBLE"),
        ],
        primary_key=["symbol", "date"],
        partition_key="symbol",
        ttl_seconds=86400,
    ),
    TableSchema(
        name="securities",
        columns=[
            ("symbol", "VARCHAR(10)"),
            ("name", "VARCHAR(50)"),
            ("type", "VARCHAR(20)"),
            ("start_date", "DATE"),
            ("end_date", "DATE"),
        ],
        primary_key=["symbol"],
        ttl_seconds=604800,
    ),
    TableSchema(
        name="trade_days",
        columns=[("date", "DATE")],
        primary_key=["date"],
        ttl_seconds=604800,
    ),
    TableSchema(
        name="northbound_flow",
        columns=[
            ("date", "DATE"),
            ("net_buy", "DOUBLE"),
            ("net_sell", "DOUBLE"),
            ("net_amount", "DOUBLE"),
        ],
        primary_key=["date"],
        ttl_seconds=86400,
    ),
    TableSchema(
        name="macro_data",
        columns=[
            ("indicator", "VARCHAR(30)"),
            ("date", "DATE"),
            ("value", "DOUBLE"),
        ],
        primary_key=["indicator", "date"],
        ttl_seconds=2592000,
    ),
]


def init_schemas() -> None:
    for schema in SCHEMAS:
        SchemaRegistry.register(schema)
```

### 3.4 `cache/parquet_store.py` — 分区存储（写路径）

```python
class ParquetStore:
    """按分区写入 Parquet 文件 — 多读多写无冲突"""

    def __init__(self, base_dir: str, config: CacheConfig):
        self.base_dir = Path(base_dir).expanduser()
        self.config = config

    def _partition_path(self, table: str, partition_value: str) -> Path:
        """生成分区路径

        stock_daily/2024-01-15/data.parquet
        stock_minute/2024-W03/data.parquet
        balance_sheet/600000/data.parquet
        securities/data.parquet  (无分区)
        """
        schema = SchemaRegistry.get(table)
        if schema and schema.partition_key:
            return self.base_dir / table / partition_value / "data.parquet"
        return self.base_dir / table / "data.parquet"

    def write(self, table: str, df: pd.DataFrame, partition_value: str | None = None) -> None:
        """原子写入：先写临时文件，再 rename

        不同 partition_value 写入不同文件，天然无锁冲突。
        同一 partition_value 的并发写入通过 AtomicWriter 保证安全。
        """
        schema = SchemaRegistry.get(table)
        if not schema:
            raise ValueError(f"Unknown table: {table}")

        # 列对齐
        expected_cols = [c[0] for c in schema.columns]
        df = df[[c for c in expected_cols if c in df.columns]].copy()
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        if partition_value:
            path = self._partition_path(table, partition_value)
        else:
            path = self._partition_path(table, "all")

        AtomicWriter.write_parquet(
            path, df, compression=self.config.compression
        )

    def write_batch(self, table: str, df: pd.DataFrame,
                    partition_col: str) -> int:
        """按某列值拆分 DataFrame，批量写入多个分区

        例：write_batch("stock_daily", df, "date")
        自动按 date 拆分，每个日期写入独立 parquet 文件
        """
        partitions = df.groupby(partition_col)
        operations = []
        for partition_value, group_df in partitions:
            path = self._partition_path(table, str(partition_value))
            operations.append((path, group_df))

        AtomicWriter.write_batch(operations)
        return len(operations)

    def has_data(self, table: str, partition_value: str | None = None) -> bool:
        path = self._partition_path(table, partition_value or "all")
        return path.exists()

    def get_date_range(self, table: str) -> tuple[str, str] | None:
        """获取表的日期范围（扫描分区目录名）"""
        table_dir = self.base_dir / table
        if not table_dir.exists():
            return None

        dates = []
        for d in table_dir.iterdir():
            if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name):
                dates.append(d.name)

        if not dates:
            return None
        return min(dates), max(dates)

    def list_partitions(self, table: str) -> list[str]:
        table_dir = self.base_dir / table
        if not table_dir.exists():
            return []
        return [d.name for d in table_dir.iterdir() if d.is_dir()]

    def delete_partition(self, table: str, partition_value: str) -> None:
        path = self._partition_path(table, partition_value)
        if path.exists():
            path.unlink()
```

### 3.5 `cache/duckdb_engine.py` — 查询引擎（读路径）

```python
class DuckDBEngine:
    """DuckDB 查询引擎 — 跨分区查询 + 长期缓存

    不存储数据，只读取 Parquet 文件。
    每次查询创建独立连接（:memory:），无并发冲突。
    """

    def __init__(self, config: CacheConfig):
        self.config = config

    def query(self, table: str,
              symbol: str | None = None,
              start: str | None = None,
              end: str | None = None,
              columns: list[str] | None = None,
              order_by: str | None = "date") -> pd.DataFrame:
        """查询表数据，自动处理多分区

        例：query("stock_daily", symbol="600000",
                   start="2024-01-01", end="2024-12-31")
        → SELECT * FROM read_parquet('stock_daily/*/data.parquet')
          WHERE symbol='600000' AND date BETWEEN ...
          ORDER BY date
        """
        schema = SchemaRegistry.get(table)
        if not schema:
            return pd.DataFrame()

        # 定位 parquet 文件
        table_dir = Path(self.config.parquet_dir).expanduser() / table
        if not table_dir.exists():
            return pd.DataFrame()

        # 构建 glob 模式
        if schema.partition_key:
            pattern = str(table_dir / "*" / "data.parquet")
        else:
            pattern = str(table_dir / "data.parquet")
            if not Path(pattern).exists():
                return pd.DataFrame()

        # 构建 SQL
        cols = ", ".join(columns) if columns else "*"
        sql = f"SELECT {cols} FROM read_parquet('{pattern}')"

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

        return self._execute(sql, params)

    def query_raw(self, sql: str, params: list | None = None) -> pd.DataFrame:
        """执行原始 SQL"""
        return self._execute(sql, params or [])

    def aggregate(self, table: str, agg_expr: str,
                  group_by: str | None = None,
                  where: str | None = None) -> pd.DataFrame:
        """聚合查询

        例：aggregate("stock_daily", "AVG(close) as avg_close",
                      group_by="symbol", where="date >= '2024-01-01'")
        """
        table_dir = Path(self.config.parquet_dir).expanduser() / table
        pattern = str(table_dir / "*" / "data.parquet")

        sql = f"SELECT {agg_expr} FROM read_parquet('{pattern}')"
        if where:
            sql += f" WHERE {where}"
        if group_by:
            sql += f" GROUP BY {group_by}"

        return self._execute(sql)

    def _execute(self, sql: str, params: list) -> pd.DataFrame:
        """执行 SQL（每次创建独立连接，无并发冲突）"""
        import duckdb

        conn = duckdb.connect(":memory:")
        conn.execute(f"SET threads={self.config.duckdb_threads}")
        conn.execute(f"SET memory_limit='{self.config.duckdb_memory_limit}'")
        try:
            return conn.execute(sql, params).fetchdf()
        finally:
            conn.close()
```

### 3.6 `cache/atomic_writer.py` — 原子写入

```python
class AtomicWriter:
    """崩溃安全的原子写入"""

    @staticmethod
    def write_parquet(path: Path, df: pd.DataFrame,
                      compression: str = "snappy") -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(".parquet.tmp")
        try:
            df.to_parquet(tmp_path, compression=compression, engine="pyarrow")
            tmp_path.rename(path)  # POSIX rename 是原子的
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def write_batch(operations: list[tuple[Path, pd.DataFrame]],
                    compression: str = "snappy") -> None:
        """批量原子写入：全部成功或全部回滚"""
        tmp_files = []
        try:
            for path, df in operations:
                path.parent.mkdir(parents=True, exist_ok=True)
                tmp = path.with_suffix(".parquet.tmp")
                df.to_parquet(tmp, compression=compression, engine="pyarrow")
                tmp_files.append((tmp, path))
            # 全部写入成功后 rename
            for tmp, path in tmp_files:
                tmp.rename(path)
        except Exception:
            for tmp, _ in tmp_files:
                tmp.unlink(missing_ok=True)
            raise
```

### 3.7 `cache/normalizer.py` — 符号标准化

```python
class SymbolNormalizer:
    """统一符号格式：输入任意格式 → 输出 6 位纯数字"""

    @staticmethod
    def normalize(symbol: str) -> str:
        s = symbol.upper().strip()
        if s.startswith(("SH", "SZ")):
            s = s[2:]
        if ".XSHG" in s or ".XSHE" in s:
            s = s.split(".")[0]
        return s.zfill(6)

    @staticmethod
    def to_jq(symbol: str) -> str:
        s = SymbolNormalizer.normalize(symbol)
        exchange = "XSHG" if s.startswith(("6", "9")) else "XSHE"
        return f"{s}.{exchange}"
```

### 3.8 `cache/status.py` — 缓存状态

```python
@dataclass
class CacheStatus:
    table: str
    has_data: bool
    partition_count: int
    date_range: tuple[str, str] | None
    size_mb: float


class CacheStatusChecker:
    def __init__(self, store: ParquetStore, engine: DuckDBEngine):
        self.store = store
        self.engine = engine

    def check_table(self, table: str, symbol: str | None = None) -> CacheStatus:
        date_range = self.store.get_date_range(table)
        partitions = self.store.list_partitions(table)

        size_mb = 0.0
        table_dir = Path(self.store.base_dir) / table
        if table_dir.exists():
            size_mb = sum(f.stat().st_size for f in table_dir.rglob("*.parquet")) / 1024 / 1024

        return CacheStatus(
            table=table,
            has_data=bool(partitions),
            partition_count=len(partitions),
            date_range=date_range,
            size_mb=round(size_mb, 2),
        )

    def check_coverage(self, table: str, symbol: str,
                       start: str, end: str) -> dict:
        """检查缓存覆盖度"""
        df = self.engine.query(table, symbol=symbol, start=start, end=end)
        if df.empty:
            return {"has_data": False, "coverage_pct": 0.0}

        cached_dates = set(df["date"].astype(str))
        trading_days = self._get_trading_days(start, end)
        missing = trading_days - cached_dates

        return {
            "has_data": True,
            "is_complete": len(missing) == 0,
            "cached_count": len(cached_dates),
            "total_count": len(trading_days),
            "missing_days": sorted(missing)[:10],  # 最多显示10天
            "coverage_pct": round(len(cached_dates) / len(trading_days), 4),
        }

    def validate_for_offline(self, symbols: list[str],
                             start: str, end: str) -> tuple[bool, dict]:
        """验证离线模式是否可用"""
        missing = []
        incomplete = []

        for symbol in symbols:
            coverage = self.check_coverage("stock_daily", symbol, start, end)
            if not coverage["has_data"]:
                missing.append(symbol)
            elif not coverage["is_complete"]:
                incomplete.append((symbol, coverage["coverage_pct"]))

        is_valid = not missing and not incomplete
        return is_valid, {
            "missing": missing,
            "incomplete": incomplete,
        }
```

### 3.9 `cache/cleaner.py` — TTL 过期清理

```python
class TTLCleaner:
    """清理过期分区"""

    def __init__(self, store: ParquetStore):
        self.store = store

    def clean_table(self, table: str, now: datetime | None = None) -> int:
        """清理表的过期分区"""
        schema = SchemaRegistry.get(table)
        if not schema or schema.ttl_seconds == 0:
            return 0

        now = now or datetime.now()
        cutoff = now - timedelta(seconds=schema.ttl_seconds)
        cutoff_str = cutoff.strftime("%Y-%m-%d")

        cleaned = 0
        for partition in self.store.list_partitions(table):
            if partition < cutoff_str:
                self.store.delete_partition(table, partition)
                cleaned += 1

        return cleaned

    def clean_all(self) -> dict[str, int]:
        """清理所有表的过期分区"""
        results = {}
        for table in SchemaRegistry.list_tables():
            cleaned = self.clean_table(table)
            if cleaned > 0:
                results[table] = cleaned
        return results
```

### 3.10 `cache/manager.py` — 统一入口

```python
class CacheManager:
    """统一缓存管理器 — 组合 Memory + Parquet + DuckDB"""

    _instance: "CacheManager | None" = None
    _lock = threading.Lock()

    def __init__(self, config: CacheConfig | None = None):
        self.config = config or CacheConfig.from_env()
        init_schemas()

        # 内存缓存（热数据）
        self.memory = TTLCache(
            maxsize=self.config.memory_max_items,
            ttl=self.config.memory_default_ttl,
        )
        self.memory_lock = threading.Lock()

        # 持久化层
        self.store = ParquetStore(self.config.parquet_dir, self.config)
        self.engine = DuckDBEngine(self.config)
        self.status = CacheStatusChecker(self.store, self.engine)
        self.cleaner = TTLCleaner(self.store)

    @classmethod
    def get_instance(cls, config: CacheConfig | None = None) -> "CacheManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
        return cls._instance

    # ── 核心 API ──

    def get(self, table: str, symbol: str | None = None,
            start: str | None = None, end: str | None = None,
            columns: list[str] | None = None) -> pd.DataFrame:
        """查询：Memory → DuckDB(Parquet) → 空"""

        # 1. 查内存
        key = self._make_key(table, symbol, start, end)
        with self.memory_lock:
            try:
                result = self.memory[key]
                return result.copy()
            except KeyError:
                pass

        # 2. 查持久化（DuckDB 跨分区查询）
        df = self.engine.query(table, symbol, start, end, columns)

        # 3. 写回内存
        if not df.empty:
            with self.memory_lock:
                self.memory[key] = df

        return df

    def set(self, table: str, df: pd.DataFrame,
            symbol: str | None = None,
            partition_value: str | None = None) -> None:
        """写入：Parquet + 内存"""
        if df.empty:
            return

        # 1. 写 Parquet（分区写入，无冲突）
        self.store.write(table, df, partition_value)

        # 2. 写内存
        key = self._make_key(table, symbol)
        with self.memory_lock:
            self.memory[key] = df

    def set_batch(self, table: str, df: pd.DataFrame,
                  partition_col: str) -> int:
        """批量写入：按某列拆分到多个分区"""
        if df.empty:
            return 0

        count = self.store.write_batch(table, df, partition_col)

        # 写内存（整个 DataFrame）
        key = f"{table}:batch:{partition_col}"
        with self.memory_lock:
            self.memory[key] = df

        return count

    def invalidate(self, table: str | None = None,
                   symbol: str | None = None) -> None:
        """失效内存缓存"""
        with self.memory_lock:
            if table:
                prefix = table
                if symbol:
                    prefix += f":{SymbolNormalizer.normalize(symbol)}"
                keys_to_remove = [k for k in self.memory if k.startswith(prefix)]
                for k in keys_to_remove:
                    del self.memory[k]
            else:
                self.memory.clear()

    def clean_expired(self) -> dict[str, int]:
        """清理过期分区"""
        return self.cleaner.clean_all()

    def _make_key(self, table: str, symbol: str | None = None,
                  start: str | None = None, end: str | None = None) -> str:
        parts = [table]
        if symbol:
            parts.append(SymbolNormalizer.normalize(symbol))
        if start:
            parts.append(start)
        if end:
            parts.append(end)
        return ":".join(parts)


def get_cache() -> CacheManager:
    return CacheManager.get_instance()
```

---

## 4. 装饰器重写

### 4.1 `modules/cache.py` — 全新实现

**删除现有 TTLCache 装饰器，重写为：**

```python
"""缓存装饰器 — 内存 + Parquet + DuckDB"""

import os
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import pandas as pd

from ..cache import get_cache, SymbolNormalizer
from ..metrics import get_stats_collector

F = TypeVar("F", bound=Callable[..., Any])

# cache_key → table_name 映射
_TABLE_MAP = {
    "realtime_cache": "realtime",
    "futures_realtime_cache": "futures_realtime",
    "options_realtime_cache": "options_realtime",
    "hist_data_cache": "stock_daily",
    "hist_daily_cache": "stock_daily",
    "news_cache": "news",
    "futures_hist_cache": "futures_daily",
    "options_chain_cache": "options_chain",
    "financial_cache": "financial_metrics",
    "info_cache": "securities",
    "insider_cache": "insider_trade",
    "macro_cache": "macro_data",
    "blockdeal_cache": "block_deal",
    "shareholder_cache": "shareholder_top10",
    "dividend_data_cache": "dividend",
    "adjust_factor_cache": "adjust_factor",
    "northbound_cache": "northbound_flow",
    "margin_cache": "margin_data",
    "index_cache": "index_daily",
    "lhbg_cache": "dragon_tiger",
    "pledge_cache": "equity_pledge",
    "restricted_cache": "restricted_release",
    "stock_list_cache": "securities",
    "trade_dates_cache": "trade_days",
}


def cache(cache_key: str, key: Callable | None = None) -> Callable[[F], F]:
    """缓存装饰器

    查询路径: Memory → DuckDB(Parquet) → 调用原函数 → 写回 Parquet + Memory
    """
    table_name = _TABLE_MAP.get(cache_key, cache_key.replace("_cache", ""))

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_enabled = os.getenv("AKSHARE_ONE_CACHE_ENABLED", "true").lower() in (
                "1", "true", "yes", "on"
            )
            if not cache_enabled:
                return func(*args, **kwargs)

            stats = get_stats_collector()
            mgr = get_cache()

            # 提取 symbol 和日期
            symbol = _extract_symbol(args, kwargs)
            start = _extract_start_date(args, kwargs)
            end = _extract_end_date(args, kwargs)

            if symbol:
                symbol = SymbolNormalizer.normalize(symbol)

            # ── 1. 查内存 ──
            mem_key = _make_mem_key(table_name, symbol, start, end)
            with mgr.memory_lock:
                try:
                    result = mgr.memory[mem_key]
                    stats.record_cache_hit(f"{cache_key}_memory")
                    return result.copy()
                except KeyError:
                    stats.record_cache_miss(cache_key)

            # ── 2. 查持久化 ──
            df = mgr.engine.query(table_name, symbol, start, end)
            if not df.empty:
                with mgr.memory_lock:
                    mgr.memory[mem_key] = df
                stats.record_cache_hit(f"{cache_key}_persistence")
                return df.copy()

            # ── 3. 调用原函数 ──
            result = func(*args, **kwargs)

            # ── 4. 写回持久化 ──
            if isinstance(result, pd.DataFrame) and not result.empty:
                partition = _extract_partition_value(result, table_name, symbol)
                mgr.store.write(table_name, result, partition)
                with mgr.memory_lock:
                    mgr.memory[mem_key] = result

            return result.copy() if isinstance(result, pd.DataFrame) else result

        return wrapper  # type: ignore

    return decorator


def smart_cache(realtime_key: str, daily_key: str,
                interval_attr: str = "interval") -> Callable[[F], F]:
    """智能缓存：根据 interval 选择不同 TTL"""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 判断 interval
            use_daily = True
            if args and hasattr(args[0], interval_attr):
                interval = getattr(args[0], interval_attr, "day").lower()
                if interval in ("minute", "hour"):
                    use_daily = False

            cache_key = daily_key if use_daily else realtime_key
            return cache(cache_key)(func)(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def clear_cache(cache_key: str | None = None) -> None:
    """清除缓存"""
    mgr = get_cache()
    if cache_key:
        table = _TABLE_MAP.get(cache_key, cache_key.replace("_cache", ""))
        mgr.invalidate(table)
    else:
        mgr.invalidate()


# ── 辅助函数 ──

def _extract_symbol(args, kwargs) -> str | None:
    for k in ("symbol", "code", "underlying_symbol"):
        if k in kwargs:
            return str(kwargs[k])
    return None

def _extract_start_date(args, kwargs) -> str | None:
    for k in ("start_date", "start"):
        if k in kwargs:
            return str(kwargs[k])
    return None

def _extract_end_date(args, kwargs) -> str | None:
    for k in ("end_date", "end"):
        if k in kwargs:
            return str(kwargs[k])
    return None

def _extract_partition_value(df: pd.DataFrame, table: str,
                             symbol: str | None) -> str | None:
    """从 DataFrame 提取分区值"""
    from ..cache.schema import SchemaRegistry

    schema = SchemaRegistry.get(table)
    if not schema or not schema.partition_key:
        return None

    col = schema.partition_key
    if col == "date" and "date" in df.columns:
        # 取第一个日期作为分区值
        return str(df["date"].iloc[0])
    if col == "week" and "date" in df.columns:
        # 按周分区
        date = pd.to_datetime(df["date"].iloc[0])
        return date.strftime("%Y-W%W")
    if col == "symbol" and symbol:
        return symbol

    return None

def _make_mem_key(table: str, symbol: str | None,
                  start: str | None, end: str | None) -> str:
    parts = [table]
    if symbol:
        parts.append(symbol)
    if start:
        parts.append(start)
    if end:
        parts.append(end)
    return ":".join(parts)
```

---

## 5. 分区文件布局

```
~/.akshare_one/cache/parquet/
├── stock_daily/
│   ├── 2024-01-15/
│   │   └── data.parquet          # 单股或多股单日
│   ├── 2024-01-16/
│   │   └── data.parquet
│   └── ...
├── etf_daily/
│   ├── 2024-01-15/
│   │   └── data.parquet
│   └── ...
├── index_daily/
│   └── ...
├── stock_minute/
│   ├── 2024-W03/                  # 按周分区
│   │   └── data.parquet
│   └── 2024-W04/
│       └── data.parquet
├── financial_metrics/
│   ├── 600000/
│   │   └── data.parquet           # 按 symbol 分区
│   └── 000001/
│       └── data.parquet
├── trade_days/
│   └── data.parquet               # 无分区，单文件
├── securities/
│   └── data.parquet
├── macro_data/
│   └── data.parquet
└── northbound_flow/
    └── data.parquet
```

**DuckDB 跨分区查询示例：**

```sql
-- 自动扫描所有日期分区，合并返回
SELECT * FROM read_parquet('stock_daily/*/data.parquet')
WHERE symbol = '600000' AND date >= '2024-01-01' AND date <= '2024-12-31'
ORDER BY date;
```

---

## 6. 与现有代码的集成

| 现有模块 | 改动 |
|---------|------|
| `modules/cache.py` | **完全重写**，删除 TTLCache 装饰器，接入 CacheManager |
| `modules/historical/cached_provider.py` | 删除（被统一缓存层替代） |
| `modules/historical/duckdb_storage.py` | 删除（被 DuckDBEngine 替代） |
| `modules/cache.py` 的 CACHE_CONFIG 字典 | 删除（TTL 移至 CacheConfig） |
| 所有 Provider | **零改动**（装饰器 API 不变） |
| `metrics/stats.py` | 新增 `record_cache_hit("xxx_persistence")` 统计 |

---

## 7. 使用方式

### 环境变量

```bash
export AKSHARE_ONE_CACHE_DIR=~/.akshare_one/cache
export AKSHARE_ONE_CACHE_MAX_ITEMS=10000
```

### Python API

```python
from akshare_one.cache import CacheManager, CacheConfig

# 获取实例
cache = CacheManager.get_instance()

# 查询
df = cache.get("stock_daily", symbol="600000", start="2024-01-01", end="2024-12-31")

# 写入
cache.set("stock_daily", df, symbol="600000", partition_value="2024-01-15")

# 批量写入（按日期拆分到多个分区）
cache.set_batch("stock_daily", large_df, partition_col="date")

# 状态检查
status = cache.status.check_table("stock_daily")
coverage = cache.status.check_coverage("stock_daily", "600000", "2024-01-01", "2024-12-31")

# 离线验证
valid, report = cache.status.validate_for_offline(
    symbols=["600000", "000001"],
    start="2024-01-01", end="2024-12-31",
)

# 清理过期
cleaned = cache.clean_expired()

# 清除缓存
from akshare_one.cache import clear_cache
clear_cache()  # 清除所有
clear_cache("hist_data_cache")  # 清除指定
```

---

## 8. 实施计划

| 阶段 | 任务 | Agent |
|------|------|-------|
| **P0** | `cache/config.py` + `cache/schema.py` + `cache/normalizer.py` | 1 |
| **P1** | `cache/parquet_store.py` + `cache/atomic_writer.py` | 2 |
| **P2** | `cache/duckdb_engine.py` + `cache/manager.py` | 3 |
| **P3** | `cache/status.py` + `cache/cleaner.py` | 4 |
| **P4** | 重写 `modules/cache.py` 装饰器 | 5 |
| **P5** | 删除旧代码 + 集成测试 | 6 |
