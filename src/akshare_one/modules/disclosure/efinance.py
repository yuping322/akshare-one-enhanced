"""
Efinance disclosure data provider.

This module implements the disclosure data provider using efinance as the data source.
"""

import time

import efinance as ef
import pandas as pd

from ...logging_config import get_logger, log_api_request
from .base import DisclosureFactory, DisclosureProvider

REPORT_DATES_FIELD_MAP = {
    "报告期": "report_date",
    "报告期类型": "report_type",
}


@DisclosureFactory.register("efinance")
class EfinanceDisclosureProvider(DisclosureProvider):
    """
    Disclosure data provider using efinance as the data source.

    Provides:
    - get_all_report_dates: Get all financial report dates
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)

    def get_source_name(self) -> str:
        return "efinance"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_all_report_dates(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get all financial report dates.

        Args:
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules

        Returns:
            pd.DataFrame: List of financial report dates
        """
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching all report dates",
                extra={
                    "context": {
                        "source": "efinance",
                        "action": "fetch_start",
                    }
                },
            )

            raw_df = ef.stock.get_all_report_dates()

            if raw_df.empty:
                return pd.DataFrame(columns=columns) if columns else raw_df

            df = self._map_fields(raw_df)
            df = self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_all_report_dates",
                params={},
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
                endpoint="get_all_report_dates",
                params={},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            self.logger.error(f"Failed to fetch all report dates: {e}")
            return pd.DataFrame()

    def _map_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map efinance fields to standard field names."""
        df = df.copy()

        rename_cols = {}
        for cn_name, en_name in REPORT_DATES_FIELD_MAP.items():
            if cn_name in df.columns:
                rename_cols[cn_name] = en_name

        if rename_cols:
            df = df.rename(columns=rename_cols)

        return df


EfinanceDisclosure = EfinanceDisclosureProvider
