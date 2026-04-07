"""
Eastmoney board data provider.
"""

import pandas as pd

from .base import BoardProvider, BoardFactory


@BoardFactory.register("eastmoney")
class EastmoneyBoardProvider(BoardProvider):
    """
    Board data provider using Eastmoney as the data source.

    Provides KCB (科创板) and CYB (创业板) stock data.
    Uses AkShareAdapter to handle function name drift across versions.
    """

    _API_MAP = {
        "get_kcb_stocks": {
            "ak_func": "stock_kcb_spot_em",
            "fallback_func": "stock_kcb_spot",  # Fallback for older versions
        },
        "get_cyb_stocks": {
            "ak_func": "stock_cyb_spot_em",
            "fallback_func": "stock_cyb_spot",  # Fallback for older versions
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch all board stocks (KCB and CYB).

        Returns:
            pd.DataFrame: Combined board stocks data.
        """
        kcb_df = self.get_kcb_stocks()
        cyb_df = self.get_cyb_stocks()

        # Concatenate results, handling empty DataFrames gracefully
        dfs = [df for df in [kcb_df, cyb_df] if not df.empty]
        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True)

    def get_kcb_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get Kechuang Board (Star Market) spot stock quotes.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: KCB stocks with price and change data.
        """
        try:
            # Use AkShareAdapter to handle function drift
            config = self._API_MAP["get_kcb_stocks"]
            raw_df = self.akshare_adapter.call(
                config["ak_func"],
                fallback_func=config.get("fallback_func"),
            )

            if raw_df.empty:
                self.logger.warning("KCB stocks data is empty")
                return pd.DataFrame()

            return self.standardize_and_filter(raw_df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch KCB stocks: {e}")
            return pd.DataFrame()

    def get_cyb_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get ChiNext (Growth Enterprise Market) spot stock quotes.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: CYB stocks with price and change data.
        """
        try:
            # Use AkShareAdapter to handle function drift
            config = self._API_MAP["get_cyb_stocks"]
            raw_df = self.akshare_adapter.call(
                config["ak_func"],
                fallback_func=config.get("fallback_func"),
            )

            if raw_df.empty:
                self.logger.warning("CYB stocks data is empty")
                return pd.DataFrame()

            return self.standardize_and_filter(raw_df, "eastmoney", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch CYB stocks: {e}")
            return pd.DataFrame()
