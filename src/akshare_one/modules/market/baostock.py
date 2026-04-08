"""
Baostock provider for market infrastructure data.

This module implements instrument data providers using Baostock API.
"""

import time

import pandas as pd

from ...logging_config import get_logger, log_api_request
from .base import InstrumentFactory, InstrumentProvider


@InstrumentFactory.register("baostock")
class BaostockInstrumentProvider(InstrumentProvider):
    """
    Instrument metadata provider using Baostock API.

    Provides metadata for stocks including basic info, industry classification, and index constituents.
    """

    _bs_instance = None
    _is_logged_in = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)
        self._ensure_login()

    @classmethod
    def _ensure_login(cls):
        """Ensure baostock is logged in"""
        if not cls._is_logged_in:
            try:
                import baostock as bs

                cls._bs_instance = bs
                lg = bs.login()
                if lg.error_code == "0":
                    cls._is_logged_in = True
                else:
                    raise ConnectionError(f"Baostock login failed: {lg.error_msg}")
            except ImportError:
                raise ImportError("baostock is not installed. Install it with: pip install baostock")

    @classmethod
    def logout(cls):
        """Logout from baostock"""
        if cls._is_logged_in and cls._bs_instance:
            cls._bs_instance.logout()
            cls._is_logged_in = False

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "baostock"

    def get_instruments(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get instrument metadata from Baostock.

        This method returns all stocks by default.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Instrument metadata with columns:
                - symbol: Stock code (6 digits)
                - name: Stock name
                - exchange: Exchange code (SH/SZ)
                - status: Trading status
                - listing_date: Listing date
                - delisting_date: Delisting date
        """
        return self.query_all_stock(columns=columns, row_filter=row_filter)

    def query_all_stock(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get all stock list from Baostock.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters
                - date: Query date (YYYY-MM-DD format, optional)

        Returns:
            pd.DataFrame: All stocks with columns:
                - symbol: Stock code (6 digits)
                - name: Stock name
                - exchange: Exchange code (SH/SZ)
                - status: Trading status
                - listing_date: Listing date
                - delisting_date: Delisting date
        """
        start_time = time.time()

        try:
            date = kwargs.get("date", None)

            self.logger.debug(
                "Fetching all stock list",
                extra={
                    "context": {
                        "source": "baostock",
                        "date": date,
                        "action": "fetch_start",
                    }
                },
            )

            rs = self._bs_instance.query_all_stock(day=date)

            if rs.error_code != "0":
                raise ValueError(f"Baostock query_all_stock failed: {rs.error_msg}")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return pd.DataFrame()

            raw_df = pd.DataFrame(data_list, columns=rs.fields)

            df = self._standardize_all_stock(raw_df)

            df = self.standardize_and_filter(df, source="baostock", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="query_all_stock",
                params={"date": date},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return df

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="query_all_stock",
                params={"date": kwargs.get("date")},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch all stock list: {str(e)}") from e

    def query_stock_basic(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get stock basic information from Baostock.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters
                - code: Stock code (e.g., "sh.600000")

        Returns:
            pd.DataFrame: Stock basic info with columns:
                - symbol: Stock code (6 digits)
                - name: Stock name
                - exchange: Exchange code (SH/SZ)
                - status: Trading status
                - listing_date: Listing date
                - type: Stock type (1: A-share, etc.)
                - total_share: Total shares
                - float_share: Float shares
        """
        start_time = time.time()

        try:
            code = kwargs.get("code", None)

            if not code:
                return pd.DataFrame()

            self.logger.debug(
                "Fetching stock basic info",
                extra={
                    "context": {
                        "source": "baostock",
                        "code": code,
                        "action": "fetch_start",
                    }
                },
            )

            rs = self._bs_instance.query_stock_basic(code=code)

            if rs.error_code != "0":
                raise ValueError(f"Baostock query_stock_basic failed: {rs.error_msg}")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return pd.DataFrame()

            raw_df = pd.DataFrame(data_list, columns=rs.fields)

            df = self._standardize_stock_basic(raw_df)

            df = self.standardize_and_filter(df, source="baostock", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="query_stock_basic",
                params={"code": code},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return df

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="query_stock_basic",
                params={"code": kwargs.get("code")},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch stock basic info: {str(e)}") from e

    def query_stock_industry(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Get stock industry classification from Baostock.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters
                - code: Stock code (e.g., "sh.600000", optional)
                - date: Query date (YYYY-MM-DD format, optional)

        Returns:
            pd.DataFrame: Industry classification with columns:
                - symbol: Stock code (6 digits)
                - name: Stock name
                - industry: Industry classification
                - industry_code: Industry code
        """
        start_time = time.time()

        try:
            code = kwargs.get("code", None)
            date = kwargs.get("date", None)

            self.logger.debug(
                "Fetching stock industry classification",
                extra={
                    "context": {
                        "source": "baostock",
                        "code": code,
                        "date": date,
                        "action": "fetch_start",
                    }
                },
            )

            rs = self._bs_instance.query_stock_industry(code=code, day=date)

            if rs.error_code != "0":
                raise ValueError(f"Baostock query_stock_industry failed: {rs.error_msg}")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return pd.DataFrame()

            raw_df = pd.DataFrame(data_list, columns=rs.fields)

            df = self._standardize_stock_industry(raw_df)

            df = self.standardize_and_filter(df, source="baostock", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="query_stock_industry",
                params={"code": code, "date": date},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return df

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="query_stock_industry",
                params={"code": kwargs.get("code"), "date": kwargs.get("date")},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch stock industry classification: {str(e)}") from e

    def query_hs300_stocks(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get HS300 index constituent stocks from Baostock.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters
                - date: Query date (YYYY-MM-DD format, optional)

        Returns:
            pd.DataFrame: HS300 constituents with columns:
                - symbol: Stock code (6 digits)
                - name: Stock name
                - exchange: Exchange code (SH/SZ)
                - in_date: Inclusion date
                - out_date: Exclusion date
        """
        return self._query_index_constituents("hs300", columns=columns, row_filter=row_filter, **kwargs)

    def query_sz50_stocks(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get SZ50 index constituent stocks from Baostock.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters
                - date: Query date (YYYY-MM-DD format, optional)

        Returns:
            pd.DataFrame: SZ50 constituents with columns:
                - symbol: Stock code (6 digits)
                - name: Stock name
                - exchange: Exchange code (SH/SZ)
                - in_date: Inclusion date
                - out_date: Exclusion date
        """
        return self._query_index_constituents("sz50", columns=columns, row_filter=row_filter, **kwargs)

    def query_zz500_stocks(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """
        Get ZZ500 index constituent stocks from Baostock.

        Args:
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters
                - date: Query date (YYYY-MM-DD format, optional)

        Returns:
            pd.DataFrame: ZZ500 constituents with columns:
                - symbol: Stock code (6 digits)
                - name: Stock name
                - exchange: Exchange code (SH/SZ)
                - in_date: Inclusion date
                - out_date: Exclusion date
        """
        return self._query_index_constituents("zz500", columns=columns, row_filter=row_filter, **kwargs)

    def _query_index_constituents(
        self, index_code: str, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """
        Internal method to query index constituent stocks.

        Args:
            index_code: Index code (hs300, sz50, zz500)
            columns: Columns to return
            row_filter: Row filter
            **kwargs: Additional parameters
                - date: Query date (YYYY-MM-DD format, optional)

        Returns:
            pd.DataFrame: Index constituents
        """
        start_time = time.time()

        try:
            date = kwargs.get("date", None)

            self.logger.debug(
                f"Fetching {index_code} index constituents",
                extra={
                    "context": {
                        "source": "baostock",
                        "index_code": index_code,
                        "date": date,
                        "action": "fetch_start",
                    }
                },
            )

            index_name_map = {
                "hs300": "沪深300",
                "sz50": "上证50",
                "zz500": "中证500",
            }

            rs = (
                self._bs_instance.query_hs300_stocks()
                if index_code == "hs300"
                else (
                    self._bs_instance.query_sz50_stocks()
                    if index_code == "sz50"
                    else self._bs_instance.query_zz500_stocks()
                )
            )

            if rs.error_code != "0":
                raise ValueError(f"Baostock query_{index_code}_stocks failed: {rs.error_msg}")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return pd.DataFrame()

            raw_df = pd.DataFrame(data_list, columns=rs.fields)

            df = self._standardize_index_constituents(raw_df, index_name_map.get(index_code, index_code))

            df = self.standardize_and_filter(df, source="baostock", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint=f"query_{index_code}_stocks",
                params={"date": date},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return df

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint=f"query_{index_code}_stocks",
                params={"date": kwargs.get("date")},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch {index_code} index constituents: {str(e)}") from e

    def _standardize_all_stock(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Standardize all stock data"""
        column_map = {
            "code": "symbol",
            "code_name": "name",
            "tradeStatus": "status",
            "ipoDate": "listing_date",
            "outDate": "delisting_date",
            "type": "type",
        }

        df = raw_df.rename(columns=column_map)

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].apply(self._extract_symbol_code)
            df["exchange"] = df["symbol"].apply(self._get_exchange_from_symbol)

        if "listing_date" in df.columns:
            df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce")

        if "delisting_date" in df.columns:
            df["delisting_date"] = pd.to_datetime(df["delisting_date"], errors="coerce")

        return df

    def _standardize_stock_basic(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Standardize stock basic info data"""
        column_map = {
            "code": "symbol",
            "code_name": "name",
            "tradeStatus": "status",
            "ipoDate": "listing_date",
            "type": "type",
            "totalShare": "total_share",
            "floatShare": "float_share",
        }

        df = raw_df.rename(columns=column_map)

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].apply(self._extract_symbol_code)
            df["exchange"] = df["symbol"].apply(self._get_exchange_from_symbol)

        if "listing_date" in df.columns:
            df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce")

        for col in ["total_share", "float_share"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def _standardize_stock_industry(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Standardize stock industry classification data"""
        column_map = {
            "code": "symbol",
            "code_name": "name",
            "industry": "industry",
            "industryCode": "industry_code",
        }

        df = raw_df.rename(columns=column_map)

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].apply(self._extract_symbol_code)

        return df

    def _standardize_index_constituents(self, raw_df: pd.DataFrame, index_name: str) -> pd.DataFrame:
        """Standardize index constituent data"""
        column_map = {
            "code": "symbol",
            "code_name": "name",
            "inDate": "in_date",
            "outDate": "out_date",
            "updateDate": "update_timestamp",
        }

        df = raw_df.rename(columns=column_map)

        if "update_timestamp" in df.columns:
            df.drop(columns=["update_timestamp"], inplace=True)

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].apply(self._extract_symbol_code)
            df["exchange"] = df["symbol"].apply(self._get_exchange_from_symbol)

        df["index_name"] = index_name

        for col in ["in_date", "out_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        return df

    def _extract_symbol_code(self, full_code: str) -> str:
        """
        Extract symbol code from full code (sh.600000 -> 600000)

        Args:
            full_code: Full code in baostock format (e.g., "sh.600000")

        Returns:
            str: 6-digit symbol code
        """
        if "." in str(full_code):
            return str(full_code).split(".")[1]
        return str(full_code)

    def _get_exchange_from_symbol(self, symbol: str) -> str:
        """
        Get exchange code from symbol.

        Args:
            symbol: Stock symbol (6 digits)

        Returns:
            str: Exchange code (SH/SZ)
        """
        if not symbol:
            return ""

        symbol_str = str(symbol)
        if symbol_str.startswith(("6", "9")):
            return "SH"
        elif symbol_str.startswith(("0", "3", "2")):
            return "SZ"
        return ""
