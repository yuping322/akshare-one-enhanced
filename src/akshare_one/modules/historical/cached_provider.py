import logging
import pandas as pd
from typing import Optional, List

from .base import HistoricalDataProvider, HistoricalDataFactory
from .duckdb_storage import DuckDBManager, normalize_to_jq_format

logger = logging.getLogger(__name__)

@HistoricalDataFactory.register("duckdb_cache")
class CachedHistoricalProvider(HistoricalDataProvider):
    """
    Transparent caching provider that uses DuckDB for local storage.
    If data is not found in cache, it falls back to a real data source,
    fetches the data, caches it, and returns it.
    """

    def __init__(
        self,
        symbol: str,
        interval: str = "day",
        interval_multiplier: int = 1,
        start_date: str = "1970-01-01",
        end_date: str = "2030-12-31",
        adjust: str = "none",
        fallback_source: str = "eastmoney_direct",
        **kwargs,
    ) -> None:
        super().__init__(
            symbol=symbol,
            interval=interval,
            interval_multiplier=interval_multiplier,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            **kwargs,
        )
        self.fallback_source = fallback_source
        self.db = DuckDBManager.get_instance()

    def get_source_name(self) -> str:
        return "duckdb_cache"

    def fetch_data(self) -> pd.DataFrame:
        """Fetches data from cache or fallback source."""
        # For now, only supporting daily data for cache
        if self.interval != "day":
            logger.debug(f"Cache only supported for daily data, falling back to {self.fallback_source}")
            return self._fetch_from_fallback()

        # 1. Try to get from DuckDB
        df = self.db.get_stock_daily(
            symbol=self.symbol,
            start_date=self.start_date,
            end_date=self.end_date,
            adjust=self.adjust
        )

        # 2. Check if we have enough data (simplified check: if empty, fetch from fallback)
        # In a real scenario, we might check if the date range is fully covered
        if df.empty:
            logger.info(f"Cache miss for {self.symbol} ({self.start_date} to {self.end_date}), fetching from {self.fallback_source}")
            df = self._fetch_from_fallback()
            if not df.empty:
                # 3. Save to cache
                self.db.save_stock_daily(self.symbol, df, self.adjust)
        else:
            logger.debug(f"Cache hit for {self.symbol} ({len(df)} rows)")

        return df

    def _fetch_from_fallback(self) -> pd.DataFrame:
        """Helper to fetch data from the fallback provider."""
        try:
            # We must be careful not to create a circular dependency or infinite loop
            # We use the factory to get the real provider
            provider = HistoricalDataFactory.get_provider(
                self.fallback_source,
                symbol=self.symbol,
                interval=self.interval,
                interval_multiplier=self.interval_multiplier,
                start_date=self.start_date,
                end_date=self.end_date,
                adjust=self.adjust
            )
            return provider.fetch_data()
        except Exception as e:
            logger.error(f"Fallback fetch failed from {self.fallback_source}: {e}")
            return pd.DataFrame()

    def get_hist_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Override to implement the caching logic."""
        df = self.fetch_data()
        
        # Apply columns and row filters (though BaseFactory usually does this, 
        # we might want to do it here if we are bypassing some of that logic)
        # Actually BaseFactory.call_provider_method calls provider.method and then applies filters.
        # So we just need to return the DataFrame.
        return df
