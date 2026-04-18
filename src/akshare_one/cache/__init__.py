"""akshare_one cache package - unified cache layer with memory + parquet + DuckDB.

Usage:
    from akshare_one.cache import get_cache_manager
    cache = get_cache_manager()
    df = cache.get("stock_daily", symbol="600000", start="2024-01-01", end="2024-12-31")
"""

from .config import CacheConfig
from .schema import (
    SCHEMA_REGISTRY,
    TableSchema,
    init_schemas,
    list_tables,
    get_table_schema,
)
from .normalizer import SymbolNormalizer
from .parquet_store import ParquetStore
from .duckdb_engine import DuckDBEngine
from .manager import CacheManager, get_cache_manager, reset_cache_manager
from .status import CacheStatus, CacheStatusChecker
from .cleaner import TTLCleaner

__all__ = [
    "CacheConfig",
    "SCHEMA_REGISTRY",
    "TableSchema",
    "init_schemas",
    "list_tables",
    "get_table_schema",
    "SymbolNormalizer",
    "ParquetStore",
    "DuckDBEngine",
    "CacheManager",
    "get_cache_manager",
    "reset_cache_manager",
    "CacheStatus",
    "CacheStatusChecker",
    "TTLCleaner",
]
