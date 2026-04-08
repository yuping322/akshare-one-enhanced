"""
Efinance fund flow data provider.

This module implements the fund flow data provider using Efinance as the data source.
"""

import time

import pandas as pd

from ...logging_config import get_logger, log_api_request
from .base import FundFlowFactory, FundFlowProvider

try:
    import efinance as ef

    EFINANCE_AVAILABLE = True
except ImportError:
    EFINANCE_AVAILABLE = False


EFINANCE_FUNDFLOW_FIELD_MAP = {
    "股票代码": "symbol",
    "主力净流入": "main_net_inflow",
    "小单净流入": "small_net_inflow",
    "中单净流入": "medium_net_inflow",
    "大单净流入": "large_net_inflow",
    "超大单净流入": "super_large_net_inflow",
    "主力净占比": "main_net_ratio",
    "日期": "date",
}


@FundFlowFactory.register("efinance")
class EfinanceFundFlowProvider(FundFlowProvider):
    """
    Fund flow data provider using Efinance as the data source.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)

        if not EFINANCE_AVAILABLE:
            raise ImportError("efinance is not installed. Please install it using: pip install efinance")

    def get_source_name(self) -> str:
        """Return the data source name."""
        return "efinance"

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw data from Efinance."""
        return pd.DataFrame()

    def get_history_bill(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get historical fund flow data for a stock from Efinance.

        Args:
            symbol: Stock symbol (6-digit string)
            **kwargs: Additional parameters (columns, row_filter)

        Returns:
            pd.DataFrame: Historical fund flow data
        """
        self.validate_symbol(symbol)

        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching history bill data",
                extra={
                    "context": {
                        "source": "efinance",
                        "symbol": symbol,
                        "action": "fetch_start",
                    }
                },
            )

            raw_df = ef.stock.get_history_bill(symbol)

            if raw_df.empty:
                self.logger.warning(f"No history bill data found for stock {symbol}")
                return pd.DataFrame()

            df = self._map_fields(raw_df)
            df = self.standardize_and_filter(df, "efinance", **kwargs)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_history_bill",
                params={"symbol": symbol},
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
                endpoint="get_history_bill",
                params={"symbol": symbol},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise RuntimeError(f"Failed to fetch history bill data: {str(e)}") from e

    def get_today_bill(self, symbol: str, **kwargs) -> pd.DataFrame:
        """
        Get today's fund flow data for a stock from Efinance.

        Args:
            symbol: Stock symbol (6-digit string)
            **kwargs: Additional parameters (columns, row_filter)

        Returns:
            pd.DataFrame: Today's fund flow data
        """
        self.validate_symbol(symbol)

        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching today bill data",
                extra={
                    "context": {
                        "source": "efinance",
                        "symbol": symbol,
                        "action": "fetch_start",
                    }
                },
            )

            raw_df = ef.stock.get_today_bill(symbol)

            if raw_df.empty:
                self.logger.warning(f"No today bill data found for stock {symbol}")
                return pd.DataFrame()

            df = self._map_fields(raw_df)
            df = self.standardize_and_filter(df, "efinance", **kwargs)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_today_bill",
                params={"symbol": symbol},
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
                endpoint="get_today_bill",
                params={"symbol": symbol},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            raise RuntimeError(f"Failed to fetch today bill data: {str(e)}") from e

    def _map_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map efinance Chinese field names to standard English names.

        Args:
            df: DataFrame with Chinese field names

        Returns:
            pd.DataFrame: DataFrame with English field names
        """
        df = df.copy()

        rename_cols = {}
        for cn_name, en_name in EFINANCE_FUNDFLOW_FIELD_MAP.items():
            if cn_name in df.columns:
                rename_cols[cn_name] = en_name

        if rename_cols:
            df = df.rename(columns=rename_cols)

        return df

    def get_stock_fund_flow(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get individual stock fund flow data from Efinance.
        Uses get_history_bill as the primary method.

        Args:
            symbol: Stock symbol (6-digit code)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Stock fund flow data
        """
        self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)

        try:
            df = self.get_history_bill(symbol, **kwargs)

            if not df.empty and "date" in df.columns:
                df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

            return df

        except Exception as e:
            self.logger.error(f"Failed to fetch stock fund flow for {symbol}: {e}")
            raise RuntimeError(f"Failed to fetch stock fund flow data: {str(e)}") from e
