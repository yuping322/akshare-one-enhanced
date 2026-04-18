"""
Efinance board data provider.

This module implements the board data provider using efinance as the data source.
"""

import time

import efinance as ef
import pandas as pd

from .....logging_config import get_logger, log_api_request
from .base import BoardFactory, BoardProvider

BELONG_BOARD_FIELD_MAP = {
    "板块代码": "board_code",
    "板块名称": "board_name",
    "板块类型": "board_type",
    "股票代码": "stock_code",
    "最新价": "price",
    "涨跌幅": "pct_change",
    "涨跌额": "change",
    "成交量": "volume",
    "成交额": "amount",
    "换手率": "turnover_rate",
    "总市值": "market_cap",
    "流通市值": "float_market_cap",
}


@BoardFactory.register("efinance")
class EfinanceBoardProvider(BoardProvider):
    """
    Board data provider using efinance as the data source.

    Provides:
    - get_belong_board: Get which boards/concepts a stock belongs to
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)

    def get_source_name(self) -> str:
        return "efinance"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_belong_board(
        self,
        stock_code: str,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """
        Get which boards/concepts a stock belongs to.

        Args:
            stock_code: Stock code (e.g., '600000', '000001')
            columns: List of columns to keep
            row_filter: Dictionary of row filter rules

        Returns:
            pd.DataFrame: Boards/concepts the stock belongs to
        """
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching belong board data",
                extra={
                    "context": {
                        "source": "efinance",
                        "stock_code": stock_code,
                        "action": "fetch_start",
                    }
                },
            )

            raw_df = ef.stock.get_belong_board(stock_code)

            if raw_df.empty:
                return pd.DataFrame(columns=columns) if columns else raw_df

            df = self._map_fields(raw_df, stock_code)
            df = self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_belong_board",
                params={"stock_code": stock_code},
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
                endpoint="get_belong_board",
                params={"stock_code": stock_code},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            self.logger.error(f"Failed to fetch belong board data for {stock_code}: {e}")
            return pd.DataFrame()

    def _map_fields(self, df: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        """Map efinance fields to standard field names."""
        df = df.copy()

        rename_cols = {}
        for cn_name, en_name in BELONG_BOARD_FIELD_MAP.items():
            if cn_name in df.columns:
                rename_cols[cn_name] = en_name

        if rename_cols:
            df = df.rename(columns=rename_cols)

        if "stock_code" not in df.columns:
            df["stock_code"] = stock_code

        return df


EfinanceBoard = EfinanceBoardProvider
