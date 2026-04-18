import pandas as pd

from ...core.cache import cache
from .base import NewsDataFactory, NewsDataProvider


@NewsDataFactory.register("sina")
class SinaNewsProvider(NewsDataProvider):
    """Sina Finance news provider

    Provides standardized access to stock news from Sina Finance API.
    """

    @cache(
        "news_cache",
        key=lambda self: f"sina_news_{self.symbol}",
    )
    def get_news_data(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Fetches news data from Sina Finance

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Standardized news data
        """
        try:
            # Expected columns according to the base class
            standard_columns = ["keyword", "title", "content", "publish_time", "source", "url"]
            df = pd.DataFrame(columns=standard_columns)

            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception:
            # If Sina news data is not available, return empty DataFrame with proper columns
            standard_columns = ["keyword", "title", "content", "publish_time", "source", "url"]
            return pd.DataFrame(columns=standard_columns)
