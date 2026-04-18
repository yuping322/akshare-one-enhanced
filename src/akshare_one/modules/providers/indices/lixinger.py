"""
Lixinger provider for index data.

This module implements index data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ....lixinger_client import get_lixinger_client
from .base import IndexFactory, IndexProvider


@IndexFactory.register("lixinger")
class LixingerIndexProvider(IndexProvider):
    """
    Index data provider using Lixinger OpenAPI.

    Provides index info, constituents, historical data, fundamentals,
    drawdown, mutual market hot data, tracking funds, financial statements.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_index_hist(
        self, symbol: str, start_date: str, end_date: str, interval: str = "daily", **kwargs
    ) -> pd.DataFrame:
        """
        Get index historical/K-line data from Lixinger.

        Args:
            symbol: Index code (e.g., '000300')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (only 'daily' supported)
            **kwargs: Additional parameters (e.g., type='normal' or 'total_return')

        Returns:
            pd.DataFrame: Index historical data
        """
        client = get_lixinger_client()

        if interval != "daily":
            self.logger.warning(
                f"Lixinger only supports daily data. Requested interval '{interval}' will be ignored.",
                extra={
                    "context": {
                        "log_type": "unsupported_interval",
                        "provider": "lixinger",
                        "requested_interval": interval,
                    }
                },
            )

        candlestick_type = kwargs.get("type", "normal")
        params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date, "type": candlestick_type}

        response = client.query_api("cn/index/candlestick", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_list(self, category: str = "cn", **kwargs) -> pd.DataFrame:
        """
        Get index list from Lixinger.

        Args:
            category: Index category ('cn', 'hk', 'us')

        Returns:
            pd.DataFrame: Index list
        """
        client = get_lixinger_client()

        api_map = {"cn": "cn/index", "hk": "hk/index", "us": "us/index"}

        api_suffix = api_map.get(category, "cn/index")

        params = {}

        response = client.query_api(api_suffix, params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_constituents(
        self, symbol: str, include_weight: bool = True, start_date: str = None, end_date: str = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get index constituent stocks from Lixinger.

        Args:
            symbol: Index code
            include_weight: Whether to include weights
            start_date: Start date (YYYY-MM-DD), required for constituent-weightings
            end_date: End date (YYYY-MM-DD), optional

        Returns:
            pd.DataFrame: Index constituents
        """
        client = get_lixinger_client()

        if include_weight:
            api_suffix = "cn/index/constituent-weightings"
            flatten_field = "weightings"
            if not start_date:
                from datetime import datetime, timedelta

                end_date_dt = datetime.now()
                start_date_dt = end_date_dt - timedelta(days=365)
                start_date = start_date_dt.strftime("%Y-%m-%d")
                end_date = end_date_dt.strftime("%Y-%m-%d")
                self.logger.info(
                    f"No start_date provided for constituent-weightings, "
                    f"using default range: {start_date} to {end_date}"
                )
            params = {"stockCode": symbol, "startDate": start_date, "endDate": end_date}
        else:
            api_suffix = "cn/index/constituents"
            flatten_field = "constituents"
            params = {"stockCodes": [symbol], "date": kwargs.get("date", "latest")}

        response = client.query_api(api_suffix, params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        if flatten_field:
            flattened_data = []
            for item in data:
                if flatten_field in item and isinstance(item[flatten_field], list):
                    flattened_data.extend(item[flatten_field])
                else:
                    flattened_data.append(item)
            data = flattened_data

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_fundamental(
        self,
        symbols: list[str] | str,
        metrics: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get index fundamental data (PE/PB etc.) from Lixinger.

        Args:
            symbols: Index codes (list or single symbol, e.g., '000016' or ['000016', '000300'])
                     Maximum 100 symbols. Note: When start_date is provided, only one symbol is allowed.
            metrics: List of metrics to fetch. Metrics can be in three formats:
                     - [metricsName].[granularity].[metricsType].[statisticsDataType]
                       e.g., 'pe_ttm.y10.mcw.cvpos' (10-year market cap weighted PE percentile)
                     - [metricsName].[metricsType]
                       e.g., 'pe_ttm.mcw' (market cap weighted PE)
                     - [metricsName]
                       e.g., 'mc' (market cap), 'cp' (close point)

                     Supported metricsName:
                     - pe_ttm: PE-TTM
                     - pb: PB
                     - ps_ttm: PS-TTM
                     - dyr: Dividend yield ratio
                     - tv: Trading volume
                     - ta: Trading amount
                     - to_r: Turnover rate
                     - cp: Close point
                     - cpc: Close point change percentage
                     - cpa: Close point amplitude
                     - r_cp: Total return close point
                     - r_cpc: Total return close point change percentage
                     - mc: Market cap
                     - mc_om: A-share market cap
                     - cmc: Circulating market cap
                     - ecmc: Free floating market cap
                     And many more with statistical calculations.

                     granularity: fs/y20/y10/y5/y3/y1
                     metricsType: mcw/ew/ewpvo/avg/median
                     statisticsDataType: cv/cvpos/minv/maxv/maxpv/q5v/q8v/q2v/avgv

            date: Optional specific date (YYYY-MM-DD). Either date or start_date is required.
            start_date: Optional start date (YYYY-MM-DD). Used for date range queries.
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.
                     Note: Time range cannot exceed 10 years.

        Returns:
            pd.DataFrame: Index fundamental data with requested metrics

        Example:
            >>> provider.get_index_fundamental(
            ...     symbols='000016',
            ...     metrics=['pe_ttm.y10.mcw.cvpos', 'pe_ttm.mcw', 'mc'],
            ...     date='2026-02-17'
            ... )
        """
        client = get_lixinger_client()

        stock_codes = [symbols] if isinstance(symbols, str) else symbols

        params = {"stockCodes": stock_codes, "metricsList": metrics}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/index/fundamental", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_drawdown(
        self, symbol: str, start_date: str, end_date: str | None = None, granularity: str = "y1", **kwargs
    ) -> pd.DataFrame:
        """
        Get index drawdown data from Lixinger.

        Args:
            symbol: Index code (e.g., '000016')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.
                     Note: Time range cannot exceed 10 years.
            granularity: Drawdown cycle/period. Supported values:
                         - 'm': Month
                         - 'q': Quarter
                         - 'hy': Half year
                         - 'y1': 1 year
                         - 'y3': 3 years
                         - 'y5': 5 years
                         - 'y10': 10 years
                         - 'fs': Since listing

        Returns:
            pd.DataFrame: Index drawdown data with columns:
                - date: Data date
                - value: Drawdown value
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date, "granularity": granularity}

        if end_date:
            params["endDate"] = end_date

        response = client.query_api("cn/index/drawdown", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_hot_mm_ha(self, symbols: list[str] | str, **kwargs) -> pd.DataFrame:
        """
        Get mutual market (互联互通) hot data for indices from Lixinger.

        This provides aggregated mutual market data including holding amounts,
        net buy amounts over quarters, and ratio changes.

        Args:
            symbols: Index codes (list or single symbol, e.g., '000016')
                     Maximum 100 symbols.

        Returns:
            pd.DataFrame: Mutual market hot data with columns:
                - stock_code: Index code
                - last_data_date: Last data date
                - cpc: Price change percentage
                - mm_sha: Mutual market holding amount (陆股通持仓金额)
                - mm_sha_mc_r: Mutual market holding ratio (持仓金额占市值比例)
                - mm_sh_nba_q1-q4: Net buy amount for past 1-4 quarters
                - mm_sha_mc_rc_q1-q4: Holding ratio change for past 1-4 quarters
        """
        client = get_lixinger_client()

        stock_codes = [symbols] if isinstance(symbols, str) else symbols

        params = {"stockCodes": stock_codes}

        response = client.query_api("cn/index/hot/mm_ha", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_tracking_fund(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get funds tracking an index from Lixinger.

        Args:
            symbol: Index code (e.g., '000016')

        Returns:
            pd.DataFrame: Tracking funds data with columns:
                - name: Fund name
                - stock_code: Fund code
                - short_name: Short name
                - area_code: Area code
                - market: Market
                - exchange: Exchange
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol}

        response = client.query_api("cn/index/tracking-fund", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_fs_hybrid(
        self,
        symbols: list[str] | str,
        metrics: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get index financial statement (hybrid) data from Lixinger.

        This provides aggregated financial data for index constituents,
        such as revenue, ROE, etc., calculated at the index level.

        Args:
            symbols: Index codes (list or single symbol, e.g., '000016')
                     Maximum 100 symbols. Note: When start_date is provided, only one symbol is allowed.
            metrics: List of metrics to fetch. Format: [granularity].[tableName].[fieldName].[expressionCalculateType]
                     e.g., 'q.ps.toi.t' (quarterly cumulative total operating revenue)

                     granularity:
                     - 'y': Year
                     - 'hy': Half year
                     - 'q': Quarter

                     expressionCalculateType (varies by statement type):
                     Balance Sheet (all granularities): t/t_r/t_y2y/t_c2c/c/c_r/c_y2y/c_c2c
                     Income Statement (q/hy): t/t_r/t_y2y/t_c2c/c/c_r/c_y2y/c_c2c/c_2y/ttm/ttm_y2y/ttm_c2c
                     Cash Flow (q/hy): t/t_r/t_y2y/t_c2c/c/c_r/c_y2y/c_c2c/c_2y/ttm/ttm_y2y/ttm_c2c

                     tableName.fieldName examples:
                     - ps.oi: Operating revenue (营业收入)
                     - ps.op: Operating profit (营业利润)
                     - ps.np: Net profit (净利润)
                     - bs.ta: Total assets (资产总计)
                     - bs.tl: Total liabilities (负债合计)
                     - bs.te: Total equity (所有者权益合计)
                     - cf.noa: Net operating cash flow (经营活动现金净额)
                     And many more fields from balance sheet (bs), income statement (ps), cash flow (cf).

            date: Optional specific date (YYYY-MM-DD) or 'latest'.
                  Valid dates are end of quarters: 2017-03-31, 2017-06-30, 2017-09-30, 2017-12-31.
                  'latest' returns data from past 1.1 years.
                  Either date or start_date is required.
            start_date: Optional start date (YYYY-MM-DD). Used for date range queries.
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.
                     Note: Time range cannot exceed 10 years.

        Returns:
            pd.DataFrame: Index financial data with requested metrics

        Example:
            >>> provider.get_index_fs_hybrid(
            ...     symbols='000016',
            ...     metrics=['q.ps.oi.t'],
            ...     date='2025-09-30'
            ... )
        """
        client = get_lixinger_client()

        stock_codes = [symbols] if isinstance(symbols, str) else symbols

        params = {"stockCodes": stock_codes, "metricsList": metrics}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/index/fs/hybrid", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_mutual_market(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get index mutual market data (互联互通数据) from Lixinger.

        Args:
            symbol: Index code (e.g., '000016')
            start_date: Start date (YYYY-MM-DD). Time range cannot exceed 10 years.
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Mutual market data with columns:
                - date: Data date
                - shareholdingsMoney: Shareholdings amount (持股金额)
                - shareholdingsMoneyToMarketCap: Shareholdings ratio to market cap (港资持仓金额占市值比例)
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/index/mutual-market", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_index_margin_trading(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
                Get index margin trading and securities lending data (融资融券数据) from Lixinger.

                Args:
                    symbol: Index code (e.g., '000016')
                    start_date: Start date (YYYY-MM-DD). Time range cannot exceed 10 years.
                    end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

                Returns:
                    pd.DataFrame: Margin trading data with columns:
                        - date: Data date
        - financingBalance: Financing balance (融资余额)
                    - securitiesBalance: Securities lending balance (融券余额)
                    - financingBalanceToMarketCap: Financing balance ratio to circulating
                      market cap (融资余额占流通市值比例)
                    - securitiesBalanceToMarketCap: Securities lending balance ratio to
                      circulating market cap (融券余额占流通市值比例)
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/index/margin-trading-and-securities-lending", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )
