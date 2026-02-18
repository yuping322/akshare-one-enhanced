import time

import akshare as ak
import pandas as pd

from ...logging_config import get_logger, log_api_request
from ..cache import cache
from .base import RealtimeDataProvider


class EastmoneyRealtime(RealtimeDataProvider):
    def __init__(self, symbol: str | None = None):
        super().__init__(symbol=symbol)
        self.logger = get_logger(__name__)

    @cache(
        "realtime_cache",
        key=lambda self: f"eastmoney_{self.symbol if self.symbol else 'all'}",
    )
    def get_current_data(self) -> pd.DataFrame:
        """获取沪深京A股实时行情数据"""
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching realtime data",
                extra={
                    "context": {
                        "source": "eastmoney",
                        "symbol": self.symbol or "all",
                        "action": "fetch_start",
                    }
                },
            )

            raw_df = ak.stock_zh_a_spot_em()
            df = self._clean_spot_data(raw_df)

            if self.symbol:
                df = df[df["symbol"] == self.symbol].reset_index(drop=True)

                if df.empty:
                    self.logger.warning(
                        f"No data found for symbol {self.symbol}",
                        extra={
                            "context": {
                                "source": "eastmoney",
                                "symbol": self.symbol,
                                "issue": "symbol_not_found",
                            }
                        },
                    )

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="eastmoney",
                endpoint="realtime",
                params={"symbol": self.symbol or "all"},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return df

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="eastmoney",
                endpoint="realtime",
                params={"symbol": self.symbol or "all"},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise

    def _clean_spot_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """清理和标准化实时行情数据"""
        column_mapping = {
            "代码": "symbol",
            "最新价": "price",
            "涨跌额": "change",
            "涨跌幅": "pct_change",
            "成交量": "volume",
            "成交额": "amount",
            "今开": "open",
            "最高": "high",
            "最低": "low",
            "昨收": "prev_close",
        }

        df = raw_df.rename(columns=column_mapping)

        # Check for missing required columns
        missing_cols = [col for col in column_mapping.values() if col not in df.columns]
        if missing_cols:
            self.logger.warning(
                "Missing columns in realtime data",
                extra={
                    "context": {
                        "source": "eastmoney",
                        "missing_columns": missing_cols,
                        "available_columns": list(df.columns),
                    }
                },
            )

        df = df.assign(timestamp=lambda x: pd.Timestamp.now(tz="Asia/Shanghai"))

        required_columns = [
            "symbol",
            "price",
            "change",
            "pct_change",
            "timestamp",
            "volume",
            "amount",
            "open",
            "high",
            "low",
            "prev_close",
        ]

        available_columns = [col for col in required_columns if col in df.columns]
        return df[available_columns]
