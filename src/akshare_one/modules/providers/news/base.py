import numpy as np
import pandas as pd

from ...core.base import BaseProvider
from ...core.factory import BaseFactory


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

    def ensure_json_compatible(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure DataFrame is JSON-compatible but preserve datetime objects for publish_time.

        News data benefits from having actual datetime objects for publish_time field
        to enable time-based filtering and analysis.
        """
        if df.empty:
            return df

        df = df.copy()

        # 1. Handle NaN and Infinity in numeric columns
        for col in df.select_dtypes(include=["float64", "float32", "float16"]).columns:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            df[col] = df[col].replace({np.nan: None})

        # 2. Convert datetime columns to strings (except publish_time)
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns
        for col in datetime_cols:
            if col == "publish_time":
                # Keep publish_time as datetime object (timezone-aware)
                continue
            # Convert other datetime columns to strings
            try:
                if hasattr(df[col].dt, 'time') and df[col].dt.time.eq(pd.Timestamp("00:00:00").time()).all():
                    df[col] = df[col].dt.strftime("%Y-%m-%d")
                else:
                    df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                # If conversion fails, keep the original datetime
                pass

        # 3. Ensure symbol-like columns are strings
        for col in df.columns:
            if col in ["symbol", "code", "keyword", "stock_code"]:
                df[col] = df[col].astype(str)
                # Preserve leading zeros
                df[col] = df[col].str.strip()

        return df

    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize news data format.

        Override parent method to keep publish_time as datetime object instead of string.
        """
        if df.empty:
            return df

        # 1. Infer field types and amount units
        field_types = self.infer_field_types(df)
        amount_fields = self.infer_amount_fields(df)

        # 2. Apply amount unit conversion (all to yuan)
        if amount_fields:
            df = self.apply_amount_conversion(df, amount_fields)

        # 3. Apply field name validation and standardization (snake_case, types)
        if field_types:
            df = self.apply_field_standardization(df, field_types)

        # 4. Convert publish_time to datetime (keep as datetime object with timezone)
        if "publish_time" in df.columns:
            try:
                # Convert to datetime and localize to UTC
                df["publish_time"] = pd.to_datetime(df["publish_time"]).dt.tz_localize("UTC")
            except Exception:
                # Skip if conversion fails
                pass

        return df

    def get_news_data(self, columns: list | None = None, row_filter: dict | None = None, **kwargs) -> pd.DataFrame:
        """Fetches news data"""
        return self._execute_api_mapped("get_news_data", columns=columns, row_filter=row_filter, **kwargs)


class NewsDataFactory(BaseFactory["NewsDataProvider"]):
    """Factory class for creating news data providers."""

    _providers: dict[str, type["NewsDataProvider"]] = {}
