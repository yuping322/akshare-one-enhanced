import pandas as pd

from .....core.cache import cache
from .base import InfoDataFactory, InfoDataProvider


@InfoDataFactory.register("sina")
class SinaInfoProvider(InfoDataProvider):
    """Sina Finance stock basic info provider

    Provides standardized access to stock basic information from Sina Finance API.
    """

    # Mapping from our standard column names for basic info
    _expected_columns = [
        "price",
        "symbol",
        "name",
        "total_shares",
        "float_shares",
        "total_market_cap",
        "float_market_cap",
        "industry",
        "listing_date",
    ]

    @cache(
        "info_cache",
        key=lambda self: f"sina_info_{self.symbol}",
    )
    def get_basic_info(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Fetches stock basic info data from Sina Finance

        Args:
            columns: List of columns to keep.
            row_filter: Dictionary of row filter rules.

        Returns:
            pd.DataFrame: Standardized stock basic info data
        """
        try:
            df = pd.DataFrame(columns=self._expected_columns)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)

        except Exception:
            return pd.DataFrame(columns=self._expected_columns)

SinaInfo = SinaInfoProvider
