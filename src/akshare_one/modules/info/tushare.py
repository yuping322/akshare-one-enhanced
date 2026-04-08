"""
Tushare info data provider.

This module provides stock info data from Tushare Pro API.
"""


import pandas as pd

from ...tushare_client import get_tushare_client
from ..cache import cache
from .base import InfoDataFactory, InfoDataProvider


@InfoDataFactory.register("tushare")
class TushareInfoProvider(InfoDataProvider):
    """Info data provider for Tushare Pro."""

    def __init__(self, symbol: str, **kwargs) -> None:
        super().__init__(symbol, **kwargs)
        self._convert_symbol_to_ts_code()

    def get_source_name(self) -> str:
        return "tushare"

    def _convert_symbol_to_ts_code(self) -> None:
        """Convert symbol to Tushare ts_code format."""
        symbol = self.symbol
        if "." in symbol:
            self.ts_code = symbol
        elif symbol.startswith("6"):
            self.ts_code = f"{symbol}.SH"
        elif symbol.startswith(("0", "3")):
            self.ts_code = f"{symbol}.SZ"
        elif symbol.startswith(("4", "8", "9")):
            self.ts_code = f"{symbol}.BJ"
        else:
            self.ts_code = f"{symbol}.SH"

    def _convert_date_format(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to YYYYMMDD format for Tushare."""
        return date_str.replace("-", "")

    @cache(
        "info_cache",
        key=lambda self, start_date=None, end_date=None: f"tushare_daily_basic_{self.symbol}_{start_date}_{end_date}",
    )
    def get_daily_basic(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get daily basic indicators (PE, PB, turnover rate, etc.) from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date) if start_date else None
        end_date_ts = self._convert_date_format(end_date) if end_date else None

        try:
            raw_df = client.get_daily_basic(
                ts_code=self.ts_code,
                start_date=start_date_ts,
                end_date=end_date_ts,
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_daily_basic_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get daily basic from Tushare: {e}")
            return pd.DataFrame()

    def _process_daily_basic_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize daily basic data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")

        df = df.sort_values("date", ascending=False).reset_index(drop=True)

        return df

    @cache(
        "info_cache",
        key=lambda self, start_date=None, end_date=None: f"tushare_suspend_{self.symbol}_{start_date}_{end_date}",
    )
    def get_suspend_data(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get suspension/resumption data from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date) if start_date else None
        end_date_ts = self._convert_date_format(end_date) if end_date else None

        try:
            raw_df = client.get_suspend(
                ts_code=self.ts_code,
                start_date=start_date_ts,
                end_date=end_date_ts,
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_suspend_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get suspend data from Tushare: {e}")
            return pd.DataFrame()

    def _process_suspend_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize suspension data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "suspend_date" in df.columns:
            df["suspend_date"] = pd.to_datetime(df["suspend_date"], format="%Y%m%d")

        if "resume_date" in df.columns:
            df["resume_date"] = pd.to_datetime(df["resume_date"], format="%Y%m%d")

        df = df.sort_values("suspend_date", ascending=False).reset_index(drop=True)

        return df

    @cache(
        "hist_daily_cache",
        key=lambda self, start_date=None, end_date=None: f"tushare_stk_limit_{self.symbol}_{start_date}_{end_date}",
    )
    def get_stk_limit(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get daily limit up/down prices from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date) if start_date else None
        end_date_ts = self._convert_date_format(end_date) if end_date else None

        try:
            raw_df = client.get_stk_limit(
                ts_code=self.ts_code,
                start_date=start_date_ts,
                end_date=end_date_ts,
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_stk_limit_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get stk limit from Tushare: {e}")
            return pd.DataFrame()

    def _process_stk_limit_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize stk limit data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")

        df = df.sort_values("date", ascending=True).reset_index(drop=True)

        return df

    @cache(
        "adjust_factor_cache",
        key=lambda self, start_date=None, end_date=None: f"tushare_adj_factor_{self.symbol}_{start_date}_{end_date}",
    )
    def get_adj_factor(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: list | None = None,
        row_filter: dict | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Get adjustment factor data from Tushare."""
        client = get_tushare_client()

        if not client.is_available():
            self.logger.warning("Tushare API not available")
            return pd.DataFrame()

        start_date_ts = self._convert_date_format(start_date) if start_date else None
        end_date_ts = self._convert_date_format(end_date) if end_date else None

        try:
            raw_df = client.get_adj_factor(
                ts_code=self.ts_code,
                start_date=start_date_ts,
                end_date=end_date_ts,
            )

            if raw_df.empty:
                return pd.DataFrame()

            df = self._process_adj_factor_data(raw_df)
            return self.apply_data_filter(df, columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to get adj factor from Tushare: {e}")
            return pd.DataFrame()

    def _process_adj_factor_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize adj factor data."""
        df = self.map_source_fields(raw_df, "tushare")

        if "trade_date" in df.columns:
            df["date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")

        df = df.sort_values("date", ascending=True).reset_index(drop=True)

        return df

    def get_basic_info(
        self, columns: list | None = None, row_filter: dict | None = None, **kwargs
    ) -> pd.DataFrame:
        """Get basic info - wrapper for daily_basic with latest date."""
        return self.get_daily_basic(columns=columns, row_filter=row_filter, **kwargs)
