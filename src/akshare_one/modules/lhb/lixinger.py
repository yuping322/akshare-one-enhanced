"""
Lixinger provider for dragon tiger list data.

This module implements dragon tiger list data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import DragonTigerFactory, DragonTigerProvider


@DragonTigerFactory.register("lixinger")
class LixingerDragonTigerProvider(DragonTigerProvider):
    """
    Dragon tiger list data provider using Lixinger OpenAPI.

    Provides dragon tiger list transaction details from Lixinger API.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_dragon_tiger_list(self, date: str, symbol: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get dragon tiger list data from Lixinger.

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
                - institution_buy_count: Number of buying institutions
                - institution_sell_count: Number of selling institutions
                - institution_buy_amount: Institution buy amount
                - institution_sell_amount: Institution sell amount
                - institution_net_amount: Institution net buy amount

        Raises:
            ValueError: If parameters are invalid
        """
        self.validate_date(date)
        if symbol:
            self.validate_symbol(symbol)

        client = get_lixinger_client()

        params = {"date": date}
        if symbol:
            params["stockCode"] = symbol

        response = client.query_api("cn/company/trading-abnormal", params)

        if response.get("code") != 1:
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
                    "institution_buy_count",
                    "institution_sell_count",
                    "institution_buy_amount",
                    "institution_sell_amount",
                    "institution_net_amount",
                ]
            )

        data = response.get("data", [])
        if not data:
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
                    "institution_buy_count",
                    "institution_sell_count",
                    "institution_buy_amount",
                    "institution_sell_amount",
                    "institution_net_amount",
                ]
            )

        df = pd.json_normalize(data)

        standardized = pd.DataFrame()
        standardized["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        standardized["symbol"] = df["stockCode"].astype(str).str.zfill(6) if "stockCode" in df.columns else None
        standardized["name"] = df["stockName"].astype(str) if "stockName" in df.columns else None
        standardized["close_price"] = pd.to_numeric(df.get("closePrice"), errors="coerce")
        standardized["pct_change"] = pd.to_numeric(df.get("pctChange"), errors="coerce")
        standardized["reason"] = df["reasonForDisclosure"].astype(str) if "reasonForDisclosure" in df.columns else None
        standardized["buy_amount"] = pd.to_numeric(df.get("totalPurchaseAmount"), errors="coerce")
        standardized["sell_amount"] = pd.to_numeric(df.get("totalSellAmount"), errors="coerce")
        standardized["net_amount"] = pd.to_numeric(df.get("totalNetPurchaseAmount"), errors="coerce")
        standardized["total_amount"] = standardized["buy_amount"].fillna(0) + standardized["sell_amount"].fillna(0)
        standardized["turnover_rate"] = pd.to_numeric(df.get("turnoverRate"), errors="coerce")
        standardized["institution_buy_count"] = pd.to_numeric(df.get("institutionBuyCount"), errors="coerce").astype(
            "Int64"
        )
        standardized["institution_sell_count"] = pd.to_numeric(df.get("institutionSellCount"), errors="coerce").astype(
            "Int64"
        )
        standardized["institution_buy_amount"] = pd.to_numeric(df.get("institutionBuyAmount"), errors="coerce")
        standardized["institution_sell_amount"] = pd.to_numeric(df.get("institutionSellAmount"), errors="coerce")
        standardized["institution_net_amount"] = pd.to_numeric(df.get("institutionNetPurchaseAmount"), errors="coerce")

        return self.ensure_json_compatible(standardized.reset_index(drop=True))

    def get_dragon_tiger_summary(self, start_date: str, end_date: str, group_by: str, **kwargs) -> pd.DataFrame:
        """
        Get dragon tiger list summary statistics from Lixinger.

        Note: Lixinger doesn't provide summary API directly.
        This method aggregates from dragon tiger list data.

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

        client = get_lixinger_client()

        params = {"startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/trading-abnormal", params)

        if response.get("code") != 1:
            if group_by == "stock":
                return self.create_empty_dataframe(
                    ["symbol", "name", "list_count", "net_buy_amount", "buy_amount", "sell_amount", "total_amount"]
                )
            elif group_by == "broker":
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
            else:
                return self.create_empty_dataframe(
                    ["reason", "list_count", "net_buy_amount", "buy_amount", "sell_amount", "total_amount"]
                )

        data = response.get("data", [])
        if not data:
            if group_by == "stock":
                return self.create_empty_dataframe(
                    ["symbol", "name", "list_count", "net_buy_amount", "buy_amount", "sell_amount", "total_amount"]
                )
            elif group_by == "broker":
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
            else:
                return self.create_empty_dataframe(
                    ["reason", "list_count", "net_buy_amount", "buy_amount", "sell_amount", "total_amount"]
                )

        df = pd.json_normalize(data)

        if group_by == "stock":
            df["stockCode"] = df["stockCode"].astype(str).str.zfill(6)
            summary = (
                df.groupby(["stockCode", "stockName"] if "stockName" in df.columns else ["stockCode"])
                .agg(
                    {
                        "stockCode": "count",
                        "totalNetPurchaseAmount": "sum",
                        "totalPurchaseAmount": "sum",
                        "totalSellAmount": "sum",
                    }
                )
                .reset_index()
            )

            result = pd.DataFrame()
            result["symbol"] = summary["stockCode"]
            result["name"] = summary["stockName"] if "stockName" in summary.columns else None
            result["list_count"] = (
                summary[("stockCode", "count")] if isinstance(summary.columns, pd.MultiIndex) else summary["count"]
            )
            result["net_buy_amount"] = pd.to_numeric(
                summary[("totalNetPurchaseAmount", "sum")]
                if isinstance(summary.columns, pd.MultiIndex)
                else summary["totalNetPurchaseAmount"],
                errors="coerce",
            )
            result["buy_amount"] = pd.to_numeric(
                summary[("totalPurchaseAmount", "sum")]
                if isinstance(summary.columns, pd.MultiIndex)
                else summary["totalPurchaseAmount"],
                errors="coerce",
            )
            result["sell_amount"] = pd.to_numeric(
                summary[("totalSellAmount", "sum")]
                if isinstance(summary.columns, pd.MultiIndex)
                else summary["totalSellAmount"],
                errors="coerce",
            )
            result["total_amount"] = result["buy_amount"].fillna(0) + result["sell_amount"].fillna(0)

        elif group_by == "broker":
            all_brokers = []

            for _, row in df.iterrows():
                buy_list = row.get("buyList", [])
                if buy_list:
                    for broker in buy_list:
                        all_brokers.append(
                            {
                                "branchName": broker.get("branchName", ""),
                                "buyAmount": broker.get("buyAmount", 0),
                                "sellAmount": broker.get("sellAmount", 0),
                            }
                        )

            if not all_brokers:
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

            broker_df = pd.DataFrame(all_brokers)

            summary = (
                broker_df.groupby("branchName")
                .agg(
                    {
                        "branchName": "count",
                        "buyAmount": ["sum", lambda x: (x > 0).sum()],
                        "sellAmount": ["sum", lambda x: (x > 0).sum()],
                    }
                )
                .reset_index()
            )

            result = pd.DataFrame()
            result["broker_name"] = summary["branchName"]
            result["list_count"] = summary[("branchName", "count")]
            result["buy_amount"] = pd.to_numeric(summary[("buyAmount", "sum")], errors="coerce")
            result["buy_count"] = summary[("buyAmount", "<lambda_0>")]
            result["sell_amount"] = pd.to_numeric(summary[("sellAmount", "sum")], errors="coerce")
            result["sell_count"] = summary[("sellAmount", "<lambda_0>")]
            result["total_amount"] = result["buy_amount"].fillna(0) + result["sell_amount"].fillna(0)

        else:
            summary = (
                df.groupby("reasonForDisclosure")
                .agg(
                    {
                        "reasonForDisclosure": "count",
                        "totalNetPurchaseAmount": "sum",
                        "totalPurchaseAmount": "sum",
                        "totalSellAmount": "sum",
                    }
                )
                .reset_index()
            )

            result = pd.DataFrame()
            result["reason"] = summary["reasonForDisclosure"]
            result["list_count"] = (
                summary[("reasonForDisclosure", "count")]
                if isinstance(summary.columns, pd.MultiIndex)
                else summary["count"]
            )
            result["net_buy_amount"] = pd.to_numeric(
                summary[("totalNetPurchaseAmount", "sum")]
                if isinstance(summary.columns, pd.MultiIndex)
                else summary["totalNetPurchaseAmount"],
                errors="coerce",
            )
            result["buy_amount"] = pd.to_numeric(
                summary[("totalPurchaseAmount", "sum")]
                if isinstance(summary.columns, pd.MultiIndex)
                else summary["totalPurchaseAmount"],
                errors="coerce",
            )
            result["sell_amount"] = pd.to_numeric(
                summary[("totalSellAmount", "sum")]
                if isinstance(summary.columns, pd.MultiIndex)
                else summary["totalSellAmount"],
                errors="coerce",
            )
            result["total_amount"] = result["buy_amount"].fillna(0) + result["sell_amount"].fillna(0)

        return self.ensure_json_compatible(result)

    def get_dragon_tiger_broker_stats(self, start_date: str, end_date: str, top_n: int, **kwargs) -> pd.DataFrame:
        """
        Get broker statistics from dragon tiger list from Lixinger.

        Note: Lixinger doesn't provide broker stats API directly.
        This method aggregates from dragon tiger list data.

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
        self.validate_date_range(start_date, end_date)
        if top_n <= 0:
            raise ValueError(f"top_n must be positive, got {top_n}")

        client = get_lixinger_client()

        params = {"startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/trading-abnormal", params)

        if response.get("code") != 1:
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

        data = response.get("data", [])
        if not data:
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

        all_brokers = []

        for record in data:
            buy_list = record.get("buyList", [])
            sell_list = record.get("sellList", [])

            if buy_list:
                for broker in buy_list:
                    all_brokers.append(
                        {
                            "branchName": broker.get("branchName", ""),
                            "buyAmount": broker.get("buyAmount", 0),
                            "sellAmount": broker.get("sellAmount", 0),
                        }
                    )

            if sell_list:
                for broker in sell_list:
                    all_brokers.append(
                        {
                            "branchName": broker.get("branchName", ""),
                            "buyAmount": broker.get("buyAmount", 0),
                            "sellAmount": broker.get("sellAmount", 0),
                        }
                    )

        if not all_brokers:
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

        broker_df = pd.DataFrame(all_brokers)

        summary = (
            broker_df.groupby("branchName")
            .agg(
                {
                    "branchName": "count",
                    "buyAmount": ["sum", lambda x: (x > 0).sum()],
                    "sellAmount": ["sum", lambda x: (x > 0).sum()],
                }
            )
            .reset_index()
        )

        result = pd.DataFrame()
        result["broker_name"] = summary["branchName"]
        result["list_count"] = summary[("branchName", "count")]
        result["buy_amount"] = pd.to_numeric(summary[("buyAmount", "sum")], errors="coerce")
        result["buy_count"] = summary[("buyAmount", "<lambda_0>")]
        result["sell_amount"] = pd.to_numeric(summary[("sellAmount", "sum")], errors="coerce")
        result["sell_count"] = summary[("sellAmount", "<lambda_0>")]
        result["net_amount"] = result["buy_amount"].fillna(0) - result["sell_amount"].fillna(0)
        result["total_amount"] = result["buy_amount"].fillna(0) + result["sell_amount"].fillna(0)

        result = result.sort_values("total_amount", ascending=False).head(top_n)
        result["rank"] = range(1, len(result) + 1)
        result = result.reset_index(drop=True)

        result = result[
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
        ]

        return self.ensure_json_compatible(result)
