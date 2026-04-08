import akshare as ak
import pandas as pd

from ..cache import cache
from .base import NewsDataFactory, NewsDataProvider


@NewsDataFactory.register("eastmoney")
class EastmoneyNewsProvider(NewsDataProvider):
    @cache(
        "news_cache",
        key=lambda self: f"eastmoney_news_{self.symbol}",
    )
    def get_news_data(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """获取东方财富个股新闻数据"""
        raw_df = ak.stock_news_em(symbol=self.symbol)
        return self.standardize_and_filter(raw_df, "eastmoney", columns=columns, row_filter=row_filter)
