"""
Efinance shareholder data provider.

This module implements the shareholder data provider using efinance as the data source.
"""

import time
from datetime import datetime

import pandas as pd

from ...logging_config import get_logger, log_api_request
from ...constants import SYMBOL_ZFILL_WIDTH
from ..cache import cache
from .base import ShareholderFactory, ShareholderProvider

try:
    import efinance as ef

    EFINANCE_AVAILABLE = True
except ImportError:
    EFINANCE_AVAILABLE = False


@ShareholderFactory.register("efinance")
class EfinanceShareholderProvider(ShareholderProvider):
    """Shareholder data provider using efinance as the data source."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)

        if not EFINANCE_AVAILABLE:
            raise ImportError("efinance is not installed. Please install it using: pip install efinance")

    def get_source_name(self) -> str:
        return "efinance"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    @cache(
        "shareholder_cache",
        key=lambda self, stock_code, top=10: f"efinance_top10_stock_holder_{stock_code}_{top}",
    )
    def get_top10_stock_holder_info(self, stock_code: str, top: int = 10) -> pd.DataFrame:
        """
        Get top 10 stock holder information from efinance.

        Args:
            stock_code: Stock code (e.g., '600000')
            top: Number of top holders to return

        Returns:
            pd.DataFrame: Top holder data with standardized fields
        """
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching top10 stock holder info",
                extra={
                    "context": {
                        "source": "efinance",
                        "stock_code": stock_code,
                        "top": top,
                        "action": "fetch_start",
                    }
                },
            )

            raw_df = ef.stock.get_top10_stock_holder_info(stock_code, top)

            if raw_df.empty:
                return self.create_empty_dataframe(["holder_name", "holding_shares", "holding_ratio", "report_period"])

            df = self._map_holder_fields(raw_df)

            if top and len(df) > top:
                df = df.head(top)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_top10_stock_holder_info",
                params={"stock_code": stock_code, "top": top},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return self.ensure_json_compatible(df)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_top10_stock_holder_info",
                params={"stock_code": stock_code, "top": top},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            self.logger.error(f"Failed to fetch top10 stock holder info: {e}", exc_info=True)
            return self.create_empty_dataframe(["holder_name", "holding_shares", "holding_ratio", "report_period"])

    @cache(
        "shareholder_cache",
        key=lambda self, date: f"efinance_latest_holder_number_{date}",
    )
    def get_latest_holder_number(self, date: str) -> pd.DataFrame:
        """
        Get latest holder number from efinance.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: Holder number data
        """
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching latest holder number",
                extra={
                    "context": {
                        "source": "efinance",
                        "date": date,
                        "action": "fetch_start",
                    }
                },
            )

            raw_df = ef.stock.get_latest_holder_number(date)

            if raw_df.empty:
                return self.create_empty_dataframe(["symbol", "name", "holder_number", "date"])

            df = self._map_holder_number_fields(raw_df, date)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_latest_holder_number",
                params={"date": date},
                duration_ms=duration_ms,
                status="success",
                rows=len(df),
            )

            return self.ensure_json_compatible(df)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_latest_holder_number",
                params={"date": date},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            self.logger.error(f"Failed to fetch latest holder number: {e}", exc_info=True)
            return self.create_empty_dataframe(["symbol", "name", "holder_number", "date"])

    def _map_holder_fields(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Map efinance Chinese field names to standard English names for holder data."""
        column_map = {
            "股东名称": "holder_name",
            "持股数量": "holding_shares",
            "持股比例": "holding_ratio",
            "报告期": "report_period",
            "股票代码": "symbol",
            "更新日期": "update_date",
            "股东代码": "holder_code",
            "持股数": "holding_shares",
            "增减": "change",
            "变动率": "change_rate",
        }

        df = raw_df.copy()

        rename_cols = {}
        for cn_name, en_name in column_map.items():
            if cn_name in df.columns:
                rename_cols[cn_name] = en_name

        if rename_cols:
            df = df.rename(columns=rename_cols)

        numeric_cols = ["holding_shares", "holding_ratio", "change_rate"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def _map_holder_number_fields(self, raw_df: pd.DataFrame, date: str) -> pd.DataFrame:
        """Map efinance Chinese field names to standard English names for holder number data."""
        column_map = {
            "股票代码": "symbol",
            "股票名称": "name",
            "股东人数": "holder_number",
            "股东户数": "holder_number",
            "日期": "date",
            "股东户数统计截止日": "stat_date",
        }

        df = raw_df.copy()

        rename_cols = {}
        for cn_name, en_name in column_map.items():
            if cn_name in df.columns:
                rename_cols[cn_name] = en_name

        if rename_cols:
            df = df.rename(columns=rename_cols)

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str).str.zfill(SYMBOL_ZFILL_WIDTH)

        if "holder_number" in df.columns:
            df["holder_number"] = pd.to_numeric(df["holder_number"], errors="coerce")

        if "date" not in df.columns:
            df["date"] = date

        cols = ["symbol", "name", "holder_number", "date"]
        available_cols = [col for col in cols if col in df.columns]
        return df[available_cols] if available_cols else df

    def get_shareholder_changes(
        self, symbol: str | None = None, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get shareholder changes from efinance.

        Note: efinance doesn't support shareholder changes data, this method raises NotImplementedError.
        """
        raise NotImplementedError("efinance does not support shareholder changes. Use 'eastmoney' provider instead.")

    def get_top_shareholders(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get top shareholders from efinance.

        Note: efinance doesn't support top shareholders data, this method raises NotImplementedError.
        """
        raise NotImplementedError("efinance does not support top shareholders. Use 'eastmoney' provider instead.")

    def get_institution_holdings(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get institution holdings from efinance.

        Note: efinance doesn't support institution holdings data, this method raises NotImplementedError.
        """
        raise NotImplementedError("efinance does not support institution holdings. Use 'eastmoney' provider instead.")

    def get_top10_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get top 10 shareholders from efinance.

        Note: efinance doesn't support top 10 shareholders data, this method raises NotImplementedError.
        """
        raise NotImplementedError("efinance does not support top 10 shareholders. Use 'lixinger' provider instead.")

    def get_top10_float_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get top 10 float shareholders from efinance.

        Note: efinance doesn't support top 10 float shareholders data, this method raises NotImplementedError.
        """
        raise NotImplementedError(
            "efinance does not support top 10 float shareholders. Use 'lixinger' provider instead."
        )

    def get_fund_shareholders(
        self, symbol: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
    ) -> pd.DataFrame:
        """
        Get fund shareholders from efinance.

        Note: efinance doesn't support fund shareholders data, this method raises NotImplementedError.
        """
        raise NotImplementedError("efinance does not support fund shareholders. Use 'lixinger' provider instead.")
