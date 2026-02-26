"""
Eastmoney dragon tiger list data provider.

This module implements the dragon tiger list data provider using Eastmoney as the data source.
It wraps akshare functions and standardizes the output format.
"""

import pandas as pd

from .base import DragonTigerProvider


class EastmoneyDragonTigerProvider(DragonTigerProvider):
    """
    Dragon tiger list data provider using Eastmoney as the data source.

    This provider wraps akshare functions to fetch dragon tiger list data from Eastmoney
    and standardizes the output format for consistency.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data from Eastmoney.

        This method is not directly used as each specific method
        fetches its own data. Implemented for BaseProvider compatibility.

        Returns:
            pd.DataFrame: Empty DataFrame
        """
        return pd.DataFrame()

    def get_dragon_tiger_list(self, date: str, symbol: str | None = None) -> pd.DataFrame:
        """
        Get dragon tiger list data from Eastmoney.

        This method wraps akshare dragon tiger list functions and standardizes
        the output format.

        Args:
            date: Date (YYYY-MM-DD)
            symbol: Stock symbol (optional, if None returns all stocks)

        Returns:
            pd.DataFrame: Standardized dragon tiger list data with columns:
                - date: Date (YYYY-MM-DD)
                - symbol: Stock symbol
                - name: Stock name
                - close_price: Closing price
                - pct_change: Price change percentage
                - reason: Reason for being on the list
                - buy_amount: Dragon tiger list buy amount
                - sell_amount: Dragon tiger list sell amount
                - net_amount: Dragon tiger list net amount
                - total_amount: Dragon tiger list total transaction amount
                - turnover_rate: Turnover rate

        Raises:
            ValueError: If parameters are invalid

        Example:
            >>> provider = EastmoneyDragonTigerProvider()
            >>> df = provider.get_dragon_tiger_list('2024-01-01')
        """
        # Validate parameters
        self.validate_date(date)
        if symbol:
            self.validate_symbol(symbol)

        try:
            import akshare as ak

            # Call akshare function to get dragon tiger list
            # Note: akshare uses date format YYYYMMDD
            date_str = date.replace("-", "")
            raw_df = ak.stock_lhb_detail_em(start_date=date_str, end_date=date_str)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    [
                        "date",
                        "symbol",
                        "name",
                        "close_price",
                        "pct_change",
                        "reason",
                        "buy_amount",
                        "sell_amount",
                        "net_amount",
                        "total_amount",
                        "turnover_rate",
                    ]
                )

            # Filter by symbol if provided
            if symbol:
                raw_df = raw_df[raw_df["代码"].astype(str).str.zfill(6) == symbol]
                if raw_df.empty:
                    return self.create_empty_dataframe(
                        [
                            "date",
                            "symbol",
                            "name",
                            "close_price",
                            "pct_change",
                            "reason",
                            "buy_amount",
                            "sell_amount",
                            "net_amount",
                            "total_amount",
                            "turnover_rate",
                        ]
                    )

            # Standardize the data
            standardized = pd.DataFrame()
            standardized["date"] = pd.to_datetime(raw_df["上榜日"]).dt.strftime("%Y-%m-%d")
            standardized["symbol"] = raw_df["代码"].astype(str).str.zfill(6)
            standardized["name"] = raw_df["名称"].astype(str)
            standardized["close_price"] = raw_df["收盘价"].astype(float)
            standardized["pct_change"] = raw_df["涨跌幅"].astype(float)
            standardized["reason"] = raw_df["上榜原因"].astype(str)
            standardized["buy_amount"] = raw_df["龙虎榜买入额"].astype(float)
            standardized["sell_amount"] = raw_df["龙虎榜卖出额"].astype(float)
            standardized["net_amount"] = raw_df["龙虎榜净买额"].astype(float)
            standardized["total_amount"] = raw_df["龙虎榜成交额"].astype(float)
            standardized["turnover_rate"] = raw_df["换手率"].astype(float)

            # Ensure JSON compatibility
            result = self.ensure_json_compatible(standardized)
            return result.reset_index(drop=True)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch dragon tiger list data: {e}") from e

    def get_dragon_tiger_summary(self, start_date: str, end_date: str, group_by: str) -> pd.DataFrame:
        """
        Get dragon tiger list summary statistics from Eastmoney.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            group_by: Grouping dimension ('stock', 'broker', or 'reason')

        Returns:
            pd.DataFrame: Summary statistics grouped by specified dimension

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        if group_by not in ["stock", "broker", "reason"]:
            raise ValueError(f"Invalid group_by: {group_by}. Must be 'stock', 'broker', or 'reason'")

        try:
            import akshare as ak

            # For stock grouping, use the stock statistic function
            if group_by == "stock":
                # Use stock statistic function which provides aggregated data
                raw_df = ak.stock_lhb_stock_statistic_em(symbol="近一月")

                if raw_df.empty:
                    return self.create_empty_dataframe(
                        ["symbol", "name", "list_count", "net_buy_amount", "buy_amount", "sell_amount", "total_amount"]
                    )

                # Standardize the data
                result = pd.DataFrame()
                result["symbol"] = raw_df["代码"].astype(str).str.zfill(6)
                result["name"] = raw_df["名称"].astype(str)
                result["list_count"] = raw_df["上榜次数"].astype(int)
                result["net_buy_amount"] = raw_df["龙虎榜净买额"].astype(float)
                result["buy_amount"] = raw_df["龙虎榜买入额"].astype(float)
                result["sell_amount"] = raw_df["龙虎榜卖出额"].astype(float)
                result["total_amount"] = raw_df["龙虎榜总成交额"].astype(float)

            elif group_by == "broker":
                # Use broker statistic function
                raw_df = ak.stock_lhb_traderstatistic_em(symbol="近一月")

                if raw_df.empty:
                    return self.create_empty_dataframe(
                        [
                            "broker_name",
                            "list_count",
                            "buy_amount",
                            "buy_count",
                            "sell_amount",
                            "sell_count",
                            "total_amount",
                        ]
                    )

                # Standardize the data
                result = pd.DataFrame()
                result["broker_name"] = raw_df["营业部名称"].astype(str)
                result["list_count"] = raw_df["上榜次数"].astype(int)
                result["buy_amount"] = raw_df["买入额"].astype(float)
                result["buy_count"] = raw_df["买入次数"].astype(int)
                result["sell_amount"] = raw_df["卖出额"].astype(float)
                result["sell_count"] = raw_df["卖出次数"].astype(int)
                result["total_amount"] = raw_df["龙虎榜成交金额"].astype(float)

            else:  # reason
                # For reason grouping, fetch detail data and aggregate
                start_str = start_date.replace("-", "")
                end_str = end_date.replace("-", "")
                raw_df = ak.stock_lhb_detail_em(start_date=start_str, end_date=end_str)

                if raw_df.empty:
                    return self.create_empty_dataframe(
                        ["reason", "list_count", "net_buy_amount", "buy_amount", "sell_amount", "total_amount"]
                    )

                # Group by reason
                grouped = (
                    raw_df.groupby("上榜原因")
                    .agg(
                        {
                            "代码": "count",
                            "龙虎榜净买额": "sum",
                            "龙虎榜买入额": "sum",
                            "龙虎榜卖出额": "sum",
                            "龙虎榜成交额": "sum",
                        }
                    )
                    .reset_index()
                )

                result = pd.DataFrame()
                result["reason"] = grouped["上榜原因"].astype(str)
                result["list_count"] = grouped["代码"].astype(int)
                result["net_buy_amount"] = grouped["龙虎榜净买额"].astype(float)
                result["buy_amount"] = grouped["龙虎榜买入额"].astype(float)
                result["sell_amount"] = grouped["龙虎榜卖出额"].astype(float)
                result["total_amount"] = grouped["龙虎榜成交额"].astype(float)

            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch dragon tiger summary: {e}") from e

    def get_dragon_tiger_broker_stats(self, start_date: str, end_date: str, top_n: int) -> pd.DataFrame:
        """
        Get broker statistics from dragon tiger list from Eastmoney.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            top_n: Number of top brokers to return

        Returns:
            pd.DataFrame: Broker statistics with columns:
                - rank: Ranking position
                - broker_name: Broker name
                - list_count: Number of times on the list
                - buy_amount: Total buy amount
                - buy_count: Number of buy transactions
                - sell_amount: Total sell amount
                - sell_count: Number of sell transactions
                - net_amount: Net amount (buy - sell)
                - total_amount: Total transaction amount

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        if top_n <= 0:
            raise ValueError(f"top_n must be positive, got {top_n}")

        try:
            import akshare as ak

            # Call akshare function for broker statistics
            # Use the broker statistic function which provides aggregated data
            raw_df = ak.stock_lhb_traderstatistic_em(symbol="近一月")

            if raw_df.empty:
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

            # Standardize the data
            result = pd.DataFrame()
            result["rank"] = range(1, len(raw_df) + 1)
            result["broker_name"] = raw_df["营业部名称"].astype(str)
            result["list_count"] = raw_df["上榜次数"].astype(int)
            result["buy_amount"] = raw_df["买入额"].astype(float)
            result["buy_count"] = raw_df["买入次数"].astype(int)
            result["sell_amount"] = raw_df["卖出额"].astype(float)
            result["sell_count"] = raw_df["卖出次数"].astype(int)
            result["net_amount"] = result["buy_amount"] - result["sell_amount"]
            result["total_amount"] = raw_df["龙虎榜成交金额"].astype(float)

            # Sort by total amount and get top N
            result = result.sort_values("total_amount", ascending=False).head(top_n)
            result["rank"] = range(1, len(result) + 1)
            result = result.reset_index(drop=True)

            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch broker statistics: {e}") from e
