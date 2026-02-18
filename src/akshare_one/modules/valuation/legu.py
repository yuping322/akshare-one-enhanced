"""
Legu (乐咕乐股) valuation data provider.

This module implements the valuation data provider using Legu as the data source.
"""

import pandas as pd

from .base import ValuationProvider


class LeguValuationProvider(ValuationProvider):
    """
    Valuation data provider using Legu (乐咕乐股) as the data source.

    Legu provides market valuation data including:
    - A-share PE/PB history
    - Market-wide indicators
    """

    def __init__(self):
        """Initialize the Legu valuation provider."""
        super().__init__()

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "legu"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data. Not used directly."""
        return pd.DataFrame()

    def get_stock_valuation(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get stock valuation data.

        Note: Legu doesn't provide individual stock valuation.
        Returns empty DataFrame.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame(
            columns=[
                "date",
                "symbol",
                "close",
                "pe_ttm",
                "pe_static",
                "pb",
                "ps",
                "pcf",
                "peg",
                "market_cap",
                "float_market_cap",
            ]
        )

    def get_market_valuation(self) -> pd.DataFrame:
        """
        Get market-wide valuation data from Legu.

        Returns:
            pd.DataFrame: Market valuation data
        """
        import akshare as ak

        try:
            df = ak.stock_a_pe_and_pb_em(symbol="上证指数")

            if df.empty:
                return pd.DataFrame()

            df = df.rename(columns={"date": "date", "pe": "pe", "pb": "pb"})

            df["index_name"] = "上证指数"

            cols = ["date", "index_name", "pe", "pb"]

            return df[[c for c in cols if c in df.columns]]
        except Exception:
            return pd.DataFrame()
