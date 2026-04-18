"""
Baostock financial data provider.

This module provides financial data from Baostock API.
"""

import time
import warnings

import pandas as pd

from ......logging_config import get_logger, log_api_request
from ......metrics.stats import get_stats_collector
from .....core.cache import cache
from .base import FinancialDataFactory, FinancialDataProvider

warnings.filterwarnings("ignore", message=".*lzma.*")


@FinancialDataFactory.register("baostock")
class BaostockFinancialProvider(FinancialDataProvider):
    """Financial data provider for Baostock."""

    _bs_instance = None
    _is_logged_in = False

    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(symbol, **kwargs)
        self.logger = get_logger(__name__)
        self._ensure_login()
        self._convert_symbol_to_baostock_format()

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
                raise ImportError("baostock is not installed. Install it with: pip install baostock") from None

    @classmethod
    def logout(cls):
        """Logout from baostock"""
        if cls._is_logged_in and cls._bs_instance:
            cls._bs_instance.logout()
            cls._is_logged_in = False

    def get_source_name(self) -> str:
        return "baostock"

    def _convert_symbol_to_baostock_format(self) -> None:
        """Convert symbol format to baostock format (sh.600000 or sz.000001)"""
        symbol = self.symbol
        if symbol.startswith(("sh.", "sz.", "bj.")):
            self.bs_code = symbol
        elif len(symbol) == 6:
            if symbol.startswith(("6", "9")):
                self.bs_code = f"sh.{symbol}"
            elif symbol.startswith(("0", "3", "2")):
                self.bs_code = f"sz.{symbol}"
            else:
                self.bs_code = f"sh.{symbol}"
        else:
            raise ValueError(f"Invalid symbol format: {symbol}")

    def _fetch_baostock_data(
        self,
        query_method,
        data_name: str,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Generic method to fetch financial data from Baostock.

        Args:
            query_method: Baostock query method to call
            data_name: Name of the data for logging
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules
            **kwargs: Additional parameters (year, quarter)

        Returns:
            DataFrame with financial data
        """
        start_time = time.time()

        try:
            year = kwargs.get("year")
            quarter = kwargs.get("quarter")

            self.logger.debug(
                f"Fetching {data_name}",
                extra={
                    "context": {
                        "source": "baostock",
                        "symbol": self.symbol,
                        "year": year,
                        "quarter": quarter,
                        "action": "fetch_start",
                    }
                },
            )

            rs = query_method(code=self.bs_code, year=year, quarter=quarter)

            if rs.error_code != "0":
                raise ValueError(f"Baostock query failed: {rs.error_msg}")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return pd.DataFrame()

            raw_df = pd.DataFrame(data_list, columns=rs.fields)
            df = self._process_financial_data(raw_df)
            df = self.apply_data_filter(df, columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            stats_collector = get_stats_collector()
            stats_collector.record_request("baostock", duration_ms, True)

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint=data_name,
                params={"symbol": self.symbol, "year": year, "quarter": quarter},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return df
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            stats_collector = get_stats_collector()
            stats_collector.record_request("baostock", duration_ms, False)

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint=data_name,
                params={"symbol": self.symbol},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )
            raise ValueError(f"Failed to fetch {data_name}: {str(e)}") from e

    @cache(
        "financial_cache",
        key=lambda self,
        columns=None,
        row_filter=None,
        **kwargs: f"baostock_profit_{self.symbol}_{kwargs.get('year')}_{kwargs.get('quarter')}",
    )
    def get_profit_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Get profit data (盈利能力) from Baostock.

        Args:
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules
            **kwargs: Additional parameters (year, quarter)

        Returns:
            DataFrame with profit data
        """
        return self._fetch_baostock_data(
            query_method=self._bs_instance.query_profit_data,
            data_name="profit_data",
            columns=columns,
            row_filter=row_filter,
            **kwargs,
        )

    @cache(
        "financial_cache",
        key=lambda self,
        columns=None,
        row_filter=None,
        **kwargs: f"baostock_operation_{self.symbol}_{kwargs.get('year')}_{kwargs.get('quarter')}",
    )
    def get_operation_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Get operation data (营运能力) from Baostock.

        Args:
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules
            **kwargs: Additional parameters (year, quarter)

        Returns:
            DataFrame with operation data
        """
        return self._fetch_baostock_data(
            query_method=self._bs_instance.query_operation_data,
            data_name="operation_data",
            columns=columns,
            row_filter=row_filter,
            **kwargs,
        )

    @cache(
        "financial_cache",
        key=lambda self,
        columns=None,
        row_filter=None,
        **kwargs: f"baostock_growth_{self.symbol}_{kwargs.get('year')}_{kwargs.get('quarter')}",
    )
    def get_growth_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Get growth data (成长能力) from Baostock.

        Args:
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules
            **kwargs: Additional parameters (year, quarter)

        Returns:
            DataFrame with growth data
        """
        return self._fetch_baostock_data(
            query_method=self._bs_instance.query_growth_data,
            data_name="growth_data",
            columns=columns,
            row_filter=row_filter,
            **kwargs,
        )

    @cache(
        "financial_cache",
        key=lambda self,
        columns=None,
        row_filter=None,
        **kwargs: f"baostock_balance_{self.symbol}_{kwargs.get('year')}_{kwargs.get('quarter')}",
    )
    def get_balance_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Get balance data (偿债能力) from Baostock.

        Args:
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules
            **kwargs: Additional parameters (year, quarter)

        Returns:
            DataFrame with balance data
        """
        return self._fetch_baostock_data(
            query_method=self._bs_instance.query_balance_data,
            data_name="balance_data",
            columns=columns,
            row_filter=row_filter,
            **kwargs,
        )

    @cache(
        "financial_cache",
        key=lambda self,
        columns=None,
        row_filter=None,
        **kwargs: f"baostock_cashflow_{self.symbol}_{kwargs.get('year')}_{kwargs.get('quarter')}",
    )
    def get_cash_flow_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Get cash flow data (现金流量) from Baostock.

        Args:
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules
            **kwargs: Additional parameters (year, quarter)

        Returns:
            DataFrame with cash flow data
        """
        return self._fetch_baostock_data(
            query_method=self._bs_instance.query_cash_flow_data,
            data_name="cash_flow_data",
            columns=columns,
            row_filter=row_filter,
            **kwargs,
        )

    @cache(
        "financial_cache",
        key=lambda self,
        columns=None,
        row_filter=None,
        **kwargs: f"baostock_dupont_{self.symbol}_{kwargs.get('year')}_{kwargs.get('quarter')}",
    )
    def get_dupont_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Get dupont data (杜邦指数) from Baostock.

        Args:
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules
            **kwargs: Additional parameters (year, quarter)

        Returns:
            DataFrame with dupont data
        """
        return self._fetch_baostock_data(
            query_method=self._bs_instance.query_dupont_data,
            data_name="dupont_data",
            columns=columns,
            row_filter=row_filter,
            **kwargs,
        )

    def _process_financial_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize financial data."""
        df = self.map_source_fields(raw_df, "baostock")

        if "pubDate" in df.columns:
            df["pub_date"] = pd.to_datetime(df["pubDate"], errors="coerce")
        if "statDate" in df.columns:
            df["stat_date"] = pd.to_datetime(df["statDate"], errors="coerce")
            df["date"] = df["stat_date"]

        return df
