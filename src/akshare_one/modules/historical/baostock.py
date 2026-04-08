import time
import warnings

import pandas as pd

from ...logging_config import get_logger, log_api_request
from ..cache import cache
from .base import HistoricalDataFactory, HistoricalDataProvider

warnings.filterwarnings("ignore", message=".*lzma.*")


@HistoricalDataFactory.register("baostock")
class BaostockHistorical(HistoricalDataProvider):
    """Adapter for Baostock historical stock data API"""

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

    @cache(
        "hist_data_cache",
        key=lambda self: (f"baostock_hist_{self.symbol}_{self.interval}_{self.interval_multiplier}_{self.adjust}"),
    )
    def get_hist_data(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Fetches Baostock historical market data

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame:
                - timestamp
                - open
                - high
                - low
                - close
                - volume
        """
        self.interval = self.interval.lower()
        self._validate_interval_params(self.interval, self.interval_multiplier)

        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching historical data",
                extra={
                    "context": {
                        "source": "baostock",
                        "symbol": self.symbol,
                        "interval": self.interval,
                        "interval_multiplier": self.interval_multiplier,
                        "adjust": self.adjust,
                        "start_date": self.start_date,
                        "end_date": self.end_date,
                        "action": "fetch_start",
                    }
                },
            )

            if self.interval in ["minute", "hour"]:
                raise ValueError("Baostock does not support minute or hour level data, only day/week/month")

            df = self._get_daily_plus_data()

            df = self.standardize_and_filter(df, "baostock", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="historical",
                params={"symbol": self.symbol, "interval": self.interval, "adjust": self.adjust},
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
                endpoint="historical",
                params={"symbol": self.symbol, "interval": self.interval},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch historical data: {str(e)}") from e

    def _get_daily_plus_data(self) -> pd.DataFrame:
        """Fetches daily and higher-level data (day/week/month)"""
        bs_code = self._convert_symbol_to_baostock_format(self.symbol)

        start_date = self._convert_date_format(self.start_date)
        end_date = self._convert_date_format(self.end_date)

        frequency_map = {
            "day": "d",
            "week": "w",
            "month": "m",
        }
        frequency = frequency_map[self.interval]

        adjust_flag = self._map_adjust_param(self.adjust)

        # Different fields for different frequencies
        # Weekly/monthly data doesn't support all fields like daily data
        if self.interval == "day":
            fields = "date,code,open,high,low,close,volume,amount,adjustflag,turn,tradestatus"
        else:
            # Weekly/monthly data - limited fields
            fields = "date,code,open,high,low,close,volume,amount,adjustflag"

        rs = self._bs_instance.query_history_k_data_plus(
            bs_code,
            fields,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag=adjust_flag,
        )

        if rs.error_code != "0":
            raise ValueError(f"Baostock query failed: {rs.error_msg}")

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return pd.DataFrame()

        raw_df = pd.DataFrame(data_list, columns=rs.fields)

        if self.interval_multiplier > 1:
            raw_df = self._resample_data(raw_df, self.interval, self.interval_multiplier)

        return self._clean_data(raw_df)

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

    def _convert_date_format(self, date_str: str) -> str:
        """Converts date format from YYYY-MM-DD to YYYY-MM-DD (baostock uses YYYY-MM-DD)"""
        return date_str

    def _map_adjust_param(self, adjust: str) -> str:
        """Maps adjustment parameters to baostock format:
        - 'none' -> '3' (不复权)
        - 'qfq' -> '2' (前复权)
        - 'hfq' -> '1' (后复权)
        """
        adjust_map = {
            "none": "3",
            "qfq": "2",
            "hfq": "1",
        }
        return adjust_map.get(adjust, "3")

    def _validate_interval_params(self, interval: str, multiplier: int) -> None:
        """Validates the validity of interval and multiplier"""
        supported_intervals = ["day", "week", "month"]
        if interval not in supported_intervals:
            raise ValueError(f"Baostock only supports intervals: {supported_intervals}, got: {interval}")

        if multiplier < 1:
            raise ValueError(f"interval_multiplier must be >= 1, got: {multiplier}")

    def _resample_data(self, df: pd.DataFrame, interval: str, multiplier: int) -> pd.DataFrame:
        """Resamples daily and higher-level data to the specified interval"""
        freq_map = {
            "day": f"{multiplier}D",
            "week": f"{multiplier}W-MON",
            "month": f"{multiplier}MS",
        }
        freq = freq_map[interval]

        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        agg_dict = {}
        for col in numeric_cols:
            if col in ["open"]:
                agg_dict[col] = "first"
            elif col in ["high"]:
                agg_dict[col] = "max"
            elif col in ["low"]:
                agg_dict[col] = "min"
            elif col in ["close"]:
                agg_dict[col] = "last"
            elif col in ["volume", "amount"]:
                agg_dict[col] = "sum"
            else:
                agg_dict[col] = "last"

        resampled = df.resample(freq).agg(agg_dict)
        return resampled.reset_index()

    def _clean_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and standardizes daily and higher-level data"""
        column_map = {
            "date": "timestamp",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
            "amount": "amount",
            "turn": "turnover_rate",
            "tradestatus": "trade_status",
        }

        available_columns = {src: target for src, target in column_map.items() if src in raw_df.columns}

        if not available_columns:
            raise ValueError("Expected columns not found in raw data")

        df = raw_df.rename(columns=available_columns)

        numeric_columns = ["open", "high", "low", "close", "volume", "amount"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("Asia/Shanghai")

        if "volume" in df.columns:
            df["volume"] = df["volume"].astype("int64")

        return self._select_standard_columns(df)

    def _select_standard_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selects and orders the standard output columns"""
        standard_columns = [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        return df[[col for col in standard_columns if col in df.columns]]

    @cache(
        "trade_dates_cache",
        key=lambda self, exchange, start_date, end_date: f"baostock_trade_dates_{exchange}_{start_date}_{end_date}",
    )
    def get_trade_dates(
        self, exchange: str = "sh", start_date: str = "1990-01-01", end_date: str = "2030-12-31"
    ) -> pd.DataFrame:
        """Fetches trade calendar data

        Args:
            exchange: Exchange code ('sh' for Shanghai, 'sz' for Shenzhen). Default is 'sh'.
            start_date: Start date in YYYY-MM-DD format. Default is '1990-01-01'.
            end_date: End date in YYYY-MM-DD format. Default is '2030-12-31'.

        Returns:
            pd.DataFrame:
                - date: Date
                - is_trading_day: Whether it's a trading day (True/False)
        """
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching trade calendar",
                extra={
                    "context": {
                        "source": "baostock",
                        "exchange": exchange,
                        "start_date": start_date,
                        "end_date": end_date,
                        "action": "fetch_start",
                    }
                },
            )

            rs = self._bs_instance.query_trade_dates(start_date=start_date, end_date=end_date)

            if rs.error_code != "0":
                raise ValueError(f"Baostock query_trade_dates failed: {rs.error_msg}")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return pd.DataFrame(columns=["date", "is_trading_day"])

            raw_df = pd.DataFrame(data_list, columns=rs.fields)

            result_df = pd.DataFrame(
                {
                    "date": pd.to_datetime(raw_df["calendar_date"]),
                    "is_trading_day": raw_df["is_trading_day"].astype(str) == "1",
                }
            )

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="trade_dates",
                params={"exchange": exchange, "start_date": start_date, "end_date": end_date},
                duration_ms=duration_ms,
                status="success",
                rows=len(result_df),
            )

            return result_df
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="baostock",
                endpoint="trade_dates",
                params={"exchange": exchange, "start_date": start_date, "end_date": end_date},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch trade calendar: {str(e)}") from e
