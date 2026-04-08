"""
Lixinger disclosure data provider.

This module implements the disclosure data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import DisclosureFactory, DisclosureProvider


@DisclosureFactory.register("lixinger")
class LixingerDisclosureProvider(DisclosureProvider):
    """
    Disclosure data provider using Lixinger OpenAPI.

    Provides dividend and announcement data.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch raw data - not directly used.

        Each specific method fetches its own data.
        """
        return pd.DataFrame()

    def get_dividend_data(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get dividend data from Lixinger.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized dividend data with columns:
                - symbol: Stock symbol
                - announcement_date: Announcement date (YYYY-MM-DD)
                - content: Dividend content
                - bonus_shares_from_profit: Bonus shares from profit (per 10 shares)
                - bonus_shares_from_reserve: Bonus shares from capital reserve (per 10 shares)
                - dividend_per_share: Dividend per share (yuan)
                - currency: Currency
                - dividend_amount: Total dividend amount
                - annual_net_profit: Annual net profit
                - dividend_ratio: Dividend ratio (annual net profit dividend ratio)
                - record_date: Record date (YYYY-MM-DD)
                - ex_date: Ex-dividend date (YYYY-MM-DD)
                - payment_date: Payment date (YYYY-MM-DD)
                - fiscal_year_end: Fiscal year end date (YYYY-MM-DD)
        """
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/dividend", params)

        if response.get("code") != 1:
            return self.create_empty_dataframe(
                [
                    "symbol",
                    "announcement_date",
                    "content",
                    "bonus_shares_from_profit",
                    "bonus_shares_from_reserve",
                    "dividend_per_share",
                    "currency",
                    "dividend_amount",
                    "annual_net_profit",
                    "dividend_ratio",
                    "record_date",
                    "ex_date",
                    "payment_date",
                    "fiscal_year_end",
                ]
            )

        data = response.get("data", [])
        if not data:
            return self.create_empty_dataframe(
                [
                    "symbol",
                    "announcement_date",
                    "content",
                    "bonus_shares_from_profit",
                    "bonus_shares_from_reserve",
                    "dividend_per_share",
                    "currency",
                    "dividend_amount",
                    "annual_net_profit",
                    "dividend_ratio",
                    "record_date",
                    "ex_date",
                    "payment_date",
                    "fiscal_year_end",
                ]
            )

        df = pd.DataFrame(data)
        standardized = self._standardize_dividend_data(df, symbol)

        return self.standardize_and_filter(
            standardized, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def _standardize_dividend_data(self, raw_df: pd.DataFrame, symbol: str | None) -> pd.DataFrame:
        """
        Standardize dividend data from Lixinger API.

        Args:
            raw_df: Raw data from Lixinger API
            symbol: Stock symbol (for adding to DataFrame if not present)

        Returns:
            pd.DataFrame: Standardized dividend data
        """
        if raw_df.empty:
            return self.create_empty_dataframe(
                [
                    "symbol",
                    "announcement_date",
                    "content",
                    "bonus_shares_from_profit",
                    "bonus_shares_from_reserve",
                    "dividend_per_share",
                    "currency",
                    "dividend_amount",
                    "annual_net_profit",
                    "dividend_ratio",
                    "record_date",
                    "ex_date",
                    "payment_date",
                    "fiscal_year_end",
                ]
            )

        standardized = pd.DataFrame()

        standardized["symbol"] = [symbol] * len(raw_df) if symbol else ""

        standardized["announcement_date"] = pd.to_datetime(raw_df.get("date"), errors="coerce").dt.strftime("%Y-%m-%d")

        standardized["content"] = raw_df.get("content", "").astype(str)

        standardized["bonus_shares_from_profit"] = raw_df.get("bonusSharesFromProfit")

        standardized["bonus_shares_from_reserve"] = raw_df.get("bonusSharesFromCapitalReserve")

        standardized["dividend_per_share"] = raw_df.get("dividend")

        standardized["currency"] = raw_df.get("currency", "").astype(str)

        standardized["dividend_amount"] = raw_df.get("dividendAmount")

        standardized["annual_net_profit"] = raw_df.get("annualNetProfit")

        standardized["dividend_ratio"] = raw_df.get("annualNetProfitDividendRatio")

        standardized["record_date"] = pd.to_datetime(raw_df.get("registerDate"), errors="coerce").dt.strftime(
            "%Y-%m-%d"
        )

        standardized["ex_date"] = pd.to_datetime(raw_df.get("exDate"), errors="coerce").dt.strftime("%Y-%m-%d")

        standardized["payment_date"] = pd.to_datetime(raw_df.get("paymentDate"), errors="coerce").dt.strftime(
            "%Y-%m-%d"
        )

        standardized["fiscal_year_end"] = pd.to_datetime(raw_df.get("fsEndDate"), errors="coerce").dt.strftime(
            "%Y-%m-%d"
        )

        standardized = standardized.sort_values("announcement_date", ascending=False, na_position="last").reset_index(
            drop=True
        )

        return standardized

    def get_announcement_data(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get announcement data from Lixinger.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized announcement data with columns:
                - symbol: Stock symbol
                - date: Announcement date (YYYY-MM-DD)
                - link_text: Link text
                - link_url: Link URL
                - link_type: Link type
                - types: Announcement types (list)
        """
        if symbol:
            self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/company/announcement", params)

        if response.get("code") != 1:
            return self.create_empty_dataframe(["symbol", "date", "link_text", "link_url", "link_type", "types"])

        data = response.get("data", [])
        if not data:
            return self.create_empty_dataframe(["symbol", "date", "link_text", "link_url", "link_type", "types"])

        df = pd.DataFrame(data)
        standardized = self._standardize_announcement_data(df, symbol)

        return self.standardize_and_filter(
            standardized, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def _standardize_announcement_data(self, raw_df: pd.DataFrame, symbol: str | None) -> pd.DataFrame:
        """
        Standardize announcement data from Lixinger API.

        Args:
            raw_df: Raw data from Lixinger API
            symbol: Stock symbol (for adding to DataFrame if not present)

        Returns:
            pd.DataFrame: Standardized announcement data
        """
        if raw_df.empty:
            return self.create_empty_dataframe(["symbol", "date", "link_text", "link_url", "link_type", "types"])

        standardized = pd.DataFrame()

        standardized["symbol"] = [symbol] * len(raw_df) if symbol else ""

        standardized["date"] = pd.to_datetime(raw_df.get("date"), errors="coerce").dt.strftime("%Y-%m-%d")

        standardized["link_text"] = raw_df.get("linkText", "").astype(str)

        standardized["link_url"] = raw_df.get("linkUrl", "").astype(str)

        standardized["link_type"] = raw_df.get("linkType", "").astype(str)

        standardized["types"] = raw_df.get("types")

        standardized = standardized.sort_values("date", ascending=False, na_position="last").reset_index(drop=True)

        return standardized

    def get_disclosure_news(
        self, symbol: str | None, start_date: str, end_date: str, category: str, **kwargs
    ) -> pd.DataFrame:
        """
        Get disclosure news data from Lixinger.

        This maps to announcement data with category filtering.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            category: News category ('all', 'dividend', 'repurchase', 'st', 'major_event')

        Returns:
            pd.DataFrame: Standardized disclosure news data
        """
        announcement_df = self.get_announcement_data(symbol, start_date, end_date, **kwargs)

        if announcement_df.empty:
            return self.create_empty_dataframe(["date", "symbol", "title", "category", "content", "url"])

        standardized = pd.DataFrame()
        standardized["date"] = announcement_df["date"]
        standardized["symbol"] = announcement_df["symbol"]
        standardized["title"] = announcement_df["link_text"]
        standardized["category"] = announcement_df["types"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        )
        standardized["content"] = ""
        standardized["url"] = announcement_df["link_url"]

        if category != "all":
            standardized = self._filter_announcement_by_category(standardized, category)

        return self.ensure_json_compatible(standardized)

    def _filter_announcement_by_category(self, df: pd.DataFrame, category: str) -> pd.DataFrame:
        """
        Filter announcement data by category.

        Args:
            df: Standardized announcement DataFrame
            category: Category to filter ('dividend', 'repurchase', 'st', 'major_event')

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if df.empty:
            return df

        category_type_map = {
            "dividend": ["eac"],
            "repurchase": ["srp"],
            "st": [],
            "major_event": ["bm", "sm", "shm", "so", "eat", "c_rp"],
        }

        types_to_match = category_type_map.get(category, [])
        if not types_to_match:
            keyword_map = {
                "dividend": ["分红", "派息", "红利", "股息"],
                "repurchase": ["回购", "股份回购"],
                "st": ["ST", "*ST", "退市", "风险"],
                "major_event": ["重大", "重组", "收购"],
            }
            keywords = keyword_map.get(category, [])
            if not keywords:
                return df
            mask = df["title"].str.contains("|".join(keywords), case=False, na=False) | df["category"].str.contains(
                "|".join(keywords), case=False, na=False
            )
            return df[mask].reset_index(drop=True)

        mask = df["category"].str.contains("|".join(types_to_match), case=False, na=False)
        return df[mask].reset_index(drop=True)

    def get_repurchase_data(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get stock repurchase data.

        Note: Lixinger doesn't provide dedicated repurchase API.
        This method filters announcement data for repurchase-related news.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized repurchase data
        """
        return self.create_empty_dataframe(
            ["symbol", "announcement_date", "progress", "amount", "quantity", "price_range"]
        )

    def get_st_delist_data(self, symbol: str | None, **kwargs) -> pd.DataFrame:
        """
        Get ST/delist risk data.

        Note: Lixinger doesn't provide dedicated ST/delist API.
        This method returns empty DataFrame.

        Args:
            symbol: Stock symbol (6-digit code) or None for all stocks

        Returns:
            pd.DataFrame: Standardized ST/delist risk data
        """
        return self.create_empty_dataframe(["symbol", "name", "st_type", "risk_level", "announcement_date"])
