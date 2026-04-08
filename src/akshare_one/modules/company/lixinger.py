"""
Lixinger provider for company data.

This module implements company data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ...lixinger_client import get_lixinger_client
from .base import CompanyFactory, CompanyProvider


@CompanyFactory.register("lixinger")
class LixingerCompanyProvider(CompanyProvider):
    """
    Company data provider using Lixinger OpenAPI.

    Provides company profile, indices, industries, mutual market data.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_company_profile(self, symbols: list[str] | str, **kwargs) -> pd.DataFrame:
        """
        Get company profile data from Lixinger.

        Args:
            symbols: Stock symbols (list or single symbol, e.g., '600000' or ['600000', '600519'])
                     Maximum 100 symbols per request.

        Returns:
            pd.DataFrame: Company profile data with columns:
                - stock_code: Stock code
                - company_name: Company name
                - province: Province
                - city: City
                - actual_controller_types: Actual controller types
                - actual_controller_name: Actual controller name
                - history_stock_names: Historical names
        """
        client = get_lixinger_client()

        stock_codes = [symbols] if isinstance(symbols, str) else symbols

        params = {"stockCodes": stock_codes}

        response = client.query_api("cn/company/profile", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_indices(self, symbol: str, date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get indices that a stock belongs to from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            date: Optional date (YYYY-MM-DD format). Default is latest.

        Returns:
            pd.DataFrame: Indices data with columns:
                - name: Index name
                - stock_code: Index code
                - area_code: Area code
                - source: Index source (csi/cni/hsi/usi/lxri)
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol}

        if date:
            params["date"] = date

        response = client.query_api("cn/company/indices", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_industries(self, symbol: str, date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get industries that a stock belongs to from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            date: Optional date (YYYY-MM-DD format). Default is latest.

        Returns:
            pd.DataFrame: Industries data with columns:
                - name: Industry name
                - stock_code: Industry code
                - area_code: Area code
                - source: Industry source (sw/sw_2021/cni)
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol}

        if date:
            params["date"] = date

        response = client.query_api("cn/company/industries", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_mutual_market(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get mutual market (陆股通/互联互通) data for a stock from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.
                     Note: Time range cannot exceed 10 years.

        Returns:
            pd.DataFrame: Mutual market data with columns:
                - date: Data date
                - shareholdings: Holding quantity
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/mutual-market", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_fundamental_financial(
        self,
        symbols: list[str] | str,
        metrics: list[str],
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Get fundamental data for financial companies from Lixinger.

        Args:
            symbols: Stock symbols (list or single symbol)
                     Note: When start_date is provided, only one symbol is allowed.
                     Maximum 100 symbols, maximum 48 metrics when multiple symbols.
            metrics: List of metrics to fetch (e.g., ['pe_ttm', 'pb', 'mc'])
                     Supported metrics include:
                     - pe_ttm: PE-TTM
                     - pb: PB
                     - pb_wo_gw: PB without goodwill
                     - ps_ttm: PS-TTM
                     - dyr: Dividend yield ratio
                     - mc: Market cap
                     - cmc: Circulating market cap
                     - sp: Stock price
                     - spc: Price change percentage
                     - tv: Trading volume
                     - ta: Trading amount
                     - to_r: Turnover rate
                     - And many more valuation and statistical metrics
            date: Optional specific date (YYYY-MM-DD). Either date or start_date is required.
            start_date: Optional start date (YYYY-MM-DD). Used for date range queries.
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.
                     Note: Time range cannot exceed 10 years.

        Returns:
            pd.DataFrame: Fundamental data with requested metrics
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

        response = client.query_api("cn/company/fundamental/financial", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_allotment(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get allotment (配股) data from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Allotment data with columns:
                - date: Announcement date
                - exDate: Ex-rights date
                - currency: Currency
                - allotmentRatio: Allotment ratio
                - allotmentPrice: Allotment price
                - allotmentShares: Actual allotment shares
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/allotment", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_split(self, symbol: str, start_date: str, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get split (拆分) data from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Split data with columns:
                - date: Announcement date
                - exDate: Ex-rights date
                - content: Content
                - splitRatio: Split ratio
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/split", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_customers(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get customers (客户) data from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Customers data with columns:
                - date: Data date
                - declarationDate: Declaration date
                - dataList: List of customer details (ratio, tradeAmount, trader)
                - top5Customer: Top 5 customer data
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/customers", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_suppliers(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get suppliers (供应商) data from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Suppliers data with columns:
                - date: Data date
                - declarationDate: Declaration date
                - dataList: List of supplier details (ratio, tradeAmount, trader)
                - top5Supplier: Top 5 supplier data
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/suppliers", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_equity_change(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get equity change (股本变动) data from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Equity change data with columns:
                - date: Change date
                - declarationDate: Declaration date
                - changeReason: Change reason
                - capitalization: Total capital
                - outstandingSharesA: Outstanding A shares
                - limitedSharesA: Limited A shares
                - outstandingSharesH: Outstanding H shares
                - capitalizationChangeRatio: Total capital change ratio
                - outstandingSharesAChangeRatio: Outstanding A shares change ratio
                - limitedSharesAChangeRatio: Limited A shares change ratio
                - outstandingSharesHChangeRatio: Outstanding H shares change ratio
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/equity-change", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_operating_data(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get operating data (经营数据) from Lixinger.

        Args:
            symbol: Stock code (e.g., '600157')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Operating data with columns:
                - date: Data date
                - declarationDate: Declaration date
                - startDate: Start date
                - dataList: List of operating data items (itemName, parentItemName, unitText, value)
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/operating-data", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_operation_revenue_constitution(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get operation revenue constitution (营业收入构成) data from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Operation revenue constitution data with columns:
                - date: Data date
                - declarationDate: Declaration date
                - dataList: List of revenue constitution data
                  (classifyType, itemName, parentItemName, revenue, revenuePercentage,
                   costs, costPercentage, grossProfitMargin)
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/operation-revenue-constitution", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_fund_collection_shareholders(
        self, symbol: str, start_date: str, end_date: str | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get fund collection shareholders (基金持仓股东) data from Lixinger.

        Args:
            symbol: Stock code (e.g., '300750')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Fund collection shareholders data with columns:
                - date: Data date
                - fundCode: Fund code
                - name: Fund name
                - holdings: Holdings
                - marketCap: Market cap
                - marketCapRank: Market cap rank of the stock in the fund
                - netValueRatio: Fund holdings ratio
                - outstandingSharesA: Outstanding A shares
                - proportionOfCapitalization: Outstanding A shares proportion
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/fund-shareholders", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_hot_tr_dri(self, symbols: list[str] | str, **kwargs) -> pd.DataFrame:
        """
        Get hot TR DRI (热门股票分红再投入收益率) data from Lixinger.

        Args:
            symbols: Stock codes (list or single symbol, e.g., '300750' or ['300750', '600519'])
                     Maximum 100 symbols per request.

        Returns:
            pd.DataFrame: Hot TR DRI data with columns:
                - stockCode: Stock code
                - last_data_date: Last data date
                - p_r: Investment return rate for specified period
                - cagr_p_r_fys: Year-to-date investment return rate
                - cagr_p_r_d7: 7-day investment return rate
                - cagr_p_r_d14: 14-day investment return rate
                - cagr_p_r_d30: 30-day investment return rate
                - cagr_p_r_d60: 60-day investment return rate
                - cagr_p_r_d90: 90-day investment return rate
                - cagr_p_r_y1: 1-year investment return rate
                - cagr_p_r_y3: 3-year annualized investment return rate
                - cagr_p_r_y5: 5-year annualized investment return rate
                - cagr_p_r_y10: 10-year annualized investment return rate
                - cagr_p_r_y20: 20-year annualized investment return rate
                - cagr_p_r_fs: Since IPO annualized investment return rate
                - p_r_fs: Since IPO total investment return rate
                - period_date: Investment return rate calculation start date
        """
        client = get_lixinger_client()

        stock_codes = [symbols] if isinstance(symbols, str) else symbols

        params = {"stockCodes": stock_codes}

        response = client.query_api("cn/company/hot/tr_dri", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_inquiry(self, symbol: str, start_date: str, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get inquiry (问询函) data from Lixinger.

        Args:
            symbol: Stock code (e.g., '600866')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Inquiry data with columns:
                - date: Announcement date
                - type: Type (il: inquiry letter, olo_prpa: periodic report audit opinion letter,
                        olo_romarp: major asset restructuring plan audit opinion letter)
                - displayTypeText: Display type text
                - linkText: Link text
                - linkUrl: Link URL
                - linkType: Link type
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/inquiry", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_company_measures(self, symbol: str, start_date: str, end_date: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Get measures (监管措施) data from Lixinger.

        Args:
            symbol: Stock code (e.g., '600866')
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD). Default is last Monday.

        Returns:
            pd.DataFrame: Measures data with columns:
                - date: Announcement date
                - type: Type (sw: regulatory warning, bc: notice of criticism,
                        pcar: public condemnation and determination, sl: regulatory work letter)
                - displayTypeText: Display type text
                - linkText: Link text
                - linkUrl: Link URL
                - linkType: Link type
                - referent: Object
        """
        client = get_lixinger_client()

        params = {"stockCode": symbol, "startDate": start_date}

        if end_date:
            params["endDate"] = end_date

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        response = client.query_api("cn/company/measures", params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )
