"""
Sina equity pledge data provider.

This module implements the equity pledge data provider using Sina as the data source.
"""

from typing import Optional
import pandas as pd

from .base import EquityPledgeProvider


class SinaEquityPledgeProvider(EquityPledgeProvider):
    """
    Equity pledge data provider using Sina as the data source.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return 'sina'

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data from Sina."""
        return pd.DataFrame()

    def get_equity_pledge(
        self,
        symbol: Optional[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get equity pledge data from Sina."""
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        return pd.DataFrame(columns=[
            'date', 'symbol', 'name', 'pledgor', 'pledgee',
            'pledged_shares', 'total_shares', 'pledge_ratio', 'release_date'
        ])

    def get_equity_pledge_ratio_rank(
        self,
        date: str,
        top_n: int
    ) -> pd.DataFrame:
        """Get equity pledge ratio ranking from Sina."""
        return pd.DataFrame(columns=[
            'rank', 'symbol', 'name', 'pledge_ratio', 'pledge_amount', 'total_shares'
        ])
