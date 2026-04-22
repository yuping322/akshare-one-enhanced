"""
NetEase call auction (集合竞价) data provider.

This module implements the call auction data provider using NetEase 163 API as the data source.
It wraps akshare functions and standardizes the output format.
"""

import pandas as pd

from ...constants import SYMBOL_ZFILL_WIDTH
from .base import CallAuctionFactory, CallAuctionProvider


@CallAuctionFactory.register("netease")
class NetEaseCallAuctionProvider(CallAuctionProvider):
    """
    Call auction data provider using NetEase 163 API as the data source.

    This provider wraps akshare functions to fetch call auction data
    and standardizes the output format for consistency.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "netease"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from NetEase API.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def get_call_auction(self, symbol: str) -> pd.DataFrame:
        """
        Get call auction data for a single stock.

        Call auction period is 9:15-9:25 during trading hours.
        Uses ak.stock_zh_a_tick_163 to fetch tick data and filters
        for the call auction time period.

        Args:
            symbol: Stock symbol (6-digit code, e.g., '600000')

        Returns:
            pd.DataFrame: Call auction tick data with columns:
                - time: Tick time
                - price: Transaction price
                - volume: Transaction volume
                - amount: Transaction amount
                - type: Transaction type

        Example:
            >>> provider = NetEaseCallAuctionProvider()
            >>> df = provider.get_call_auction('600000')
        """
        self.validate_symbol(symbol)

        try:
            import akshare as ak

            raw_df = self.akshare_adapter.call("stock_zh_a_tick_163", symbol=symbol, trade_date="20231201")

            if raw_df.empty:
                return self.create_empty_dataframe(["time", "price", "volume", "amount", "type"])

            if "时间" in raw_df.columns or "time" in raw_df.columns:
                time_col = "时间" if "时间" in raw_df.columns else "time"
                mask = raw_df[time_col].astype(str).str.startswith(("09:1", "09:2"))
                raw_df = raw_df[mask]

            if raw_df.empty:
                return self.create_empty_dataframe(["time", "price", "volume", "amount", "type"])

            standardized = pd.DataFrame()
            time_col = "时间" if "时间" in raw_df.columns else "time"
            standardized["time"] = raw_df[time_col].astype(str)
            standardized["symbol"] = str(symbol).zfill(SYMBOL_ZFILL_WIDTH)

            if "价格" in raw_df.columns:
                standardized["price"] = raw_df["价格"].astype(float)
            elif "price" in raw_df.columns:
                standardized["price"] = raw_df["price"].astype(float)

            if "成交量" in raw_df.columns:
                standardized["volume"] = raw_df["成交量"].astype(float)
            elif "volume" in raw_df.columns:
                standardized["volume"] = raw_df["volume"].astype(float)

            if "成交额" in raw_df.columns:
                standardized["amount"] = raw_df["成交额"].astype(float)
            elif "amount" in raw_df.columns:
                standardized["amount"] = raw_df["amount"].astype(float)

            if "类型" in raw_df.columns:
                standardized["type"] = raw_df["类型"].astype(str)
            elif "type" in raw_df.columns:
                standardized["type"] = raw_df["type"].astype(str)

            result = self.ensure_json_compatible(standardized)
            return result.reset_index(drop=True)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch call auction data: {e}") from e

    def get_call_auction_batch(self, symbols: list[str]) -> pd.DataFrame:
        """
        Get call auction data for multiple stocks.

        Args:
            symbols: List of stock symbols (6-digit codes)

        Returns:
            pd.DataFrame: Combined call auction data for all stocks
        """
        frames = []
        for sym in symbols:
            try:
                df = self.get_call_auction(sym)
                if not df.empty:
                    frames.append(df)
            except Exception:
                continue

        if frames:
            return pd.concat(frames, ignore_index=True)
        return pd.DataFrame()
