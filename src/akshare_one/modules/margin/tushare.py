"""
Tushare margin financing data provider.

This module provides margin financing data from Tushare Pro API.
"""

import pandas as pd
from typing import Optional

from ..cache import cache
from .base import MarginFactory, MarginProvider
from ...tushare_client import get_tushare_client


@MarginFactory.register("tushare")
class TushareMarginProvider(MarginProvider):
    """Margin financing data provider for Tushare Pro."""

    def get_source_name(self) -> str:
        return "tushare"

    def _convert_symbol_to_ts_code(self, symbol: str) -> str:
        """Convert symbol to Tushare ts_code format."""
        if "." in symbol:
            return symbol
        elif symbol.startswith("6"):
            return f"{symbol}.SH"
        elif symbol.startswith(("0", "3")):
            return f"{symbol}.SZ"
        elif symbol.startswith(("4", "8", "9")):
            return f"{symbol}.BJ"
        else:
            return f"{symbol}.SH"

    def _convert_date_format(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to YYYYMMDD format for Tushare."""
        return date_str.replace("-", "")

    def _convert_market_to_exchange(self, market: str) -> Optional[str]:
        """Convert market parameter to Tushare exchange format."""
        if market == "sh":
            return "SSE"
        elif market == "sz":
            return "SZSE"
        else:
            return None

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Tushare.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    @cache(
        "margin_cache",
        key=lambda self,
        symbol=None,
        start_date="1970-01-01",
        end_date="2030-12-31",
        columns=None,
        row_filter=None: f"tushare_margin_detail_{symbol}_{start_date}_{end_date}",
    )
    def get_margin_data(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get margin financing detail data from Tushare.

        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized margin financing data with columns:
                - date: Date (YYYY-MM-DD)
                - symbol: Stock symbol
                - name: Stock name
                - margin_balance: Margin financing balance (元)
                - margin_buy: Margin financing buy amount (元)
                - short_balance: Short selling balance (元)
                - short_sell_volume: Short selling volume (股)
                - total_balance: Total margin balance (元)

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_date_range(start_date, end_date)
        if symbol:
            self.validate_symbol(symbol)

        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            if symbol:
                ts_code = self._convert_symbol_to_ts_code(symbol)
                raw_df = client.get_margin_detail(ts_code=ts_code, start_date=start_date_ts, end_date=end_date_ts)
            else:
                raw_df = client.get_margin_detail(start_date=start_date_ts, end_date=end_date_ts)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    [
                        "date",
                        "symbol",
                        "name",
                        "margin_balance",
                        "margin_buy",
                        "short_balance",
                        "short_sell_volume",
                        "total_balance",
                    ]
                )

            result = self._process_margin_detail(raw_df)
            return self.apply_data_filter(result, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(f"Failed to get margin detail data from Tushare: {e}")
            return pd.DataFrame()

    def _process_margin_detail(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize margin detail data."""
        df = pd.DataFrame()

        if "trade_date" in raw_df.columns:
            df["date"] = pd.to_datetime(raw_df["trade_date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")

        if "ts_code" in raw_df.columns:
            df["symbol"] = raw_df["ts_code"].str.split(".").str[0].str.zfill(6)

        df["name"] = ""

        if "rzye" in raw_df.columns:
            df["margin_balance"] = raw_df["rzye"].astype(float) * 10000

        if "rzmre" in raw_df.columns:
            df["margin_buy"] = raw_df["rzmre"].astype(float) * 10000

        if "rqye" in raw_df.columns:
            df["short_balance"] = raw_df["rqye"].astype(float) * 10000

        if "rqmcl" in raw_df.columns:
            df["short_sell_volume"] = raw_df["rqmcl"].astype(float)

        if "rzye" in raw_df.columns and "rqye" in raw_df.columns:
            df["total_balance"] = (raw_df["rzye"] + raw_df["rqye"]).astype(float) * 10000

        df = df.sort_values("date").reset_index(drop=True)

        return self.ensure_json_compatible(df)

    @cache(
        "margin_cache",
        key=lambda self,
        start_date="1970-01-01",
        end_date="2030-12-31",
        market="all",
        columns=None,
        row_filter=None: f"tushare_margin_{market}_{start_date}_{end_date}",
    )
    def get_margin_summary(
        self,
        start_date: str,
        end_date: str,
        market: str,
        columns: Optional[list] = None,
        row_filter: Optional[dict] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get margin financing summary data from Tushare.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            market: Market ('sh', 'sz', or 'all')

        Returns:
            pd.DataFrame: Summary data with columns:
                - date: Date (YYYY-MM-DD)
                - market: Market ('sh', 'sz', or 'all')
                - margin_balance: Total margin financing balance (元)
                - short_balance: Total short selling balance (元)
                - total_balance: Total margin balance (元)

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_date_range(start_date, end_date)
        if market not in ["sh", "sz", "all"]:
            raise ValueError(f"Invalid market: {market}. Must be 'sh', 'sz', or 'all'")

        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date)
        end_date_ts = self._convert_date_format(end_date)

        try:
            results = []

            if market in ["sh", "all"]:
                raw_df_sh = client.get_margin(exchange="SSE", start_date=start_date_ts, end_date=end_date_ts)
                if not raw_df_sh.empty:
                    processed_sh = self._process_margin_summary(raw_df_sh, "sh")
                    results.append(processed_sh)

            if market in ["sz", "all"]:
                raw_df_sz = client.get_margin(exchange="SZSE", start_date=start_date_ts, end_date=end_date_ts)
                if not raw_df_sz.empty:
                    processed_sz = self._process_margin_summary(raw_df_sz, "sz")
                    results.append(processed_sz)

            if not results:
                return self.create_empty_dataframe(
                    ["date", "market", "margin_balance", "short_balance", "total_balance"]
                )

            result_df = pd.concat(results, ignore_index=True)

            if market == "all":
                all_data = (
                    result_df.groupby("date")
                    .agg({"margin_balance": "sum", "short_balance": "sum", "total_balance": "sum"})
                    .reset_index()
                )
                all_data["market"] = "all"
                result_df = pd.concat([result_df, all_data], ignore_index=True)

            result_df = result_df.sort_values(["date", "market"]).reset_index(drop=True)

            return self.apply_data_filter(result_df, columns=columns, row_filter=row_filter)

        except Exception as e:
            self.logger.error(f"Failed to get margin summary data from Tushare: {e}")
            return pd.DataFrame()

    def _process_margin_summary(self, raw_df: pd.DataFrame, market: str) -> pd.DataFrame:
        """Process and standardize margin summary data."""
        df = pd.DataFrame()

        if "trade_date" in raw_df.columns:
            df["date"] = pd.to_datetime(raw_df["trade_date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")

        df["market"] = market

        if "rzye" in raw_df.columns:
            df["margin_balance"] = raw_df["rzye"].astype(float) * 100000000

        if "rqye" in raw_df.columns:
            df["short_balance"] = raw_df["rqye"].astype(float) * 100000000

        if "rzye" in raw_df.columns and "rqye" in raw_df.columns:
            df["total_balance"] = (raw_df["rzye"] + raw_df["rqye"]).astype(float) * 100000000

        df = df.sort_values("date").reset_index(drop=True)

        return self.ensure_json_compatible(df)
