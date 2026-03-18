from abc import abstractmethod

import pandas as pd

from ..base import BaseProvider


class NewsDataProvider(BaseProvider):
    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbol = symbol

    def get_source_name(self) -> str:
        return "news"

    def get_data_type(self) -> str:
        return "news"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_news_data()

    @abstractmethod
    def get_news_data(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Fetches news data

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame:
            - keyword: 关键词
            - title: 新闻标题
            - content: 新闻内容
            - publish_time: 发布时间
            - source: 文章来源
            - url: 新闻链接
        """
        pass
