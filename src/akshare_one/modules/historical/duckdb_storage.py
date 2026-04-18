import logging
import os
import threading
from contextlib import contextmanager

import pandas as pd

try:
    import duckdb
except ImportError:
    raise ImportError("Please install duckdb: pip install duckdb")

from ...constants import SYMBOL_ZFILL_WIDTH

logger = logging.getLogger(__name__)

# Process-level singleton cache
_SINGLETON_CACHE: dict[str, "DuckDBManager"] = {}
_SINGLETON_LOCK = threading.Lock()


def normalize_to_jq_format(symbol: str) -> str:
    """Normalize symbol to JQ format (e.g., 600000.XSHG)."""
    if not symbol:
        return symbol

    symbol = str(symbol).strip().upper()

    if symbol.endswith((".XSHG", ".XSHE")):
        return symbol

    if symbol.startswith("SH"):
        return f"{symbol[2:].zfill(SYMBOL_ZFILL_WIDTH)}.XSHG"
    if symbol.startswith("SZ"):
        return f"{symbol[2:].zfill(SYMBOL_ZFILL_WIDTH)}.XSHE"

    # Pure numeric
    if symbol.isdigit():
        code = symbol.zfill(SYMBOL_ZFILL_WIDTH)
        if code.startswith("6"):
            return f"{code}.XSHG"
        else:
            return f"{code}.XSHE"

    return symbol


class DuckDBManager:
    """DuckDB manager for storing and querying historical market data."""

    def __init__(self, db_path: str = None, read_only: bool = False):
        if db_path is None:
            # Default to /tmp/akshare_one/data/market.db
            db_path = os.path.join("/tmp", "akshare_one", "data", "market.db")

        self.db_path = db_path
        self.read_only = read_only
        self._initialized = False
        self._lock = threading.Lock()

        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        if not read_only:
            self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = duckdb.connect(self.db_path, read_only=self.read_only)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database tables."""
        with self._lock:
            if self._initialized:
                return

            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS stock_daily (
                        symbol VARCHAR NOT NULL,
                        datetime DATE NOT NULL,
                        open DOUBLE,
                        high DOUBLE,
                        low DOUBLE,
                        close DOUBLE,
                        volume BIGINT,
                        amount DOUBLE,
                        adjust VARCHAR DEFAULT 'none',
                        PRIMARY KEY (symbol, datetime, adjust)
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_daily_symbol ON stock_daily(symbol)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_daily_date ON stock_daily(datetime)")

                # Index/ETF tables if needed, for simplicity starting with stock_daily
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS index_daily (
                        symbol VARCHAR NOT NULL,
                        datetime DATE NOT NULL,
                        open DOUBLE,
                        high DOUBLE,
                        low DOUBLE,
                        close DOUBLE,
                        volume BIGINT,
                        amount DOUBLE,
                        PRIMARY KEY (symbol, datetime)
                    )
                """)

            self._initialized = True

    def save_stock_daily(self, symbol: str, df: pd.DataFrame, adjust: str = "none"):
        """Save stock daily data to DuckDB."""
        if df is None or df.empty:
            return

        jq_symbol = normalize_to_jq_format(symbol)
        df = df.copy()

        # Mapping columns to match DuckDB schema
        if "timestamp" in df.columns and "datetime" not in df.columns:
            df = df.rename(columns={"timestamp": "datetime"})

        if "amount" not in df.columns:
            df["amount"] = 0.0

        df["symbol"] = jq_symbol
        df["adjust"] = adjust

        # Ensure datetime is date type for DuckDB
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"]).dt.date

        # Define explicit column order for insertion
        cols = ["symbol", "datetime", "open", "high", "low", "close", "volume", "amount", "adjust"]

        # Check for missing columns and fill with None if necessary
        for col in cols:
            if col not in df.columns:
                df[col] = None

        df = df[cols]

        with self._get_connection() as conn:
            # Explicitly specify columns in INSERT statement to avoid Binder errors
            col_list = ", ".join(cols)
            conn.execute(f"INSERT OR REPLACE INTO stock_daily ({col_list}) SELECT * FROM df")
            logger.info(f"Saved {len(df)} rows for {jq_symbol} ({adjust}) to DuckDB")

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str, adjust: str = "none") -> pd.DataFrame:
        """Query stock daily data from DuckDB."""
        jq_symbol = normalize_to_jq_format(symbol)

        with self._get_connection() as conn:
            query = """
                SELECT datetime, open, high, low, close, volume, amount
                FROM stock_daily
                WHERE symbol = ? AND adjust = ?
                  AND datetime >= ? AND datetime <= ?
                ORDER BY datetime
            """
            df = conn.execute(query, [jq_symbol, adjust, start_date, end_date]).fetchdf()
            return df

    @classmethod
    def get_instance(cls, db_path: str = None, read_only: bool = False):
        key = f"{db_path}_{read_only}"
        with _SINGLETON_LOCK:
            if key not in _SINGLETON_CACHE:
                _SINGLETON_CACHE[key] = cls(db_path, read_only)
            return _SINGLETON_CACHE[key]
