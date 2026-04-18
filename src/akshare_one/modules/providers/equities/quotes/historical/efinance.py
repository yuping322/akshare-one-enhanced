import time

import pandas as pd

from ......logging_config import get_logger, log_api_request
from .....core.cache import cache
from .base import HistoricalDataFactory, HistoricalDataProvider

try:
    import efinance as ef

    EFINANCE_AVAILABLE = True
except ImportError:
    EFINANCE_AVAILABLE = False


@HistoricalDataFactory.register("efinance")
class EfinanceHistoricalProvider(HistoricalDataProvider):
    """Adapter for Efinance historical stock data API"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)

        if not EFINANCE_AVAILABLE:
            raise ImportError("efinance is not installed. Please install it using: pip install efinance")

    @cache(
        "hist_data_cache",
        key=lambda self, **kwargs: (
            f"efinance_hist_{self.symbol}_{self.interval}_{self.interval_multiplier}_{self.adjust}"
        ),
    )
    def get_hist_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches Efinance historical market data

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
                - amount (optional)
                - amplitude (optional)
                - pct_change (optional)
                - change (optional)
                - turnover_rate (optional)
        """
        self.interval = self.interval.lower()
        self._validate_interval_params(self.interval, self.interval_multiplier)

        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching historical data",
                extra={
                    "context": {
                        "source": "efinance",
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

            df = self._get_historical_data()

            df = self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
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
                source="efinance",
                endpoint="historical",
                params={"symbol": self.symbol, "interval": self.interval},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise ValueError(f"Failed to fetch historical data: {str(e)}") from e

    def _get_historical_data(self) -> pd.DataFrame:
        """Fetches historical data from efinance"""
        beg = self._convert_date_format(self.start_date)
        end = self._convert_date_format(self.end_date)
        klt = self._map_interval_to_klt(self.interval, self.interval_multiplier)
        fqt = self._map_adjust_param(self.adjust)

        raw_df = ef.stock.get_quote_history(
            self.symbol,
            beg=beg,
            end=end,
            klt=klt,
            fqt=fqt,
        )

        if raw_df.empty:
            raise ValueError(f"No data found for symbol {self.symbol}")

        df = self._map_fields(raw_df)

        if self.interval in ["minute", "hour"] and self.interval_multiplier > 1:
            df = self._resample_intraday_data(df)

        return df

    def _map_interval_to_klt(self, interval: str, multiplier: int) -> int:
        """Maps interval and multiplier to efinance klt parameter

        Args:
            interval: Data interval (minute, hour, day, week, month, year)
            multiplier: Interval multiplier

        Returns:
            klt value for efinance API
        """
        if interval == "minute":
            klt_map = {1: 1, 5: 5, 15: 15, 30: 30, 60: 60}
            return klt_map.get(multiplier, multiplier)
        elif interval == "hour":
            return 60
        elif interval == "day":
            return 101
        elif interval == "week":
            return 102
        elif interval == "month":
            return 103
        elif interval == "year":
            return 103
        else:
            raise ValueError(f"Unsupported interval: {interval}")

    def _convert_date_format(self, date_str: str) -> str:
        """Converts date format to YYYYMMDD for efinance"""
        return date_str.replace("-", "") if "-" in date_str else date_str

    def _map_adjust_param(self, adjust: str) -> int:
        """Maps adjustment parameters to efinance fqt parameter

        Args:
            adjust: Adjustment type (none, qfq, hfq)

        Returns:
            fqt value: 0=none, 1=forward adjustment, 2=backward adjustment
        """
        adjust_map = {
            "none": 0,
            "qfq": 1,
            "hfq": 2,
        }
        return adjust_map.get(adjust, 0)

    def _map_fields(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Maps efinance Chinese field names to standard English names"""
        column_map = {
            "股票名称": "name",
            "股票代码": "symbol",
            "日期": "timestamp",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
            "振幅": "amplitude",
            "涨跌幅": "pct_change",
            "涨跌额": "change",
            "换手率": "turnover_rate",
        }

        df = raw_df.rename(columns=column_map)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            if df["timestamp"].dt.tz is None:
                df["timestamp"] = df["timestamp"].dt.tz_localize("Asia/Shanghai")

        if "volume" in df.columns:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype("int64")

        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        for col in ["amplitude", "pct_change", "change", "turnover_rate"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def _resample_intraday_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resamples intraday data for custom multipliers"""
        freq = f"{self.interval_multiplier}min" if self.interval == "minute" else f"{self.interval_multiplier}h"

        df_copy = df.copy()
        df_copy = df_copy.set_index("timestamp")

        agg_dict = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }

        if "amount" in df_copy.columns:
            agg_dict["amount"] = "sum"

        resampled = df_copy.resample(freq).agg(agg_dict)
        return resampled.reset_index()

    def _validate_interval_params(self, interval: str, multiplier: int) -> None:
        """Validates the validity of interval and multiplier"""
        if interval not in self.get_supported_intervals():
            raise ValueError(f"Unsupported interval parameter: {interval}")

        if interval in ["minute", "hour"] and multiplier < 1:
            raise ValueError(f"interval_multiplier for {interval} level must be ≥ 1")

        if interval == "year":
            self.logger.warning(
                "Year interval is mapped to monthly data in efinance, consider using month interval with multiplier"
            )
