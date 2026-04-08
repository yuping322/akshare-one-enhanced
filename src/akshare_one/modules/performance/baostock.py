"""
Baostock performance data provider.
"""

import time
import warnings

import pandas as pd

from ...logging_config import get_logger, log_api_request
from ..cache import cache
from .base import PerformanceFactory, PerformanceProvider

warnings.filterwarnings("ignore", message=".*lzma.*")


@PerformanceFactory.register("baostock")
class BaostockPerformanceProvider(PerformanceProvider):
    """Baostock performance forecast and express report data provider"""

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
                raise ImportError("baostock is not installed. Install it with: pip install baostock") from None

    @classmethod
    def logout(cls):
        """Logout from baostock"""
        if cls._is_logged_in and cls._bs_instance:
            cls._bs_instance.logout()
            cls._is_logged_in = False

    def get_source_name(self) -> str:
        return "baostock"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def _convert_symbol_to_baostock_format(self, symbol: str) -> str:
        """Convert symbol format to baostock format (sh.600000 or sz.000001)"""
        if symbol.startswith(("sh.", "sz.", "bj.")):
            return symbol

        if len(symbol) != 6:
            raise ValueError(f"Invalid symbol format: {symbol}")

        if symbol.startswith(("6", "9")):
            return f"sh.{symbol}"
        elif symbol.startswith(("0", "3", "2")):
            return f"sz.{symbol}"
        else:
            raise ValueError(f"Unknown market for symbol: {symbol}")

    def _validate_params(self, symbol: str, start_date: str, end_date: str):
        """Validate input parameters"""
        if not symbol:
            raise ValueError("symbol is required for Baostock performance API")

        self.validate_date(start_date, "start_date")
        self.validate_date(end_date, "end_date")
        self.validate_date_range(start_date, end_date)

    def _fetch_forecast_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch raw forecast data from Baostock"""
        bs_code = self._convert_symbol_to_baostock_format(symbol)

        rs = self._bs_instance.query_performance_forecast_report(
            code=bs_code,
            start_date=start_date,
            end_date=end_date,
        )

        if rs.error_code != "0":
            raise ValueError(f"Baostock query failed: {rs.error_msg}")

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return pd.DataFrame()

        return pd.DataFrame(data_list, columns=rs.fields)

    def _clean_forecast_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize forecast data"""
        if df.empty:
            return df

        column_map = {
            "code": "symbol",
            "pubDate": "publish_date",
            "statDate": "report_date",
            "updateDate": "update_date",
            "performanceForeType": "forecast_type",
            "performanceForeTypeEn": "forecast_type_en",
            "performanceForecastUp": "forecast_upper",
            "performanceForecastDown": "forecast_lower",
            "performanceForecastUpType": "forecast_upper_type",
            "performanceForecastDownType": "forecast_lower_type",
        }

        df = df.rename(columns=column_map)

        for col in ["forecast_upper", "forecast_lower"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        for col in ["publish_date", "report_date", "update_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        return df

    def _fetch_express_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch raw express data from Baostock"""
        bs_code = self._convert_symbol_to_baostock_format(symbol)

        rs = self._bs_instance.query_performance_express_report(
            code=bs_code,
            start_date=start_date,
            end_date=end_date,
        )

        if rs.error_code != "0":
            raise ValueError(f"Baostock query failed: {rs.error_msg}")

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return pd.DataFrame()

        return pd.DataFrame(data_list, columns=rs.fields)

    def _clean_express_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize express data"""
        if df.empty:
            return df

        column_map = {
            "code": "symbol",
            "pubDate": "publish_date",
            "statDate": "report_date",
            "updateDate": "update_date",
            "performanceExpressType": "express_type",
            "performanceExpressTypeEn": "express_type_en",
            "performanceExpressUp": "express_upper",
            "performanceExpressDown": "express_lower",
            "performanceExpressUpType": "express_upper_type",
            "performanceExpressDownType": "express_lower_type",
        }

        df = df.rename(columns=column_map)

        for col in ["express_upper", "express_lower"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        for col in ["publish_date", "report_date", "update_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        return df

    @cache(
        "performance_cache",
        key=lambda self, symbol, start_date, end_date: (f"baostock_forecast_{symbol}_{start_date}_{end_date}"),
    )
    def get_forecast_report(
        self, symbol: str, start_date: str, end_date: str, columns: list | None = None, row_filter: dict | None = None
    ) -> pd.DataFrame:
        """Get performance forecast report data

        Args:
            symbol: Stock symbol (e.g., '600000', '000001')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules

        Returns:
            pd.DataFrame: Performance forecast data with standardized columns
        """
        start_time = time.time()

        try:
            self._validate_params(symbol, start_date, end_date)

            self.logger.debug(
                "Fetching performance forecast data",
                extra={
                    "context": {
                        "source": "baostock",
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                        "action": "fetch_forecast_start",
                    }
                },
            )

            raw_df = self._fetch_forecast_data(symbol, start_date, end_date)
            cleaned_df = self._clean_forecast_data(raw_df)
            df = self.standardize_and_filter(cleaned_df, "baostock", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="performance_forecast",
                params={"symbol": symbol, "start_date": start_date, "end_date": end_date},
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
                endpoint="performance_forecast",
                params={"symbol": symbol, "start_date": start_date, "end_date": end_date},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch performance forecast data: {str(e)}") from e

    @cache(
        "performance_cache",
        key=lambda self, symbol, start_date, end_date: (f"baostock_express_{symbol}_{start_date}_{end_date}"),
    )
    def get_performance_express_report(
        self, symbol: str, start_date: str, end_date: str, columns: list | None = None, row_filter: dict | None = None
    ) -> pd.DataFrame:
        """Get performance express report data

        Args:
            symbol: Stock symbol (e.g., '600000', '000001')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules

        Returns:
            pd.DataFrame: Performance express data with standardized columns
        """
        start_time = time.time()

        try:
            self._validate_params(symbol, start_date, end_date)

            self.logger.debug(
                "Fetching performance express data",
                extra={
                    "context": {
                        "source": "baostock",
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                        "action": "fetch_express_start",
                    }
                },
            )

            raw_df = self._fetch_express_data(symbol, start_date, end_date)
            cleaned_df = self._clean_express_data(raw_df)
            df = self.standardize_and_filter(cleaned_df, "baostock", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="performance_express",
                params={"symbol": symbol, "start_date": start_date, "end_date": end_date},
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
                endpoint="performance_express",
                params={"symbol": symbol, "start_date": start_date, "end_date": end_date},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch performance express data: {str(e)}") from e

    def get_performance_forecast(self, date: str, **kwargs) -> pd.DataFrame:
        """Base class method - requires symbol parameter

        Args:
            date: Report date (used as both start_date and end_date)
            **kwargs: Additional parameters including symbol

        Returns:
            pd.DataFrame: Performance forecast data
        """
        symbol = kwargs.get("symbol")
        if not symbol:
            raise ValueError("Baostock requires 'symbol' parameter. Use get_forecast_report() method instead.")

        return self.get_forecast_report(symbol=symbol, start_date=date, end_date=date)

    def get_performance_express(self, date: str, **kwargs) -> pd.DataFrame:
        """Base class method - requires symbol parameter

        Args:
            date: Report date (used as both start_date and end_date)
            **kwargs: Additional parameters including symbol

        Returns:
            pd.DataFrame: Performance express data
        """
        symbol = kwargs.get("symbol")
        if not symbol:
            raise ValueError(
                "Baostock requires 'symbol' parameter. Use get_performance_express_report() method instead."
            )

        return self.get_performance_express_report(symbol=symbol, start_date=date, end_date=date)
