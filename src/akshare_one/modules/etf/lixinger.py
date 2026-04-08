"""
Lixinger provider for ETF/fund data.

This module implements ETF/fund data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import ETFFactory, ETFProvider


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

    def get_fund_net_value(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund net value (净值) data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Net value data with date, net_value
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/net-value", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "netValue": "net_value",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        if "net_value" in df.columns:
            df["net_value"] = pd.to_numeric(df["net_value"], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_total_net_value(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund total net value (累计净值) data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Total net value data with date, total_net_value
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/total-net-value", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "totalNetValue": "total_net_value",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        if "total_net_value" in df.columns:
            df["total_net_value"] = pd.to_numeric(df["total_net_value"], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_dividend(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund dividend (分红) data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Dividend data with date, ex_date, dividend
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/dividend", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "exDate": "ex_date",
                "dividend": "dividend",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        if "ex_date" in df.columns:
            df["ex_date"] = pd.to_datetime(df["ex_date"], errors="coerce").dt.strftime("%Y-%m-%d")

        if "dividend" in df.columns:
            df["dividend"] = pd.to_numeric(df["dividend"], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_asset_combination(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund asset combination (资产组合) data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Asset combination data
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/asset-combination", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "ac": "asset_combination",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_asset_industry_combination(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund asset industry combination (行业组合) data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Industry combination data
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/asset-industry-combination", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "aic_cn": "industry_combination",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_shareholders_structure(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund shareholders structure (持有人结构) data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Shareholders structure data
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/shareholders-structure", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "h_a": "holders_accounts",
                "h_s_a": "holders_shares_avg",
                "ins_h_s": "institutional_shares",
                "ins_h_s_r": "institutional_ratio",
                "ind_h_s": "individual_shares",
                "ind_h_s_r": "individual_ratio",
                "f_f_s": "feeder_fund_shares",
                "f_f_s_r": "feeder_fund_ratio",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        numeric_cols = [
            "holders_accounts",
            "holders_shares_avg",
            "institutional_shares",
            "institutional_ratio",
            "individual_shares",
            "individual_ratio",
            "feeder_fund_shares",
            "feeder_fund_ratio",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_shares(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund shares (份额) data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Shares data with date, shares, asset_scale, et_shares, et_asset_scale
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/shares", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "s": "shares",
                "as": "asset_scale",
                "et_shares": "et_shares",
                "et_as": "et_asset_scale",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        numeric_cols = ["shares", "asset_scale", "et_shares", "et_asset_scale"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_fund_split(
        self, stock_code: str, start_date: str, end_date: str | None = None, limit: int | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund split (拆分) data from Lixinger.

        Args:
            stock_code: Fund code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD, optional, defaults to last Monday)
            limit: Number of recent records to return (optional)

        Returns:
            pd.DataFrame: Split data with date, split_ratio
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}
        if end_date:
            params["endDate"] = end_date
        if limit:
            params["limit"] = limit

        response = client.query_api("cn/fund/split", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        df = df.rename(
            columns={
                "date": "date",
                "splitRatio": "split_ratio",
            }
        )

        df["symbol"] = stock_code

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

        if "split_ratio" in df.columns:
            df["split_ratio"] = pd.to_numeric(df["split_ratio"], errors="coerce")

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_etf_hist(
        self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs
    ) -> pd.DataFrame:
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
