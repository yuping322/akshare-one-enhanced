"""
Eastmoney insider data provider.

This module implements the insider data provider using Eastmoney as the data source.
"""

import pandas as pd

from .base import InsiderDataProvider


class EastmoneyInsiderProvider(InsiderDataProvider):
    """
    Insider data provider using Eastmoney as the data source.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def get_inner_trade_data(self) -> pd.DataFrame:
        """Get insider trade data from Eastmoney."""
        return pd.DataFrame(
            columns=[
                "symbol",
                "issuer",
                "name",
                "title",
                "transaction_date",
                "transaction_shares",
                "transaction_price_per_share",
                "shares_owned_after_transaction",
                "relationship",
                "is_board_director",
                "transaction_value",
                "shares_owned_before_transaction",
            ]
        )
