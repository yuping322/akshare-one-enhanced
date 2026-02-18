"""
Eastmoney ESG rating data provider.

This module implements the ESG rating data provider using Eastmoney as the data source.
It wraps akshare functions and standardizes the output format.
"""

import pandas as pd

from .base import ESGProvider


class EastmoneyESGProvider(ESGProvider):
    """
    ESG rating data provider using Eastmoney as the data source.

    This provider wraps akshare functions to fetch ESG rating data from Eastmoney
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

    def get_esg_rating(
        self,
        symbol: str | None,
        start_date: str,
        end_date: str,
        page: int = 1,
        page_size: int | None = 1,
    ) -> pd.DataFrame:
        """
        Get ESG rating data from Eastmoney.

        This method wraps akshare ESG rating functions and standardizes
        the output format.

        Args:
            symbol: Stock symbol (e.g., '600000'). If None, returns all stocks.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        page: Page number to return (default: 1)
        page_size: Number of items per page (default: 1, returns only first page)
            If None, returns all matching data.
            If specified, returns only the requested page of data.

        Returns:
            pd.DataFrame: Standardized ESG rating data with columns:
                - symbol: Stock symbol
                - rating_date: Rating date (YYYY-MM-DD)
                - esg_score: Overall ESG score
                - e_score: Environmental score
                - s_score: Social score
                - g_score: Governance score
                - rating_agency: Rating agency name

        Raises:
            ValueError: If parameters are invalid

        Example:
            >>> provider = EastmoneyESGProvider()
            >>> df = provider.get_esg_rating('600000', '2024-01-01', '2024-12-31')
        """
        # Validate parameters
        self.validate_date_range(start_date, end_date)
        if symbol:
            self.validate_symbol(symbol)

        if page < 1:
            raise ValueError(f"Page must be >= 1, got {page}")
        if page_size is not None and page_size < 1:
            raise ValueError(f"Page size must be >= 1, got {page_size}")

        try:
            import akshare as ak

            # Get ESG rating data
            # akshare function: stock_esg_rate_sina() - ESG评级数据
            raw_df = ak.stock_esg_rate_sina()

            if raw_df.empty:
                return self.create_empty_dataframe(
                    [
                        "symbol",
                        "rating_date",
                        "esg_score",
                        "e_score",
                        "s_score",
                        "g_score",
                        "rating_agency",
                    ]
                )

            # Standardize the data
            standardized = pd.DataFrame()

            # Extract symbol
            if "股票代码" in raw_df.columns:
                standardized["symbol"] = raw_df["股票代码"].astype(str).str.zfill(6)
            elif "代码" in raw_df.columns:
                standardized["symbol"] = raw_df["代码"].astype(str).str.zfill(6)
            else:
                # If no symbol column, cannot proceed
                return self.create_empty_dataframe(
                    [
                        "symbol",
                        "rating_date",
                        "esg_score",
                        "e_score",
                        "s_score",
                        "g_score",
                        "rating_agency",
                    ]
                )

            # Extract rating date
            if "评级日期" in raw_df.columns:
                standardized["rating_date"] = pd.to_datetime(raw_df["评级日期"]).dt.strftime("%Y-%m-%d")
            elif "日期" in raw_df.columns:
                standardized["rating_date"] = pd.to_datetime(raw_df["日期"]).dt.strftime("%Y-%m-%d")
            else:
                # Use end_date as default
                standardized["rating_date"] = end_date

            # Extract ESG score
            if "ESG评分" in raw_df.columns:
                standardized["esg_score"] = raw_df["ESG评分"].astype(float)
            elif "ESG得分" in raw_df.columns:
                standardized["esg_score"] = raw_df["ESG得分"].astype(float)
            elif "综合评分" in raw_df.columns:
                standardized["esg_score"] = raw_df["综合评分"].astype(float)
            else:
                standardized["esg_score"] = 0.0

            # Extract E score (Environmental)
            if "E评分" in raw_df.columns:
                standardized["e_score"] = raw_df["E评分"].astype(float)
            elif "环境评分" in raw_df.columns:
                standardized["e_score"] = raw_df["环境评分"].astype(float)
            else:
                standardized["e_score"] = 0.0

            # Extract S score (Social)
            if "S评分" in raw_df.columns:
                standardized["s_score"] = raw_df["S评分"].astype(float)
            elif "社会评分" in raw_df.columns:
                standardized["s_score"] = raw_df["社会评分"].astype(float)
            else:
                standardized["s_score"] = 0.0

            # Extract G score (Governance)
            if "G评分" in raw_df.columns:
                standardized["g_score"] = raw_df["G评分"].astype(float)
            elif "治理评分" in raw_df.columns:
                standardized["g_score"] = raw_df["治理评分"].astype(float)
            else:
                standardized["g_score"] = 0.0

            # Extract rating agency
            if "评级机构" in raw_df.columns:
                standardized["rating_agency"] = raw_df["评级机构"].astype(str)
            elif "机构" in raw_df.columns:
                standardized["rating_agency"] = raw_df["机构"].astype(str)
            else:
                standardized["rating_agency"] = "Unknown"

            # Filter by symbol if specified
            if symbol:
                standardized = standardized[standardized["symbol"] == symbol.zfill(6)]

            # Filter by date range
            mask = (standardized["rating_date"] >= start_date) & (standardized["rating_date"] <= end_date)
            result = standardized[mask].reset_index(drop=True)

            # Apply pagination
            if page_size is not None:
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                result = result.iloc[start_idx:end_idx].reset_index(drop=True)

            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch ESG rating data: {e}") from e

    def get_esg_rating_rank(self, date: str, industry: str | None, top_n: int) -> pd.DataFrame:
        """
        Get ESG rating rankings from Eastmoney.

        Args:
            date: Query date (YYYY-MM-DD)
            industry: Industry filter (optional). If None, returns all industries.
            top_n: Number of top stocks to return

        Returns:
            pd.DataFrame: ESG rating rankings with columns:
                - rank: Overall rank
                - symbol: Stock symbol
                - name: Stock name
                - esg_score: Overall ESG score
                - industry: Industry name
                - industry_rank: Rank within industry

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate date format
        try:
            from datetime import datetime

            datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD") from e

        # Validate top_n
        if top_n <= 0:
            raise ValueError(f"top_n must be positive, got {top_n}")

        try:
            import akshare as ak

            # Get ESG rating data
            # akshare function: stock_esg_rate_sina() - ESG评级数据
            raw_df = ak.stock_esg_rate_sina()

            if raw_df.empty:
                return self.create_empty_dataframe(["rank", "symbol", "name", "esg_score", "industry", "industry_rank"])

            # Standardize the data
            df = pd.DataFrame()

            # Extract symbol
            if "股票代码" in raw_df.columns:
                df["symbol"] = raw_df["股票代码"].astype(str).str.zfill(6)
            elif "代码" in raw_df.columns:
                df["symbol"] = raw_df["代码"].astype(str).str.zfill(6)
            else:
                return self.create_empty_dataframe(["rank", "symbol", "name", "esg_score", "industry", "industry_rank"])

            # Extract stock name
            if "股票简称" in raw_df.columns:
                df["name"] = raw_df["股票简称"].astype(str)
            elif "名称" in raw_df.columns:
                df["name"] = raw_df["名称"].astype(str)
            else:
                df["name"] = ""

            # Extract ESG score
            if "ESG评分" in raw_df.columns:
                df["esg_score"] = raw_df["ESG评分"].astype(float)
            elif "ESG得分" in raw_df.columns:
                df["esg_score"] = raw_df["ESG得分"].astype(float)
            elif "综合评分" in raw_df.columns:
                df["esg_score"] = raw_df["综合评分"].astype(float)
            else:
                df["esg_score"] = 0.0

            # Extract industry information
            if "所属行业" in raw_df.columns:
                df["industry"] = raw_df["所属行业"].astype(str)
            elif "行业" in raw_df.columns:
                df["industry"] = raw_df["行业"].astype(str)
            else:
                # If industry info is not available, try to fetch it separately
                # For now, use a default value
                df["industry"] = "未分类"

            # Filter by industry if specified
            if industry:
                df = df[df["industry"] == industry]

            # Sort by ESG score descending
            df = df.sort_values("esg_score", ascending=False).reset_index(drop=True)

            # Add overall rank
            df["rank"] = range(1, len(df) + 1)

            # Calculate industry rank
            df["industry_rank"] = df.groupby("industry")["esg_score"].rank(ascending=False, method="min").astype(int)

            # Limit to top_n
            result = df.head(top_n)

            # Reorder columns
            result = result[["rank", "symbol", "name", "esg_score", "industry", "industry_rank"]]

            # Ensure JSON compatibility
            return self.ensure_json_compatible(result)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch ESG rating rankings: {e}") from e
