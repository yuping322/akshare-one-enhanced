"""
Efinance index data provider.

This module implements the index data provider using efinance as the data source.
"""

import time

import efinance as ef
import pandas as pd

from ...logging_config import get_logger, log_api_request
from .base import IndexFactory, IndexProvider

INDEX_MEMBERS_FIELD_MAP = {
    "股票代码": "symbol",
    "股票名称": "name",
    "指数代码": "index_code",
}


@IndexFactory.register("efinance")
class EfinanceIndexProvider(IndexProvider):
    """
    Index data provider using efinance as the data source.

    Provides:
    - get_members: Get stocks in an index (e.g., 沪深300成分股)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)

    def get_source_name(self) -> str:
        return "efinance"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_members(
        self,
        index_code: str,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get stocks in an index (index constituent stocks).

        Args:
            index_code: Index code (e.g., '000300' for 沪深300, '000016' for 上证50)
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules

        Returns:
            pd.DataFrame: List of stocks in the index
        """
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching index members data",
                extra={
                    "context": {
                        "source": "efinance",
                        "index_code": index_code,
                        "action": "fetch_start",
                    }
                },
            )

            raw_df = ef.stock.get_members(index_code)

            if raw_df.empty:
                return pd.DataFrame(columns=columns) if columns else raw_df

            df = self._map_fields(raw_df, index_code)
            df = self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_members",
                params={"index_code": index_code},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return df

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_members",
                params={"index_code": index_code},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            self.logger.error(f"Failed to fetch index members for {index_code}: {e}")
            return pd.DataFrame()

    def _map_fields(self, df: pd.DataFrame, index_code: str) -> pd.DataFrame:
        """Map efinance fields to standard field names."""
        df = df.copy()

        rename_cols = {}
        for cn_name, en_name in INDEX_MEMBERS_FIELD_MAP.items():
            if cn_name in df.columns:
                rename_cols[cn_name] = en_name

        if rename_cols:
            df = df.rename(columns=rename_cols)

        if "index_code" not in df.columns:
            df["index_code"] = index_code

        return df


EfinanceIndex = EfinanceIndexProvider
