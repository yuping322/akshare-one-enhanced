"""
Sina restricted stock release data provider.

This module implements restricted release data provider using Sina as the data source.
"""

import pandas as pd

from ......constants import SYMBOL_ZFILL_WIDTH
from .base import RestrictedReleaseFactory, RestrictedReleaseProvider


@RestrictedReleaseFactory.register("sina")
class SinaRestrictedReleaseProvider(RestrictedReleaseProvider):
    """
    Restricted release data provider using Sina as the data source.

    Provides restricted stock release (限售解禁) data.
    """

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "sina"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data - not directly used."""
        return pd.DataFrame()

    def get_restricted_release(self, symbol: str | None, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get restricted stock release data from Sina.

        Note: Sina only provides data for a specific stock symbol.

        Args:
            symbol: Stock symbol (e.g., '600000'). Required for Sina.
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Standardized restricted release data with columns:
                - symbol: Stock symbol
                - release_date: Release date (YYYY-MM-DD)
                - release_shares: Released shares
                - release_value: Released market value
                - release_type: Release type
                - shareholder_name: Shareholder name

        Raises:
            ValueError: If symbol is not provided
        """
        if not symbol:
            raise ValueError("symbol is required for Sina restricted release API")

        self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        try:
            import akshare as ak

            raw_df = ak.stock_restricted_release_queue_sina(symbol=symbol)

            if raw_df.empty:
                return self.create_empty_dataframe(
                    [
                        "symbol",
                        "release_date",
                        "release_shares",
                        "release_value",
                        "release_type",
                        "shareholder_name",
                    ]
                )

            standardized = pd.DataFrame()

            standardized["symbol"] = symbol.zfill(SYMBOL_ZFILL_WIDTH)

            if "解禁时间" in raw_df.columns:
                standardized["release_date"] = pd.to_datetime(raw_df["解禁时间"]).dt.strftime("%Y-%m-%d")
            elif "日期" in raw_df.columns:
                standardized["release_date"] = pd.to_datetime(raw_df["日期"]).dt.strftime("%Y-%m-%d")
            else:
                standardized["release_date"] = ""

            if "解禁数量" in raw_df.columns:
                standardized["release_shares"] = pd.to_numeric(raw_df["解禁数量"], errors="coerce").fillna(0.0)
            else:
                standardized["release_shares"] = 0.0

            if "解禁市值" in raw_df.columns:
                standardized["release_value"] = pd.to_numeric(raw_df["解禁市值"], errors="coerce").fillna(0.0)
            else:
                standardized["release_value"] = 0.0

            if "股份类型" in raw_df.columns:
                standardized["release_type"] = raw_df["股份类型"].astype(str)
            else:
                standardized["release_type"] = ""

            if "股东名称" in raw_df.columns:
                standardized["shareholder_name"] = raw_df["股东名称"].astype(str)
            else:
                standardized["shareholder_name"] = ""

            if len(standardized) > 0 and standardized["release_date"].iloc[0]:
                mask = (standardized["release_date"] >= start_date) & (standardized["release_date"] <= end_date)
                result = standardized[mask].reset_index(drop=True)
            else:
                result = standardized

            return self.standardize_and_filter(
                result, source="sina", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
            )

        except Exception as e:
            self.logger.error(f"Failed to fetch restricted release data from Sina: {e}")
            return self.create_empty_dataframe(
                [
                    "symbol",
                    "release_date",
                    "release_shares",
                    "release_value",
                    "release_type",
                    "shareholder_name",
                ]
            )

    def get_restricted_release_calendar(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get restricted stock release calendar from Sina.

        Note: Sina does not provide calendar functionality, returns empty DataFrame.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Empty DataFrame (not supported by Sina)
        """
        return self.create_empty_dataframe(["date", "release_stock_count", "total_release_value"])
