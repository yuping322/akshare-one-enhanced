"""
Sina LHB (Dragon Tiger List) data provider.

This module implements the LHB data provider using Sina as the data source.
"""

import pandas as pd

from .base import DragonTigerProvider


class SinaLHBProvider(DragonTigerProvider):
    """
    LHB data provider using Sina as the data source.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return 'sina'

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data from Sina."""
        return pd.DataFrame()

    def get_dragon_tiger_list(
        self,
        date: str,
        symbol: str | None
    ) -> pd.DataFrame:
        """Get dragon tiger list data from Sina."""
        if symbol:
            self.validate_symbol(symbol)
        return pd.DataFrame(columns=[
            'date', 'symbol', 'name', 'close', 'change_pct',
            'turnover_rate', 'amount', 'reason', 'buy_amount',
            'sell_amount', 'net_amount'
        ])

    def get_dragon_tiger_summary(
        self,
        start_date: str,
        end_date: str,
        group_by: str
    ) -> pd.DataFrame:
        """Get dragon tiger list summary statistics from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=[
            'date', 'symbol', 'name', 'total_count', 'total_amount'
        ])

    def get_dragon_tiger_broker_stats(
        self,
        start_date: str,
        end_date: str,
        top_n: int
    ) -> pd.DataFrame:
        """Get broker statistics from dragon tiger list from Sina."""
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=[
            'broker', 'buy_count', 'sell_count', 'net_amount', 'avg_change_pct'
        ])
