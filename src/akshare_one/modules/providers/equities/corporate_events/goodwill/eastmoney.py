"""
Eastmoney goodwill data provider.

This module implements the goodwill data provider using Eastmoney as the data source.
It wraps akshare functions and standardizes the output format.
"""

import time

import pandas as pd

from ......metrics.stats import get_stats_collector
from ......constants import SYMBOL_ZFILL_WIDTH
from .base import GoodwillFactory, GoodwillProvider


@GoodwillFactory.register("eastmoney")
class EastmoneyGoodwillProvider(GoodwillProvider):
    """
    Goodwill data provider using Eastmoney as the data source.

    This provider wraps akshare functions to fetch goodwill data from Eastmoney
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

    def get_goodwill_data(self, symbol: str | None, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get goodwill data from Eastmoney.

        This method wraps akshare goodwill functions and standardizes
        the output format.

        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized goodwill data with columns:
                - symbol: Stock symbol
                - report_date: Report date (YYYY-MM-DD)
                - goodwill_balance: Goodwill balance (元)
                - goodwill_ratio: Goodwill to net assets ratio (%)
                - goodwill_impairment: Goodwill impairment (元)

        Raises:
            ValueError: If parameters are invalid

        Example:
            >>> provider = EastmoneyGoodwillProvider()
            >>> df = provider.get_goodwill_data('600000', '2024-01-01', '2024-12-31')
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        if symbol:
            self.validate_symbol(symbol)

        start_time = time.time()

        try:
            import akshare as ak

            if symbol:
                # Get goodwill data for a specific stock
                # akshare function: stock_financial_abstract_ths(symbol: str = "600000", indicator: str = "商誉")
                raw_df = ak.stock_financial_abstract_ths(symbol=symbol, indicator="商誉")

                if raw_df.empty:
                    result = self.create_empty_dataframe(
                        ["symbol", "report_date", "goodwill_balance", "goodwill_ratio", "goodwill_impairment"]
                    )
                    duration_ms = (time.time() - start_time) * 1000
                    stats_collector = get_stats_collector()
                    stats_collector.record_request("eastmoney", duration_ms, True)
                    return result

                # Standardize the data
                standardized = pd.DataFrame()
                standardized["report_date"] = pd.to_datetime(raw_df["报告期"]).dt.strftime("%Y-%m-%d")
                standardized["symbol"] = symbol.zfill(SYMBOL_ZFILL_WIDTH)

                # Extract goodwill balance (商誉余额)
                if "商誉" in raw_df.columns:
                    standardized["goodwill_balance"] = raw_df["商誉"].astype(float)
                else:
                    standardized["goodwill_balance"] = 0.0

                # Calculate goodwill ratio (商誉占净资产比)
                # This requires net assets data, which may not be in the same dataset
                # For now, set to 0.0 or calculate if data is available
                standardized["goodwill_ratio"] = 0.0

                # Extract goodwill impairment (商誉减值)
                if "商誉减值" in raw_df.columns:
                    standardized["goodwill_impairment"] = raw_df["商誉减值"].astype(float)
                else:
                    standardized["goodwill_impairment"] = 0.0

                # Filter by date range
                mask = (standardized["report_date"] >= start_date) & (standardized["report_date"] <= end_date)
                result = standardized[mask].reset_index(drop=True)

            else:
                # Get goodwill data for all stocks
                # akshare function: stock_sy_profile_em() - 商誉概况
                raw_df = ak.stock_sy_profile_em()

                if raw_df.empty:
                    result = self.create_empty_dataframe(
                        ["symbol", "report_date", "goodwill_balance", "goodwill_ratio", "goodwill_impairment"]
                    )
                    duration_ms = (time.time() - start_time) * 1000
                    stats_collector = get_stats_collector()
                    stats_collector.record_request("eastmoney", duration_ms, True)
                    return result

                # Standardize the data
                standardized = pd.DataFrame()

                # Extract report date first (needed for row count)
                if "报告期" in raw_df.columns:
                    standardized["report_date"] = pd.to_datetime(raw_df["报告期"]).dt.strftime("%Y-%m-%d")
                else:
                    # Use end_date as default
                    standardized["report_date"] = end_date

                # Handle both cases: with stock codes (individual data) or without (aggregate data)
                if "股票代码" in raw_df.columns:
                    # Individual stock data - normalize stock codes with zfill
                    standardized["symbol"] = raw_df["股票代码"].astype(str).str.zfill(SYMBOL_ZFILL_WIDTH)
                else:
                    # Aggregate data without stock codes - use 'ALL' placeholder without zfill
                    standardized["symbol"] = pd.Series(["ALL"] * len(standardized), dtype=str)

                # Extract goodwill balance
                if "商誉" in raw_df.columns:
                    standardized["goodwill_balance"] = raw_df["商誉"].astype(float)
                elif "商誉余额" in raw_df.columns:
                    standardized["goodwill_balance"] = raw_df["商誉余额"].astype(float)
                else:
                    standardized["goodwill_balance"] = 0.0

                # Extract goodwill ratio
                if "商誉占净资产比例" in raw_df.columns:
                    standardized["goodwill_ratio"] = raw_df["商誉占净资产比例"].astype(float)
                elif "商誉/净资产" in raw_df.columns:
                    standardized["goodwill_ratio"] = raw_df["商誉/净资产"].astype(float)
                else:
                    standardized["goodwill_ratio"] = 0.0

                # Extract goodwill impairment
                if "商誉减值" in raw_df.columns:
                    standardized["goodwill_impairment"] = raw_df["商誉减值"].astype(float)
                else:
                    standardized["goodwill_impairment"] = 0.0

                # Filter by date range
                mask = (standardized["report_date"] >= start_date) & (standardized["report_date"] <= end_date)
                result = standardized[mask].reset_index(drop=True)

            # Ensure JSON compatibility
            result = self.ensure_json_compatible(result)

            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, True)

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, False)
            raise RuntimeError(f"Failed to fetch goodwill data: {e}") from e

    def get_goodwill_impairment(self, date: str) -> pd.DataFrame:
        """
        Get goodwill impairment expectations from Eastmoney.

        Args:
            date: Query date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Goodwill impairment expectations with columns:
                - symbol: Stock symbol
                - name: Stock name
                - goodwill_balance: Goodwill balance (元)
                - expected_impairment: Expected impairment amount (元)
                - risk_level: Risk level (high/medium/low)

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate date format
        try:
            from datetime import datetime

            datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD") from e

        start_time = time.time()

        try:
            import akshare as ak

            # Get goodwill impairment expectations
            # akshare function: stock_sy_jz_em() - 商誉减值预期
            raw_df = ak.stock_sy_jz_em()

            if raw_df is None or raw_df.empty:
                result = self.create_empty_dataframe(
                    ["symbol", "name", "goodwill_balance", "expected_impairment", "risk_level"]
                )
                duration_ms = (time.time() - start_time) * 1000
                stats_collector = get_stats_collector()
                stats_collector.record_request("eastmoney", duration_ms, True)
                return result

            # Standardize the data
            standardized = pd.DataFrame()
            standardized["symbol"] = raw_df["股票代码"].astype(str).str.zfill(SYMBOL_ZFILL_WIDTH)
            standardized["name"] = raw_df["股票简称"].astype(str)

            # Extract goodwill balance
            if "商誉" in raw_df.columns:
                standardized["goodwill_balance"] = raw_df["商誉"].astype(float)
            elif "商誉余额" in raw_df.columns:
                standardized["goodwill_balance"] = raw_df["商誉余额"].astype(float)
            else:
                standardized["goodwill_balance"] = 0.0

            # Extract expected impairment
            if "预计商誉减值" in raw_df.columns:
                standardized["expected_impairment"] = raw_df["预计商誉减值"].astype(float)
            elif "商誉减值" in raw_df.columns:
                standardized["expected_impairment"] = raw_df["商誉减值"].astype(float)
            else:
                standardized["expected_impairment"] = 0.0

            # Calculate risk level based on impairment ratio
            def calculate_risk_level(row):
                if row["goodwill_balance"] == 0:
                    return "low"
                impairment_ratio = row["expected_impairment"] / row["goodwill_balance"]
                if impairment_ratio >= 0.5:
                    return "high"
                elif impairment_ratio >= 0.2:
                    return "medium"
                else:
                    return "low"

            standardized["risk_level"] = standardized.apply(calculate_risk_level, axis=1)

            # Ensure JSON compatibility
            result = self.ensure_json_compatible(standardized)

            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, True)

            return result

        except (TypeError, KeyError):
            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, False)
            return self.create_empty_dataframe(
                ["symbol", "name", "goodwill_balance", "expected_impairment", "risk_level"]
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, False)
            raise RuntimeError(f"Failed to fetch goodwill impairment expectations: {e}") from e

    def get_goodwill_by_industry(self, date: str) -> pd.DataFrame:
        """
        Get goodwill statistics by industry from Eastmoney.

        Args:
            date: Query date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Industry goodwill statistics with columns:
                - industry: Industry name
                - total_goodwill: Total goodwill amount (元)
                - avg_ratio: Average goodwill to net assets ratio (%)
                - total_impairment: Total impairment amount (元)
                - company_count: Number of companies

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate date format
        try:
            from datetime import datetime

            datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD") from e

        start_time = time.time()

        try:
            import akshare as ak

            # Get goodwill data for all stocks first
            # akshare function: stock_sy_profile_em() - 商誉概况
            raw_df = ak.stock_sy_profile_em()

            if raw_df is None or raw_df.empty:
                result = self.create_empty_dataframe(
                    ["industry", "total_goodwill", "avg_ratio", "total_impairment", "company_count"]
                )
                duration_ms = (time.time() - start_time) * 1000
                stats_collector = get_stats_collector()
                stats_collector.record_request("eastmoney", duration_ms, True)
                return result

            # Check if data contains industry column for grouping
            # If "所属行业" exists, group by industry
            # Otherwise, return market-level aggregate as "全市场"

            if "所属行业" in raw_df.columns:
                # Group by industry
                grouped = raw_df.groupby("所属行业")

                industry_stats = pd.DataFrame()
                industry_stats["industry"] = grouped.groups.keys()
                industry_stats = industry_stats.reset_index(drop=True)

                # Calculate aggregates for each industry
                if "商誉" in raw_df.columns:
                    industry_stats["total_goodwill"] = grouped["商誉"].sum().values
                else:
                    industry_stats["total_goodwill"] = 0.0

                if "商誉占净资产比例" in raw_df.columns:
                    industry_stats["avg_ratio"] = grouped["商誉占净资产比例"].mean().values
                else:
                    industry_stats["avg_ratio"] = 0.0

                if "商誉减值" in raw_df.columns:
                    industry_stats["total_impairment"] = grouped["商誉减值"].sum().values
                else:
                    industry_stats["total_impairment"] = 0.0

                industry_stats["company_count"] = grouped.size().values
            else:
                # No industry column - return market-level aggregate
                # Extract goodwill balance
                if "商誉" in raw_df.columns:
                    total_goodwill = raw_df["商誉"].sum()
                else:
                    total_goodwill = 0.0

                # Extract goodwill ratio (average)
                if "商誉占净资产比例" in raw_df.columns:
                    avg_ratio = raw_df["商誉占净资产比例"].mean()
                else:
                    avg_ratio = 0.0

                # Extract goodwill impairment (total)
                if "商誉减值" in raw_df.columns:
                    total_impairment = raw_df["商誉减值"].sum()
                else:
                    total_impairment = 0.0

                # Return market-level data as single industry entry
                industry_stats = pd.DataFrame(
                    {
                        "industry": ["全市场"],
                        "total_goodwill": [total_goodwill],
                        "avg_ratio": [avg_ratio],
                        "total_impairment": [total_impairment],
                        "company_count": [len(raw_df)],
                    }
                )

            # Sort by total goodwill descending
            industry_stats = industry_stats.sort_values("total_goodwill", ascending=False).reset_index(drop=True)

            # Ensure JSON compatibility
            result = self.ensure_json_compatible(industry_stats)

            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, True)

            return result

        except (TypeError, KeyError):
            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, False)
            return self.create_empty_dataframe(
                ["industry", "total_goodwill", "avg_ratio", "total_impairment", "company_count"]
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, False)
            raise RuntimeError(f"Failed to fetch goodwill statistics by industry: {e}") from e
