"""
Lixinger provider for HK stock data.

This module implements HK stock data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import HKUSFactory, HKUSProvider


@HKUSFactory.register("lixinger")
class LixingerHkusProvider(HKUSProvider):
    """
    HK stock data provider using Lixinger OpenAPI.

    Provides HK company info and index info.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_hk_company_info(
        self,
        stock_codes: list[str] | None = None,
        fs_table_type: str | None = None,
        mutual_markets: list[str] | None = None,
        include_delisted: bool = False,
        page_index: int = 0,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company information from Lixinger.

        Args:
            stock_codes: List of stock codes (e.g., ['00700']). None returns all stocks.
            fs_table_type: Financial statement type. Options:
                - 'non_financial': Non-financial companies
                - 'bank': Banks
                - 'security': Securities
                - 'insurance': Insurance
                - 'reit': Real estate investment trusts
                - 'other_financial': Other financial institutions
            mutual_markets: Mutual market types. Options: ['ah'] for HK-SZ/HK-SH stocks
            include_delisted: Whether to include delisted stocks
            page_index: Page index (default 0)
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: HK company information
        """
        client = get_lixinger_client()

        params = {"pageIndex": page_index}

        if stock_codes:
            params["stockCodes"] = stock_codes

        if fs_table_type:
            params["fsTableType"] = fs_table_type

        if mutual_markets:
            params["mutualMarkets"] = mutual_markets

        if include_delisted:
            params["includeDelisted"] = True

        response = client.query_api("hk/company", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_info(
        self,
        stock_codes: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index information from Lixinger.

        Args:
            stock_codes: List of index codes (e.g., ['HSI']). None returns all indices.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: HK index information
        """
        client = get_lixinger_client()

        params = {}

        if stock_codes:
            params["stockCodes"] = stock_codes

        response = client.query_api("hk/index", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_fundamental_non_financial(
        self,
        stock_codes: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        metrics_list: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company fundamental data (non-financial) from Lixinger.

        Args:
            stock_codes: List of stock codes (1-100 codes). e.g., ['00700']
            date: Specific date (YYYY-MM-DD). Must provide either date or start_date.
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return (for date range queries)
            metrics_list: List of metrics to query. e.g., ['mc', 'pe_ttm', 'pb', 'dyr']
                Supported metrics:
                - Valuation: pe_ttm, pb, ps_ttm, dyr, pcf_ttm, sp, spc, spa, tv, ta, to_r, mc, mc_om
                - AH data: ah_sh, ah_shm, mm_nba, sharesPerLot
                - Statistics: [metric].[granularity].[statType] e.g., 'pe_ttm.y3.cvpos'
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Fundamental data
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        if metrics_list:
            params["metricsList"] = metrics_list

        response = client.query_api("hk/company/fundamental/non_financial", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_candlestick(
        self,
        stock_code: str,
        type: str = "lxr_fc_rights",
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust_forward_date: str | None = None,
        adjust_backward_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company candlestick (K-line) data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            type: Adjustment type. Options:
                - 'ex_rights': No adjustment
                - 'lxr_fc_rights': Lixinger forward adjustment (default)
                - 'fc_rights': Forward adjustment
                - 'bc_rights': Backward adjustment
            date: Specific date (YYYY-MM-DD)
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            adjust_forward_date: Forward adjustment start date (with end_date)
            adjust_backward_date: Backward adjustment start date (with start_date)
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Candlestick data with columns:
                date, stockCode, open, close, high, low, volume, amount, change, to_r
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "type": type}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if adjust_forward_date:
            params["adjustForwardDate"] = adjust_forward_date

        if adjust_backward_date:
            params["adjustBackwardDate"] = adjust_backward_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/candlestick", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_dividend(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company dividend data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Dividend data with columns: date, content, bonusSharesFromProfit,
                bonusSharesFromCapitalReserve, dividend, currency, dividendAmount,
                annualNetProfit, annualNetProfitDividendRatio, registerDate, exDate, paymentDate, fsEndDate
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/dividend", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_repurchase(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company repurchase data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Repurchase data with columns: methodOfRepurchase, highestPrice,
                lowestPrice, avgPrice, num, totalPaid, numPurchasedInYearSinceResolution,
                ratioPurchasedSinceResolution
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/repurchase", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_profile(
        self,
        stock_codes: list[str],
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company profile data from Lixinger.

        Args:
            stock_codes: List of stock codes (1-100 codes). e.g., ['00700']
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Profile data with columns: stockCode, listingDate, chairman,
                classAdescription, classBdescription, capitalStructureClassA,
                capitalStructureClassB, fiscalYearEnd, summary, listingCategory,
                registrar, website, registeredAddress, officeAddress
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        response = client.query_api("hk/company/profile", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_employee(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company employee data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Employee data with nested dataList containing itemName,
                parentItemName, displayType, value
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/employee", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_split(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company split data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Split data with columns: date, exDate, content, splitRatio
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/split", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_candlestick(
        self,
        stock_code: str,
        type: str = "normal",
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index candlestick (K-line) data from Lixinger.

        Args:
            stock_code: Index code (e.g., 'HSI')
            type: Close price type. Options:
                - 'normal': Normal price level (default)
                - 'total_return': Total return price level
            date: Specific date (YYYY-MM-DD)
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Candlestick data with columns: date, open, close, high, low, volume, amount, change
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "type": type}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/index/candlestick", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_constituents(
        self,
        stock_codes: list[str],
        date: str = "latest",
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index constituents data from Lixinger.

        Args:
            stock_codes: List of index codes (1-100 codes). e.g., ['HSI']
            date: Date for constituents data. Use 'latest' for most recent data, or YYYY-MM-DD format.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Constituents data with columns: stockCode, constituents (nested array)
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes, "date": date}

        response = client.query_api("hk/index/constituents", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_fundamental(
        self,
        stock_codes: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        metrics_list: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index fundamental data from Lixinger.

        Args:
            stock_codes: List of index codes (1-100 codes). e.g., ['HSI']
            date: Specific date (YYYY-MM-DD). Must provide either date or start_date.
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return (for date range queries)
            metrics_list: List of metrics to query. e.g., ['mc', 'pe_ttm.mcw', 'pe_ttm.y10.mcw.cvpos']
                Supported metrics:
                - Valuation: pe_ttm, pb, ps_ttm, dyr
                - Volume/Amount: tv, ta, mc, mc_om
                - Price: cp, cpc, cpa
                - AH data: ah_shm, mm_nba, fet_as_ma, fet_snif_ma
                - Statistics: [metric].[granularity].[type].[statType]
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Fundamental data
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        if metrics_list:
            params["metricsList"] = metrics_list

        response = client.query_api("hk/index/fundamental", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_drawdown(
        self,
        stock_code: str,
        start_date: str,
        granularity: str,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index drawdown data from Lixinger.

        Args:
            stock_code: Index code (e.g., 'HSI')
            start_date: Start date (YYYY-MM-DD)
            granularity: Drawdown period. Options:
                - 'm': Monthly
                - 'q': Quarterly
                - 'hy': Half-year
                - 'y1': 1 year
                - 'y3': 3 years
                - 'y5': 5 years
                - 'y10': 10 years
                - 'fs': Since launch
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Drawdown data with columns: date, value
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date, "granularity": granularity}

        if end_date:
            params["endDate"] = end_date

        response = client.query_api("hk/index/drawdown", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_hot_mm_ah(
        self,
        stock_codes: list[str],
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index mutual market (AH) hot data from Lixinger.

        Args:
            stock_codes: List of index codes (1-100 codes). e.g., ['HSI']
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: AH hot data with columns: stockCode, last_data_date, cpc,
                mm_sha, mm_sha_mc_r, mm_sh_nba_d1/d5/d20/d60/d120/d240/ys,
                mm_sha_mc_rc_d1/d5/d20/d60/d120/d240/ys
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        response = client.query_api("hk/index/hot/mm_ah", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_fs_hybrid(
        self,
        stock_codes: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        metrics_list: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index financial statement data (hybrid) from Lixinger.

        Args:
            stock_codes: List of index codes (1-100 codes). e.g., ['HSI']
            date: Specific date (YYYY-MM-DD or 'latest'). Must provide either date or start_date.
                Use 'latest' for most recent data within 1.1 years.
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return (for date range queries)
            metrics_list: List of metrics in format [granularity].[tableName].[fieldName].[calcType]
                e.g., ['q.ps.toi.t', 'q.bs.ar.c_y2y']
                Granularity: y (year), hy (half-year), q (quarter)
                CalcType: t, t_o, t_y2y, t_c2c, c, c_o, c_y2y, c_c2c, ttm, ttm_o, ttm_y2y, ttm_c2c
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Financial statement data
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        if metrics_list:
            params["metricsList"] = metrics_list

        response = client.query_api("hk/index/fs/hybrid", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_tracking_fund(
        self,
        stock_code: str,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index tracking fund data from Lixinger.

        Args:
            stock_code: Index code (e.g., 'HSI')
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Tracking fund data with columns: name, stockCode, shortName,
                areaCode, market, exchange
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code}

        response = client.query_api("hk/index/tracking-fund", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_industry_info(
        self,
        stock_codes: list[str] | None = None,
        source: str = "hsi",
        level: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK industry information from Lixinger.

        Args:
            stock_codes: List of industry codes (e.g., ['H50', 'H5010']). None returns all.
            source: Industry source. Options: 'hsi' (Hang Seng)
            level: Classification level. Options: 'one', 'two', 'three'
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Industry info with columns: stockCode, name, launchDate,
                areaCode, market, fsTableType, level, source, currency
        """
        client = get_lixinger_client()

        params = {"source": source}

        if stock_codes:
            params["stockCodes"] = stock_codes

        if level:
            params["level"] = level

        response = client.query_api("hk/industry", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_industry_fundamental_hsi(
        self,
        stock_codes: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        metrics_list: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK industry fundamental data (HSI source) from Lixinger.

        Args:
            stock_codes: List of industry codes (1-100 codes). e.g., ['H50', 'H5010']
            date: Specific date (YYYY-MM-DD). Must provide either date or start_date.
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return (for date range queries)
            metrics_list: List of metrics. e.g., ['mc', 'pe_ttm.mcw', 'pe_ttm.y10.mcw.cvpos']
                Supported: pe_ttm, pb, ps_ttm, dyr, ta, to_r, mc, mc_om, ah_shm, mm_nba, launchDate
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Industry fundamental data
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        if metrics_list:
            params["metricsList"] = metrics_list

        response = client.query_api("hk/industry/fundamental/hsi", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_index_mutual_market(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK index mutual market data from Lixinger.

        Args:
            stock_code: Index code (e.g., 'HSI')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Mutual market data with columns: date, shareholdingsMoney, shareholdingsMoneyToMarketCap
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/index/mutual-market", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_industry_constituents_hsi(
        self,
        stock_codes: list[str] | None = None,
        date: str = "latest",
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK industry constituents data (HSI source) from Lixinger.

        Args:
            stock_codes: List of industry codes (1-100 codes). e.g., ['H50', 'H5010']. None returns all.
            date: Date for constituents data. Use 'latest' for most recent data, or YYYY-MM-DD format.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Constituents data with columns:
                stockCode, constituents (nested array with stockCode, areaCode, market)
        """
        client = get_lixinger_client()

        params = {"date": date}

        if stock_codes:
            params["stockCodes"] = stock_codes

        response = client.query_api("hk/industry/constituents/hsi", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_industry_fs_hsi_hybrid(
        self,
        stock_codes: list[str],
        metrics_list: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK industry financial statement data (HSI source, hybrid) from Lixinger.

        Args:
            stock_codes: List of industry codes (1-100 codes). e.g., ['H50', 'H5010']
                Note: When using startDate, only one stock code is allowed.
            metrics_list: List of metrics in format [granularity].[tableName].[fieldName].[calcType]
                e.g., ['q.ps.toi.t', 'q.bs.ar.c_y2y']
                Granularity: y (year), hy (half-year), q (quarter)
                CalcType varies by table:
                - Balance Sheet: t, t_o, t_y2y, t_c2c, c, c_o, c_y2y, c_c2c (hy/q)
                - Income Statement: t, t_o, t_y2y, t_c2c, c, c_o, c_y2y, c_c2c, c_2y,
                  ttm, ttm_o, ttm_y2y, ttm_c2c (hy/q)
                - Cash Flow Statement: t, t_o, t_y2y, t_c2c, c, c_o, c_y2y, c_c2c, c_2y,
                  ttm, ttm_o, ttm_y2y, ttm_c2c (hy/q)
                Max 48 metrics when stockCodes > 1, max 128 metrics when stockCodes == 1.
            date: Specific date (YYYY-MM-DD or 'latest'). Must provide either date or start_date.
                Use 'latest' for most recent data within 1.1 years.
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return (for date range queries)
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Financial statement data
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes, "metricsList": metrics_list}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/industry/fs/hsi/hybrid", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_industry_mutual_market_hsi(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK industry mutual market data (HSI source) from Lixinger.

        Args:
            stock_code: Industry code (e.g., 'H50')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Mutual market data with columns: date, shareholdingsMoney, shareholdingsMoneyToMarketCap
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/industry/mutual-market/hsi", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_us_index_hot_ifet_sni(
        self,
        stock_codes: list[str],
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US index in-field ETF subscription net inflow hot data from Lixinger.

        Args:
            stock_codes: List of index codes (1-100 codes). e.g., ['.INX']
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: In-field ETF subscription net inflow data with columns:
                stockCode, last_data_date, cpc, ifet_as, ifet_sni_ytd, ifet_sni_w1, ifet_sni_w2,
                ifet_ssni_m1, ifet_sni_m3, ifet_sni_m6, ifet_sni_y1, ifet_sni_y2, ifet_sni_fys
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        response = client.query_api("us/index/hot/ifet_sni", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK stock list (using company info API).

        This is a convenience method that wraps get_hk_company_info().

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: HK stocks information.
        """
        return self.get_hk_company_info(columns=columns, row_filter=row_filter)

    def get_us_index_info(
        self,
        stock_codes: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US index information from Lixinger.

        Args:
            stock_codes: List of index codes (e.g., ['.INX']). None returns all indices.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: US index information with columns: name, stockCode, areaCode,
                market, fsTableType, source, currency, series, launchDate,
                rebalancingFrequency, caculationMethod
        """
        client = get_lixinger_client()

        params = {}

        if stock_codes:
            params["stockCodes"] = stock_codes

        response = client.query_api("us/index", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_us_index_candlestick(
        self,
        stock_code: str,
        type: str = "normal",
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US index candlestick (K-line) data from Lixinger.

        Args:
            stock_code: Index code (e.g., '.INX')
            type: Close price type. Options:
                - 'normal': Normal price level (default)
                - 'total_return': Total return price level
            date: Specific date (YYYY-MM-DD)
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Candlestick data with columns: date, open, close, high, low, volume, amount, change
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "type": type}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("us/index/candlestick", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_us_index_constituents(
        self,
        stock_codes: list[str],
        date: str = "latest",
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US index constituents data from Lixinger.

        Args:
            stock_codes: List of index codes (1-100 codes). e.g., ['.INX']
            date: Date for constituents data. Use 'latest' for most recent data, or YYYY-MM-DD format.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Constituents data with columns: stockCode, constituents (nested array)
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes, "date": date}

        response = client.query_api("us/index/constituents", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_us_index_fundamental(
        self,
        stock_codes: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        metrics_list: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US index fundamental data from Lixinger.

        Args:
            stock_codes: List of index codes (1-100 codes). e.g., ['.INX']
            date: Specific date (YYYY-MM-DD). Must provide either date or start_date.
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return (for date range queries)
            metrics_list: List of metrics to query. e.g., ['mc', 'pe_ttm.ew', 'pe_ttm.y10.ew.cvpos']
                Supported metrics:
                - Valuation: pe_ttm, pb, ps_ttm, dyr
                - Volume/Price: tv, mc, cp, cpc, cpa
                - Fund data: fet_as_ma, fet_snif_ma
                - Statistics: [metric].[granularity].[type].[statType]
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Fundamental data
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        if metrics_list:
            params["metricsList"] = metrics_list

        response = client.query_api("us/index/fundamental", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_us_index_drawdown(
        self,
        stock_code: str,
        start_date: str,
        granularity: str,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US index drawdown data from Lixinger.

        Args:
            stock_code: Index code (e.g., '.INX')
            start_date: Start date (YYYY-MM-DD)
            granularity: Drawdown period. Options:
                - 'm': Monthly
                - 'q': Quarterly
                - 'hy': Half-year
                - 'y1': 1 year
                - 'y3': 3 years
                - 'y5': 5 years
                - 'y10': 10 years
                - 'fs': Since launch
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Drawdown data with columns: date, value
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date, "granularity": granularity}

        if end_date:
            params["endDate"] = end_date

        response = client.query_api("us/index/drawdown", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_us_index_hot_cp(
        self,
        stock_codes: list[str],
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US index close price hot data from Lixinger.

        Args:
            stock_codes: List of index codes (1-100 codes). e.g., ['.INX']
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Close price hot data with columns: stockCode, last_data_date, cpc,
                cpc_fys, cpc_w1, cpc_w2, cpc_m1, cpc_m3, cpc_m6, cpc_y1,
                cp_cac_y2, cp_cac_y3, cp_cac_y5, cp_cac_y10, cp_cac_fs
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        response = client.query_api("us/index/hot/cp", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_us_index_tracking_fund(
        self,
        stock_code: str,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US index tracking fund data from Lixinger.

        Args:
            stock_code: Index code (e.g., '.INX')
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Tracking fund data with columns: name, stockCode, shortName,
                areaCode, market, exchange
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code}

        response = client.query_api("us/index/tracking-fund", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_us_index_fs_non_financial(
        self,
        stock_codes: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        metrics_list: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US index financial statement data (non-financial) from Lixinger.

        Args:
            stock_codes: List of index codes (1-100 codes). e.g., ['.INX']
            date: Specific date (YYYY-MM-DD or 'latest'). Must provide either date or start_date.
                Use 'latest' for most recent data within 1.1 years.
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return (for date range queries)
            metrics_list: List of metrics in format [granularity].[tableName].[fieldName].[calcType]
                e.g., ['q.ps.toi.t', 'q.bs.ar.c_y2y']
                Granularity: y (year), hy (half-year), q (quarter)
                CalcType: t, t_o, t_y2y, t_c2c, c, c_o, c_y2y, c_c2c, ttm, ttm_o, ttm_y2y, ttm_c2c
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Financial statement data
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        if metrics_list:
            params["metricsList"] = metrics_list

        response = client.query_api("us/index/fs/non_financial", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_us_stocks(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get US stock list.

        Note: Lixinger does not provide US stock API, returns empty DataFrame.

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Empty DataFrame (not supported).
        """
        self.logger.warning(
            "Lixinger does not provide US stock data",
            extra={
                "context": {
                    "log_type": "unsupported_api",
                    "provider": "lixinger",
                    "api": "us_stocks",
                }
            },
        )
        return pd.DataFrame()

    def get_hk_company_allotment(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company allotment data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Allotment data with columns: date, exDate, currency,
                allotmentRatio, allotmentPrice, allotmentShares
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/allotment", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_announcement(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company announcement data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Announcement data with columns: date, linkText, linkUrl, linkType, types
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/announcement", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_equity_change(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company equity change data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Equity change data with columns: date, capitalization, capitalizationH
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/equity-change", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_fs_non_financial(
        self,
        stock_codes: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        metrics_list: list[str] | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company financial statement data (non-financial) from Lixinger.

        Args:
            stock_codes: List of stock codes (1-100 codes). e.g., ['00700']
                Note: When startDate is provided, only one stock code is allowed.
            date: Specific date (YYYY-MM-DD or 'latest'). Must provide either date or start_date.
                Use 'latest' for most recent data within 1.1 years.
                Valid dates: 2017-03-31, 2017-06-30, 2017-09-30, 2017-12-31, etc.
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return (for date range queries)
            metrics_list: List of metrics in format [granularity].[tableName].[fieldName].[calcType]
                e.g., ['q.ps.toi.t', 'q.bs.ar.c_y2y']
                Granularity: y (year), hy (half-year), q (quarter)
                CalcType: t, t_o, t_y2y, t_c2c, c, c_o, c_y2y, c_c2c, ttm, ttm_o, ttm_y2y, ttm_c2c, c_2y
                Max 48 metrics when stockCodes > 1, max 128 metrics when stockCodes = 1
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Financial statement data with columns: date, reportDate, standardDate,
                stockCode, reportType, currency, auditOpinionType, and requested metrics
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        if metrics_list:
            params["metricsList"] = metrics_list

        response = client.query_api("hk/company/fs/non_financial", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_fund_collection_shareholders(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company fund collection shareholders data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Fund collection shareholders data with columns: date, marketCap,
                name, holdings, fundCollectionCode
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/fund-collection-shareholders", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_hot_tr_dri(
        self,
        stock_codes: list[str],
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company total return with dividend reinvestment data from Lixinger.

        Args:
            stock_codes: List of stock codes (1-100 codes). e.g., ['00700']
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Total return data with columns: stockCode, last_data_date, p_r,
                cagr_p_r_fys, cagr_p_r_d7, cagr_p_r_d14, cagr_p_r_d30, cagr_p_r_d60,
                cagr_p_r_d90, cagr_p_r_y1, cagr_p_r_y3, cagr_p_r_y5, cagr_p_r_y10,
                cagr_p_r_fs, period_date
        """
        client = get_lixinger_client()

        params = {"stockCodes": stock_codes}

        response = client.query_api("hk/company/hot/tr_dri", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_indices(
        self,
        stock_code: str,
        date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company indices information from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            date: Date (YYYY-MM-DD). Default is current latest time.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Indices data with columns: name, areaCode, stockCode, source
                Source values: csi (中证), cni (国证), hsi (恒生), usi (美指), lxri (理杏仁)
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code}

        if date:
            params["date"] = date

        response = client.query_api("hk/company/indices", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_industries(
        self,
        stock_code: str,
        date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company industries information from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            date: Date (YYYY-MM-DD). Default is current latest time.
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Industries data with columns: name, areaCode, stockCode, source
                Source values: sw (申万), sw_2021 (申万2021版), cni (国证)
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code}

        if date:
            params["date"] = date

        response = client.query_api("hk/company/industries", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_latest_shareholders(
        self,
        stock_code: str,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company latest shareholders data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Latest shareholders data with columns: date, name,
                numOfSharesInterestedList (nested array with value, sharesType),
                percentageOfIssuedVotingShares (nested array with value, sharesType)
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code}

        response = client.query_api("hk/company/latest-shareholders", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_operation_revenue_constitution(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company operation revenue constitution data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Operation revenue constitution data with columns: date,
                declarationDate, currency, dataList (nested array with itemName,
                parentItemName, revenue, costs, grossProfitMargin)
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/operation-revenue-constitution", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_shareholders_equity_change(
        self,
        stock_code: str | None = None,
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company shareholders equity change data from Lixinger.

        Args:
            stock_code: Stock code (e.g., '00700'). Only valid for date range queries.
            date: Specific date (YYYY-MM-DD)
            start_date: Start date for date range (YYYY-MM-DD)
            end_date: End date for date range (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Shareholders equity change data with columns: date, name,
                numOfSharesInvolvedList (nested array with value, sharesType),
                numOfSharesInterestedList (nested array with value, sharesType),
                percentageOfIssuedVotingShares (nested array with value, sharesType)
        """
        client = get_lixinger_client()

        params = {}

        if stock_code:
            params["stockCode"] = stock_code

        if date:
            params["date"] = date
        elif start_date:
            params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/shareholders-equity-change", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)

    def get_hk_company_short_selling(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        limit: int | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get HK company short selling data from Lixinger.

        Note: Calculation uses total H shares as share capital.

        Args:
            stock_code: Stock code (e.g., '00700')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Default is last Monday.
            limit: Number of recent records to return
            columns: Optional column filter
            row_filter: Optional row filter

        Returns:
            pd.DataFrame: Short selling data with columns: date, shares, shareMoney
        """
        client = get_lixinger_client()

        params = {"stockCode": stock_code, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if limit:
            params["limit"] = limit

        response = client.query_api("hk/company/short-selling", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(df, source="lixinger", columns=columns, row_filter=row_filter)
