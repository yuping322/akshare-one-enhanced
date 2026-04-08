"""
Lixinger provider for ETF/fund data.

This module implements ETF/fund data provider using Lixinger OpenAPI.
"""

import pandas as pd

from .base import ETFProvider, ETFFactory
from ...lixinger_client import get_lixinger_client


@ETFFactory.register("lixinger")
class LixingerETFProvider(ETFProvider):
    """
    ETF/fund data provider using Lixinger OpenAPI.

    Provides fund info and holdings data.
    """

    _API_MAP = {}

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_etf_list(self, category: str = "all", **kwargs) -> pd.DataFrame:
        """
        Get ETF/fund list from Lixinger (alias for get_fund_info).

        Returns:
            pd.DataFrame: Fund list with symbol, name, type, inception_date, etc.
        """
        return self.get_fund_info(**kwargs)

    def get_fund_list(self, **kwargs) -> pd.DataFrame:
        """Alias for get_etf_list."""
        return self.get_etf_list(**kwargs)

    def get_fund_info(self, stock_codes: list[str] | None = None, page_index: int = 0, **kwargs) -> pd.DataFrame:
        """
        Get fund information from Lixinger.

        Args:
            stock_codes: List of fund codes (optional, returns all funds if not specified)
            page_index: Page index (default 0)

        Returns:
            pd.DataFrame: Fund information
        """
        client = get_lixinger_client()

        params = {"pageIndex": page_index}
        if stock_codes:
            params["stockCodes"] = stock_codes

        response = client.query_api("cn/fund", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "name": "name",
                "stockCode": "symbol",
                "fundFirstLevel": "fund_first_level",
                "fundSecondLevel": "fund_second_level",
                "shortName": "short_name",
                "areaCode": "area_code",
                "market": "market",
                "exchange": "exchange",
                "inceptionDate": "inception_date",
                "delistedDate": "delisted_date",
            }
        )

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_holdings(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund holdings data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Fund holdings data
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/shareholdings", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "stockCode": "stock_code",
                "stockAreaCode": "stock_area_code",
                "holdings": "holdings",
                "marketCap": "market_cap",
                "netValueRatio": "net_value_ratio",
            }
        )

        df["fund_code"] = stock_code

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_nav(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get fund NAV history from Lixinger via cn/fund/candlestick.

        Args:
            symbol: Fund code (e.g., '510050')

        Returns:
            pd.DataFrame: NAV history with date, nav, accumulated_nav, pct_change
        """
        client = get_lixinger_client()

        start_date = kwargs.get("start_date", "1970-01-01")
        end_date = kwargs.get("end_date", "2099-12-31")

        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/fund/candlestick", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)
        df["symbol"] = symbol

        rename = {
            "date": "date",
            "nav": "nav",
            "accumulatedNav": "accumulated_nav",
            "navChangeRate": "pct_change",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        for col in ["nav", "accumulated_nav", "pct_change"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_etf_hist(self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs) -> pd.DataFrame:
        """
        Get ETF historical data from Lixinger via cn/fund/candlestick.

        Note: Lixinger only supports daily data; interval is ignored.

        Args:
            symbol: ETF code (e.g., '510050')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Ignored (lixinger only provides daily)

        Returns:
            pd.DataFrame: Historical OHLCV data
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}

        response = client.query_api("cn/fund/candlestick", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)
        df["symbol"] = symbol

        rename = {
            "date": "date",
            "openPrice": "open",
            "closePrice": "close",
            "highestPrice": "high",
            "lowestPrice": "low",
            "turnoverVolume": "volume",
            "turnoverAmount": "amount",
            "changeRate": "pct_change",
            "turnoverRate": "turnover",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        for col in ["open", "close", "high", "low", "volume", "amount", "pct_change", "turnover"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_etf_spot(self, **kwargs) -> pd.DataFrame:
        """Lixinger does not provide realtime ETF quotes. Returns empty DataFrame."""
        return pd.DataFrame()

    def get_fund_manager(self, **kwargs) -> pd.DataFrame:
        """Lixinger does not provide fund manager data. Returns empty DataFrame."""
        return pd.DataFrame()

    def get_fund_rating(self, **kwargs) -> pd.DataFrame:
        """Lixinger does not provide fund rating data. Returns empty DataFrame."""
        return pd.DataFrame()
