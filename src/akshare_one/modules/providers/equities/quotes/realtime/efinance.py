import time
from datetime import datetime

import efinance as ef
import pandas as pd

from ......logging_config import get_logger, log_api_request
from .....core.cache import cache
from .base import RealtimeDataFactory, RealtimeDataProvider


EFINANCE_FIELD_MAP = {
    "股票代码": "symbol",
    "股票名称": "name",
    "涨跌幅": "pct_change",
    "最新价": "price",
    "最高": "high",
    "最低": "low",
    "今开": "open",
    "涨跌额": "change",
    "换手率": "turnover_rate",
    "成交量": "volume",
    "成交额": "amount",
    "昨日收盘": "prev_close",
    "总市值": "market_cap",
    "流通市值": "float_market_cap",
}


@RealtimeDataFactory.register("efinance")
class EfinanceRealtimeProvider(RealtimeDataProvider):
    def __init__(self, symbol: str | None = None, **kwargs):
        super().__init__(symbol=symbol, **kwargs)
        self.logger = get_logger(__name__)

    @cache(
        "realtime_cache",
        key=lambda self: f"efinance_{self.symbol if self.symbol else 'all'}",
    )
    def get_current_data(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """获取沪深京A股实时行情数据"""
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching realtime data",
                extra={
                    "context": {
                        "source": "efinance",
                        "symbol": self.symbol or "all",
                        "action": "fetch_start",
                    }
                },
            )

            if self.symbol:
                raw_df = ef.stock.get_latest_quote([self.symbol])
            else:
                raw_df = ef.stock.get_realtime_quotes()

            if raw_df.empty:
                return pd.DataFrame(columns=columns) if columns else raw_df

            df = self._map_fields(raw_df)
            df = self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)

            if self.symbol and not df.empty:
                df = df[df["symbol"] == self.symbol].reset_index(drop=True)

            df["timestamp"] = datetime.now()

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
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
                source="efinance",
                endpoint="realtime",
                params={"symbol": self.symbol or "all"},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise

    def _map_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """映射efinance字段到标准字段名"""
        df = df.copy()

        rename_cols = {}
        for cn_name, en_name in EFINANCE_FIELD_MAP.items():
            if cn_name in df.columns:
                rename_cols[cn_name] = en_name

        if rename_cols:
            df = df.rename(columns=rename_cols)

        return df


EfinanceRealtime = EfinanceRealtimeProvider
