import time

import akshare as ak
import pandas as pd

from ...logging_config import get_logger, log_api_request
from ...metrics import get_stats_collector
from ..cache import cache
from .base import RealtimeDataFactory, RealtimeDataProvider


@RealtimeDataFactory.register("eastmoney")
class EastmoneyRealtimeProvider(RealtimeDataProvider):
    def __init__(self, symbol: str | None = None, **kwargs):
        super().__init__(symbol=symbol, **kwargs)
        self.logger = get_logger(__name__)

    @cache(
        "realtime_cache",
        key=lambda self: f"eastmoney_{self.symbol if self.symbol else 'all'}",
    )
    def get_current_data(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
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
            df = self.standardize_and_filter(raw_df, "eastmoney", columns=columns, row_filter=row_filter)

            if self.symbol and not df.empty:
                df = df[df["symbol"] == self.symbol].reset_index(drop=True)

            duration_ms = (time.time() - start_time) * 1000

            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, True)

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

            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, False)

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


EastmoneyRealtime = EastmoneyRealtimeProvider
