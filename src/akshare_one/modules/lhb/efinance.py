"""
Efinance dragon tiger list data provider.

This module implements the dragon tiger list data provider using Efinance as the data source.
It wraps efinance functions and standardizes the output format.
"""

import pandas as pd

from .base import DragonTigerFactory, DragonTigerProvider

try:
    import efinance as ef

    EFINANCE_AVAILABLE = True
except ImportError:
    EFINANCE_AVAILABLE = False


@DragonTigerFactory.register("efinance")
class EfinanceDragonTigerProvider(DragonTigerProvider):
    """
    Dragon tiger list data provider using Efinance as the data source.

    This provider wraps efinance functions to fetch dragon tiger list data
    and standardizes the output format for consistency.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not EFINANCE_AVAILABLE:
            raise ImportError("efinance is not installed. Please install it using: pip install efinance")

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "efinance"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Efinance.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def get_dragon_tiger_list(self, date: str, symbol: str | None = None) -> pd.DataFrame:
        """
        Get dragon tiger list data from Efinance.

        This method wraps efinance dragon tiger list functions and standardizes
        the output format.

        Args:
            date: Date (YYYY-MM-DD)
            symbol: Stock symbol (optional, if None returns all stocks)

        Returns:
            pd.DataFrame: Standardized dragon tiger list data with columns:
                - date: Date (YYYY-MM-DD)
                - symbol: Stock symbol
                - name: Stock name
                - close: Closing price
                - pct_change: Price change percentage
                - net_buy: Dragon tiger list net buy amount
                - buy_amount: Dragon tiger list buy amount
                - sell_amount: Dragon tiger list sell amount
                - buy_departments: Buying departments
                - sell_departments: Selling departments
                - reason: Reason for being on the list

        Raises:
            ValueError: If parameters are invalid

        Example:
            >>> provider = EfinanceDragonTigerProvider()
            >>> df = provider.get_dragon_tiger_list('2024-01-01')
        """
        self.validate_date(date)
        if symbol:
            self.validate_symbol(symbol)

        try:
            raw_df = ef.stock.get_daily_billboard(start_date=date, end_date=date)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    [
                        "date",
                        "symbol",
                        "name",
                        "close",
                        "pct_change",
                        "net_buy",
                        "buy_amount",
                        "sell_amount",
                        "buy_departments",
                        "sell_departments",
                        "reason",
                    ]
                )

            if symbol:
                raw_df = raw_df[raw_df["股票代码"].astype(str).str.zfill(6) == symbol]
                if raw_df.empty:
                    return self.create_empty_dataframe(
                        [
                            "date",
                            "symbol",
                            "name",
                            "close",
                            "pct_change",
                            "net_buy",
                            "buy_amount",
                            "sell_amount",
                            "buy_departments",
                            "sell_departments",
                            "reason",
                        ]
                    )

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["上榜日期"]).dt.strftime("%Y-%m-%d")
            standardized["symbol"] = raw_df["股票代码"].astype(str).str.zfill(6)
            standardized["name"] = raw_df["股票名称"].astype(str)
            standardized["close"] = raw_df["收盘价"].astype(float)
            standardized["pct_change"] = raw_df["涨跌幅"].astype(float)
            standardized["net_buy"] = raw_df["龙虎榜净买额"].astype(float)
            standardized["buy_amount"] = raw_df["龙虎榜买入额"].astype(float)
            standardized["sell_amount"] = raw_df["龙虎榜卖出额"].astype(float)
            standardized["buy_departments"] = ""
            standardized["sell_departments"] = ""
            standardized["reason"] = raw_df["上榜原因"].astype(str)

            result = self.ensure_json_compatible(standardized)
            return result.reset_index(drop=True)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch dragon tiger list data: {e}") from e

    def get_dragon_tiger_summary(self, start_date: str, end_date: str, group_by: str) -> pd.DataFrame:
        """
        Get dragon tiger list summary statistics from Efinance.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            group_by: Grouping dimension ('stock', 'broker', or 'reason')

        Returns:
            pd.DataFrame: Summary statistics grouped by specified dimension

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_date_range(start_date, end_date)
        if group_by not in ["stock", "broker", "reason"]:
            raise ValueError(f"Invalid group_by: {group_by}. Must be 'stock', 'broker', or 'reason'")

        try:
            raw_df = ef.stock.get_daily_billboard(start_date=start_date, end_date=end_date)

            if raw_df.empty:
                if group_by == "stock":
                    return self.create_empty_dataframe(
                        ["symbol", "name", "list_count", "net_buy_amount", "buy_amount", "sell_amount"]
                    )
                elif group_by == "broker":
                    return self.create_empty_dataframe(["broker_name", "list_count", "buy_amount", "sell_amount"])
                else:
                    return self.create_empty_dataframe(
                        ["reason", "list_count", "net_buy_amount", "buy_amount", "sell_amount"]
                    )

            if group_by == "stock":
                grouped = (
                    raw_df.groupby(["股票代码", "股票名称"])
                    .agg(
                        {
                            "上榜日期": "count",
                            "龙虎榜净买额": "sum",
                            "龙虎榜买入额": "sum",
                            "龙虎榜卖出额": "sum",
                        }
                    )
                    .reset_index()
                )

                result = pd.DataFrame()
                result["symbol"] = grouped["股票代码"].astype(str).str.zfill(6)
                result["name"] = grouped["股票名称"].astype(str)
                result["list_count"] = grouped["上榜日期"].astype(int)
                result["net_buy_amount"] = grouped["龙虎榜净买额"].astype(float)
                result["buy_amount"] = grouped["龙虎榜买入额"].astype(float)
                result["sell_amount"] = grouped["龙虎榜卖出额"].astype(float)

            elif group_by == "reason":
                grouped = (
                    raw_df.groupby("上榜原因")
                    .agg(
                        {
                            "上榜日期": "count",
                            "龙虎榜净买额": "sum",
                            "龙虎榜买入额": "sum",
                            "龙虎榜卖出额": "sum",
                        }
                    )
                    .reset_index()
                )

                result = pd.DataFrame()
                result["reason"] = grouped["上榜原因"].astype(str)
                result["list_count"] = grouped["上榜日期"].astype(int)
                result["net_buy_amount"] = grouped["龙虎榜净买额"].astype(float)
                result["buy_amount"] = grouped["龙虎榜买入额"].astype(float)
                result["sell_amount"] = grouped["龙虎榜卖出额"].astype(float)

            else:
                return self.create_empty_dataframe(["broker_name", "list_count", "buy_amount", "sell_amount"])

            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch dragon tiger summary: {e}") from e

    def get_dragon_tiger_broker_stats(self, start_date: str, end_date: str, top_n: int) -> pd.DataFrame:
        """
        Get broker statistics from dragon tiger list from Efinance.

        Note: Efinance does not provide broker-level statistics in the daily billboard API.
        This method returns an empty DataFrame with appropriate columns.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            top_n: Number of top brokers to return

        Returns:
            pd.DataFrame: Empty DataFrame with broker statistics columns

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_date_range(start_date, end_date)
        if top_n <= 0:
            raise ValueError(f"top_n must be positive, got {top_n}")

        return self.create_empty_dataframe(
            [
                "rank",
                "broker_name",
                "list_count",
                "buy_amount",
                "buy_count",
                "sell_amount",
                "sell_count",
                "net_amount",
                "total_amount",
            ]
        )

    def get_lhb_data(self, start_date: str = "1970-01-01", end_date: str = "2030-12-31") -> pd.DataFrame:
        """
        Get dragon tiger list data (龙虎榜) for a date range from Efinance.

        This is a convenience method that wraps get_daily_billboard API.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized dragon tiger list data with columns:
                - date: Date (YYYY-MM-DD)
                - symbol: Stock symbol
                - name: Stock name
                - close: Closing price
                - pct_change: Price change percentage
                - net_buy: Dragon tiger list net buy amount
                - buy_amount: Dragon tiger list buy amount
                - sell_amount: Dragon tiger list sell amount
                - buy_departments: Buying departments
                - sell_departments: Selling departments
                - reason: Reason for being on the list

        Raises:
            ValueError: If parameters are invalid

        Example:
            >>> provider = EfinanceDragonTigerProvider()
            >>> df = provider.get_lhb_data('2024-01-01', '2024-01-31')
        """
        self.validate_date_range(start_date, end_date)

        try:
            raw_df = ef.stock.get_daily_billboard(start_date=start_date, end_date=end_date)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    [
                        "date",
                        "symbol",
                        "name",
                        "close",
                        "pct_change",
                        "net_buy",
                        "buy_amount",
                        "sell_amount",
                        "buy_departments",
                        "sell_departments",
                        "reason",
                    ]
                )

            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["上榜日期"]).dt.strftime("%Y-%m-%d")
            standardized["symbol"] = raw_df["股票代码"].astype(str).str.zfill(6)
            standardized["name"] = raw_df["股票名称"].astype(str)
            standardized["close"] = raw_df["收盘价"].astype(float)
            standardized["pct_change"] = raw_df["涨跌幅"].astype(float)
            standardized["net_buy"] = raw_df["龙虎榜净买额"].astype(float)
            standardized["buy_amount"] = raw_df["龙虎榜买入额"].astype(float)
            standardized["sell_amount"] = raw_df["龙虎榜卖出额"].astype(float)
            standardized["buy_departments"] = ""
            standardized["sell_departments"] = ""
            standardized["reason"] = raw_df["上榜原因"].astype(str)

            result = self.ensure_json_compatible(standardized)
            return result.reset_index(drop=True)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch dragon tiger list data: {e}") from e
