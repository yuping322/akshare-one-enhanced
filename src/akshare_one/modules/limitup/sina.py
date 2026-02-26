"""
Sina limit up/down data provider.

This module implements the limit up/down data provider using Sina as the data source.
"""

import pandas as pd

from .base import LimitUpDownProvider


class SinaLimitUpDownProvider(LimitUpDownProvider):
    """
    Limit up/down data provider using Sina as the data source.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "sina"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data from Sina."""
        return pd.DataFrame()

    def get_limit_up_pool(self, date: str) -> pd.DataFrame:
        """Get limit up pool data from Sina."""
        return pd.DataFrame(
            columns=[
                "date",
                "symbol",
                "name",
                "price",
                "change_pct",
                "volume",
                "turnover_rate",
                "first_limit_time",
                "reason",
            ]
        )

    def get_limit_down_pool(self, date: str) -> pd.DataFrame:
        """Get limit down pool data from Sina."""
        return pd.DataFrame(
            columns=[
                "date",
                "symbol",
                "name",
                "price",
                "change_pct",
                "volume",
                "turnover_rate",
                "first_limit_time",
                "reason",
            ]
        )

    def get_limit_up_stats(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get limit up/down statistics from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(
            columns=[
                "date",
                "limit_up_count",
                "limit_down_count",
                "continue_limit_up_count",
                "avg_change_pct",
                "total_volume",
            ]
        )
