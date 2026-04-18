import time

import akshare as ak
import pandas as pd

from ....metrics.stats import get_stats_collector
from ...core.cache import cache
from .base import NewsDataFactory, NewsDataProvider


@NewsDataFactory.register("eastmoney")
class EastmoneyNewsProvider(NewsDataProvider):
    @cache(
        "news_cache",
        key=lambda self: f"eastmoney_news_{self.symbol}",
    )
    def get_news_data(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """获取东方财富个股新闻数据"""
        start_time = time.time()

        try:
            raw_df = ak.stock_news_em(symbol=self.symbol)
            result = self.standardize_and_filter(raw_df, "eastmoney", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, True)

            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            stats_collector = get_stats_collector()
            stats_collector.record_request("eastmoney", duration_ms, False)
            raise
