"""Table schema registry for akshare_one cache.

Defines all cache table schemas including column types, primary keys,
partitioning strategy, TTL, priority, and storage layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TableSchema:
    """Immutable schema definition for a cache table.

    Attributes:
        name: Unique table identifier.
        partition_by: Column name for parquet partitioning, or None.
        ttl_hours: Time-to-live in hours. 0 means no expiration.
        schema: Mapping of column names to parquet data types.
        primary_key: Columns that uniquely identify a row.
        aggregation_enabled: Whether aggregated storage is enabled.
        compaction_threshold: File count before triggering compaction.
        priority: Priority tier (P0-P3).
        storage_layer: Logical storage layer (daily, meta, snapshot, minute).
    """

    name: str
    partition_by: str | None
    ttl_hours: int
    schema: dict[str, str]
    primary_key: list[str]
    aggregation_enabled: bool = True
    compaction_threshold: int = 20
    priority: str = "P0"
    storage_layer: str = "daily"


@dataclass
class TableInfo:
    """Runtime metadata about a cache table's physical state.

    Attributes:
        name: Table name.
        file_count: Number of parquet files on disk.
        total_size_bytes: Total size of all parquet files.
        last_updated: Timestamp of the most recent write.
        partition_count: Number of distinct partition values.
        priority: Priority tier.
    """

    name: str
    file_count: int
    total_size_bytes: int
    last_updated: str | None
    partition_count: int
    priority: str


class TableRegistry:
    """Registry for table schemas.

    Provides lookup, listing, and filtering operations over registered
    TableSchema instances.
    """

    def __init__(self) -> None:
        self._tables: dict[str, TableSchema] = {}

    def register(self, table: TableSchema) -> None:
        """Register a table schema.

        Args:
            table: TableSchema instance to register.
        """
        self._tables[table.name] = table

    def get(self, name: str) -> TableSchema:
        """Get a table schema by name.

        Args:
            name: Table name.

        Returns:
            TableSchema for the given name.

        Raises:
            KeyError: If the table is not registered.
        """
        return self._tables[name]

    def get_or_none(self, name: str) -> TableSchema | None:
        """Get a table schema by name, or None if not found.

        Args:
            name: Table name.

        Returns:
            TableSchema or None.
        """
        return self._tables.get(name)

    def list_all(self) -> dict[str, TableSchema]:
        """Return a copy of all registered schemas.

        Returns:
            Dictionary mapping table names to TableSchema.
        """
        return dict(self._tables)

    def list_by_priority(self, priority: str) -> list[TableSchema]:
        """List tables filtered by priority tier.

        Args:
            priority: Priority string (e.g. "P0").

        Returns:
            List of TableSchema matching the priority.
        """
        return [t for t in self._tables.values() if t.priority == priority]

    def list_by_layer(self, layer: str) -> list[TableSchema]:
        """List tables filtered by storage layer.

        Args:
            layer: Storage layer name (e.g. "daily", "meta").

        Returns:
            List of TableSchema matching the layer.
        """
        return [t for t in self._tables.values() if t.storage_layer == layer]

    def has(self, name: str) -> bool:
        """Check if a table is registered.

        Args:
            name: Table name.

        Returns:
            True if the table exists in the registry.
        """
        return name in self._tables


# ── Daily market data ──────────────────────────────────────────────────

STOCK_DAILY = TableSchema(
    name="stock_daily",
    partition_by="date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "date": "date",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "amount": "float64",
        "adjust": "string",
    },
    primary_key=["symbol", "date", "adjust"],
    storage_layer="daily",
)

ETF_DAILY = TableSchema(
    name="etf_daily",
    partition_by="date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "date": "date",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "amount": "float64",
    },
    primary_key=["symbol", "date"],
    storage_layer="daily",
)

INDEX_DAILY = TableSchema(
    name="index_daily",
    partition_by="date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "date": "date",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "amount": "float64",
    },
    primary_key=["symbol", "date"],
    storage_layer="daily",
)

FUTURES_DAILY = TableSchema(
    name="futures_daily",
    partition_by="date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "date": "date",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "open_interest": "float64",
    },
    primary_key=["symbol", "date"],
    storage_layer="daily",
)

CONVERSION_BOND_DAILY = TableSchema(
    name="conversion_bond_daily",
    partition_by="date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "date": "date",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "amount": "float64",
    },
    primary_key=["symbol", "date"],
    storage_layer="daily",
)

# ── Index / sector data ────────────────────────────────────────────────

INDEX_COMPONENTS = TableSchema(
    name="index_components",
    partition_by="date",
    ttl_hours=720,
    schema={
        "index_code": "string",
        "date": "date",
        "symbol": "string",
        "weight": "float64",
    },
    primary_key=["index_code", "date", "symbol"],
    storage_layer="daily",
)

INDEX_WEIGHTS = TableSchema(
    name="index_weights",
    partition_by=None,
    ttl_hours=720,
    schema={
        "index_code": "string",
        "stock_code": "string",
        "weight": "float64",
        "update_date": "date",
        "update_time": "timestamp",
    },
    primary_key=["index_code", "stock_code", "update_date"],
    storage_layer="meta",
)

INDUSTRY_COMPONENTS = TableSchema(
    name="industry_components",
    partition_by="date",
    ttl_hours=720,
    schema={
        "industry_code": "string",
        "date": "date",
        "symbol": "string",
        "industry_name": "string",
    },
    primary_key=["industry_code", "date", "symbol"],
    priority="P1",
    storage_layer="daily",
)

INDUSTRY_LIST = TableSchema(
    name="industry_list",
    partition_by=None,
    ttl_hours=720,
    schema={
        "industry_code": "string",
        "industry_name": "string",
        "source": "string",
    },
    primary_key=["industry_code"],
    aggregation_enabled=False,
    compaction_threshold=0,
    storage_layer="meta",
    priority="P2",
)

CONCEPT_LIST = TableSchema(
    name="concept_list",
    partition_by=None,
    ttl_hours=720,
    schema={
        "concept_code": "string",
        "concept_name": "string",
        "source": "string",
    },
    primary_key=["concept_code"],
    aggregation_enabled=False,
    compaction_threshold=0,
    storage_layer="meta",
    priority="P2",
)

CONCEPT_COMPONENTS = TableSchema(
    name="concept_components",
    partition_by="date",
    ttl_hours=720,
    schema={
        "concept_code": "string",
        "concept_name": "string",
        "date": "date",
        "symbol": "string",
    },
    primary_key=["concept_code", "date", "symbol"],
    storage_layer="daily",
    priority="P1",
)

# ── Financial data ─────────────────────────────────────────────────────

FINANCE_INDICATOR = TableSchema(
    name="finance_indicator",
    partition_by="report_date",
    ttl_hours=2160,
    schema={
        "symbol": "string",
        "report_date": "date",
        "pe": "float64",
        "pb": "float64",
        "ps": "float64",
        "roe": "float64",
        "net_profit": "float64",
        "revenue": "float64",
    },
    primary_key=["symbol", "report_date"],
    compaction_threshold=5,
    storage_layer="daily",
)

FINANCIAL_REPORT = TableSchema(
    name="financial_report",
    partition_by="report_date",
    ttl_hours=2160,
    schema={
        "symbol": "string",
        "report_date": "date",
        "report_type": "string",
        "item_name": "string",
        "item_value": "float64",
    },
    primary_key=["symbol", "report_date", "report_type", "item_name"],
    compaction_threshold=5,
    storage_layer="daily",
    priority="P0",
)

FINANCIAL_BENEFIT = TableSchema(
    name="financial_benefit",
    partition_by="report_date",
    ttl_hours=2160,
    schema={
        "symbol": "string",
        "report_date": "date",
        "indicator": "string",
        "value": "float64",
    },
    primary_key=["symbol", "report_date", "indicator"],
    compaction_threshold=5,
    storage_layer="daily",
    priority="P0",
)

FUND_PORTFOLIO = TableSchema(
    name="fund_portfolio",
    partition_by="report_date",
    ttl_hours=2160,
    schema={
        "fund_code": "string",
        "report_date": "date",
        "symbol": "string",
        "hold_count": "float64",
        "hold_ratio": "float64",
        "market_value": "float64",
    },
    primary_key=["fund_code", "report_date", "symbol"],
    compaction_threshold=5,
    storage_layer="daily",
    priority="P1",
)

# ── Money flow ─────────────────────────────────────────────────────────

MONEY_FLOW = TableSchema(
    name="money_flow",
    partition_by="date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "date": "date",
        "main_net_inflow": "float64",
        "super_large_net_inflow": "float64",
        "large_net_inflow": "float64",
        "medium_net_inflow": "float64",
        "small_net_inflow": "float64",
    },
    primary_key=["symbol", "date"],
    priority="P1",
    storage_layer="daily",
)

NORTH_FLOW = TableSchema(
    name="north_flow",
    partition_by="date",
    ttl_hours=0,
    schema={
        "date": "date",
        "net_flow": "float64",
        "buy_amount": "float64",
        "sell_amount": "float64",
    },
    primary_key=["date"],
    priority="P1",
    storage_layer="daily",
)

HSGT_HOLD_SNAPSHOT = TableSchema(
    name="hsgt_hold_snapshot",
    partition_by="date",
    ttl_hours=168,
    schema={
        "symbol": "string",
        "date": "date",
        "hold_count": "float64",
        "hold_ratio": "float64",
        "change_count": "float64",
    },
    primary_key=["symbol", "date"],
    compaction_threshold=1,
    storage_layer="snapshot",
    priority="P0",
)

# ── Corporate actions ──────────────────────────────────────────────────

HOLDER = TableSchema(
    name="holder",
    partition_by="report_date",
    ttl_hours=2160,
    schema={
        "symbol": "string",
        "report_date": "date",
        "holder_name": "string",
        "hold_count": "float64",
        "hold_ratio": "float64",
        "holder_type": "string",
    },
    primary_key=["symbol", "report_date", "holder_name"],
    compaction_threshold=5,
    priority="P1",
    storage_layer="daily",
)

DIVIDEND = TableSchema(
    name="dividend",
    partition_by="announce_date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "announce_date": "date",
        "dividend_cash": "float64",
        "dividend_stock": "float64",
        "record_date": "date",
        "ex_date": "date",
    },
    primary_key=["symbol", "announce_date"],
    compaction_threshold=5,
    priority="P1",
    storage_layer="daily",
)

UNLOCK = TableSchema(
    name="unlock",
    partition_by="announce_date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "announce_date": "date",
        "unlock_date": "date",
        "unlock_count": "float64",
        "unlock_ratio": "float64",
        "unlock_type": "string",
    },
    primary_key=["symbol", "announce_date"],
    compaction_threshold=5,
    priority="P1",
    storage_layer="daily",
)

SHARE_CHANGE = TableSchema(
    name="share_change",
    partition_by="announce_date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "announce_date": "date",
        "total_shares": "float64",
        "circulating_shares": "float64",
        "change_type": "string",
    },
    primary_key=["symbol", "announce_date"],
    compaction_threshold=5,
    storage_layer="daily",
    priority="P2",
)

HOLDING_CHANGE = TableSchema(
    name="holding_change",
    partition_by="announce_date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "announce_date": "date",
        "holder_name": "string",
        "change_count": "float64",
        "change_ratio": "float64",
        "change_type": "string",
    },
    primary_key=["symbol", "announce_date", "holder_name"],
    compaction_threshold=5,
    storage_layer="daily",
    priority="P2",
)

# ── Valuation & snapshot ───────────────────────────────────────────────

VALUATION = TableSchema(
    name="valuation",
    partition_by="date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "date": "date",
        "pe": "float64",
        "pb": "float64",
        "ps": "float64",
        "market_cap": "float64",
        "circulating_cap": "float64",
    },
    primary_key=["symbol", "date"],
    priority="P1",
    storage_layer="daily",
)

SPOT_SNAPSHOT = TableSchema(
    name="spot_snapshot",
    partition_by="date",
    ttl_hours=168,
    schema={
        "symbol": "string",
        "date": "date",
        "price": "float64",
        "change_pct": "float64",
        "volume": "float64",
        "amount": "float64",
        "turnover_rate": "float64",
        "pe": "float64",
        "pb": "float64",
        "market_cap": "float64",
    },
    primary_key=["symbol", "date"],
    compaction_threshold=1,
    storage_layer="snapshot",
    priority="P0",
)

SECTOR_FLOW_SNAPSHOT = TableSchema(
    name="sector_flow_snapshot",
    partition_by="date",
    ttl_hours=168,
    schema={
        "date": "date",
        "sector_name": "string",
        "sector_type": "string",
        "change_pct": "float64",
        "net_inflow": "float64",
        "stock_count": "int64",
    },
    primary_key=["date", "sector_name", "sector_type"],
    compaction_threshold=1,
    storage_layer="snapshot",
    priority="P0",
)

# ── Minute-level data ──────────────────────────────────────────────────

STOCK_MINUTE = TableSchema(
    name="stock_minute",
    partition_by="week",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "datetime": "timestamp",
        "period": "string",
        "adjust": "string",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "amount": "float64",
    },
    primary_key=["symbol", "datetime", "period", "adjust"],
    compaction_threshold=50,
    storage_layer="minute",
    priority="P2",
)

ETF_MINUTE = TableSchema(
    name="etf_minute",
    partition_by="week",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "datetime": "timestamp",
        "period": "string",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "amount": "float64",
    },
    primary_key=["symbol", "datetime", "period"],
    compaction_threshold=50,
    storage_layer="minute",
    priority="P2",
)

CALL_AUCTION = TableSchema(
    name="call_auction",
    partition_by="date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "datetime": "timestamp",
        "price": "float64",
        "volume": "float64",
        "amount": "float64",
    },
    primary_key=["symbol", "datetime"],
    compaction_threshold=50,
    storage_layer="daily",
    priority="P3",
)

# ── Reference / metadata ───────────────────────────────────────────────

SECURITIES = TableSchema(
    name="securities",
    partition_by=None,
    ttl_hours=0,
    schema={
        "symbol": "string",
        "name": "string",
        "type": "string",
        "list_date": "date",
        "delist_date": "date",
        "exchange": "string",
    },
    primary_key=["symbol"],
    aggregation_enabled=False,
    compaction_threshold=0,
    storage_layer="meta",
    priority="P2",
)

TRADE_CALENDAR = TableSchema(
    name="trade_calendar",
    partition_by=None,
    ttl_hours=0,
    schema={
        "date": "date",
        "is_trading_day": "bool",
    },
    primary_key=["date"],
    aggregation_enabled=False,
    compaction_threshold=0,
    storage_layer="meta",
    priority="P2",
)

COMPANY_INFO = TableSchema(
    name="company_info",
    partition_by=None,
    ttl_hours=720,
    schema={
        "symbol": "string",
        "name": "string",
        "industry": "string",
        "area": "string",
        "list_date": "date",
        "market": "string",
    },
    primary_key=["symbol"],
    aggregation_enabled=False,
    compaction_threshold=0,
    storage_layer="meta",
    priority="P2",
)

INDUSTRY_MAPPING = TableSchema(
    name="industry_mapping",
    partition_by=None,
    ttl_hours=720,
    schema={
        "symbol": "string",
        "industry_code": "string",
        "industry_name": "string",
        "level": "int64",
    },
    primary_key=["symbol"],
    aggregation_enabled=False,
    compaction_threshold=0,
    storage_layer="meta",
    priority="P1",
)

STATUS_CHANGE = TableSchema(
    name="status_change",
    partition_by=None,
    ttl_hours=720,
    schema={
        "symbol": "string",
        "status_date": "date",
        "status_type": "string",
        "reason": "string",
    },
    primary_key=["symbol", "status_date"],
    aggregation_enabled=False,
    compaction_threshold=0,
    storage_layer="meta",
    priority="P2",
)

# ── Factor & macro ─────────────────────────────────────────────────────

FACTOR_CACHE = TableSchema(
    name="factor_cache",
    partition_by="factor_name",
    ttl_hours=0,
    schema={
        "factor_name": "string",
        "symbol": "string",
        "date": "date",
        "value": "float64",
    },
    primary_key=["factor_name", "symbol", "date"],
    compaction_threshold=10,
    storage_layer="daily",
    priority="P1",
)

MACRO_DATA = TableSchema(
    name="macro_data",
    partition_by=None,
    ttl_hours=720,
    schema={
        "indicator": "string",
        "date": "date",
        "value": "float64",
        "change_pct": "float64",
    },
    primary_key=["indicator", "date"],
    aggregation_enabled=False,
    compaction_threshold=0,
    storage_layer="meta",
    priority="P2",
)

# ── Margin trading ─────────────────────────────────────────────────────

MARGIN_DETAIL = TableSchema(
    name="margin_detail",
    partition_by="date",
    ttl_hours=720,
    schema={
        "market": "string",
        "date": "date",
        "symbol": "string",
        "margin_balance": "float64",
        "short_balance": "float64",
    },
    primary_key=["market", "date", "symbol"],
    storage_layer="daily",
    priority="P2",
)

MARGIN_UNDERLYING = TableSchema(
    name="margin_underlying",
    partition_by="date",
    ttl_hours=720,
    schema={
        "market": "string",
        "date": "date",
        "symbol": "string",
        "stock_name": "string",
    },
    primary_key=["market", "date", "symbol"],
    storage_layer="daily",
    priority="P2",
)

# ── Options ────────────────────────────────────────────────────────────

OPTION_DAILY = TableSchema(
    name="option_daily",
    partition_by="date",
    ttl_hours=0,
    schema={
        "symbol": "string",
        "date": "date",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "open_interest": "float64",
    },
    primary_key=["symbol", "date"],
    storage_layer="daily",
    priority="P3",
)


SCHEMA_REGISTRY = TableRegistry()

_DEFAULT_TABLES = (
    STOCK_DAILY,
    ETF_DAILY,
    INDEX_DAILY,
    FUTURES_DAILY,
    CONVERSION_BOND_DAILY,
    INDEX_COMPONENTS,
    INDEX_WEIGHTS,
    FINANCE_INDICATOR,
    MONEY_FLOW,
    NORTH_FLOW,
    INDUSTRY_COMPONENTS,
    HOLDER,
    DIVIDEND,
    VALUATION,
    UNLOCK,
    SPOT_SNAPSHOT,
    SECTOR_FLOW_SNAPSHOT,
    HSGT_HOLD_SNAPSHOT,
    STOCK_MINUTE,
    ETF_MINUTE,
    SECURITIES,
    TRADE_CALENDAR,
    INDUSTRY_LIST,
    CONCEPT_LIST,
    COMPANY_INFO,
    FACTOR_CACHE,
    FINANCIAL_REPORT,
    FINANCIAL_BENEFIT,
    INDUSTRY_MAPPING,
    CONCEPT_COMPONENTS,
    FUND_PORTFOLIO,
    SHARE_CHANGE,
    HOLDING_CHANGE,
    MACRO_DATA,
    MARGIN_DETAIL,
    MARGIN_UNDERLYING,
    STATUS_CHANGE,
    OPTION_DAILY,
    CALL_AUCTION,
)


def get_table_schema(name: str) -> TableSchema | None:
    """Look up a table schema by name.

    Args:
        name: Table name.

    Returns:
        TableSchema if found, None otherwise.
    """
    return SCHEMA_REGISTRY.get_or_none(name)


def list_tables() -> list[str]:
    """Return a sorted list of all registered table names.

    Returns:
        List of table name strings.
    """
    return sorted(SCHEMA_REGISTRY.list_all().keys())


def init_schemas() -> None:
    """Register all default table schemas into the global registry.

    Idempotent: safe to call multiple times.
    """
    for table in _DEFAULT_TABLES:
        SCHEMA_REGISTRY.register(table)


init_schemas()
