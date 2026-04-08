"""
Efinance block deal data provider.

This module implements the block deal data provider using efinance as the data source.
"""

import time

import pandas as pd

from ...logging_config import get_logger, log_api_request
from ..cache import cache
from .base import BlockDealFactory, BlockDealProvider

try:
    import efinance as ef

    EFINANCE_AVAILABLE = True
except ImportError:
    EFINANCE_AVAILABLE = False


@BlockDealFactory.register("efinance")
class EfinanceBlockDealProvider(BlockDealProvider):
    """Block deal data provider using efinance as the data source."""

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
        "blockdeal_cache",
        key=lambda self, stock_code, max_count=100: f"efinance_deal_detail_{stock_code}_{max_count}",
    )
    def get_deal_detail(self, stock_code: str, max_count: int = 100) -> pd.DataFrame:
        """
        Get stock deal detail (成交明细) from efinance.

        Args:
            stock_code: Stock code (e.g., '600000')
            max_count: Maximum number of records to fetch

        Returns:
            pd.DataFrame: Deal detail data with standardized fields
        """
        start_time = time.time()

        try:
            self.logger.debug(
                "Fetching deal detail",
                extra={
                    "context": {
                        "source": "efinance",
                        "stock_code": stock_code,
                        "max_count": max_count,
                        "action": "fetch_start",
                    }
                },
            )

            raw_df = ef.stock.get_deal_detail(stock_code, max_count)

            if raw_df.empty:
                return self.create_empty_dataframe(["time", "price", "volume", "amount", "nature"])

            df = self._map_fields(raw_df)

            duration_ms = (time.time() - start_time) * 1000

            log_api_request(
                logger=self.logger,
                source="efinance",
                endpoint="get_deal_detail",
                params={"stock_code": stock_code, "max_count": max_count},
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
                endpoint="get_deal_detail",
                params={"stock_code": stock_code, "max_count": max_count},
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            )

            self.logger.error(f"Failed to fetch deal detail: {e}", exc_info=True)
            return self.create_empty_dataframe(["time", "price", "volume", "amount", "nature"])

    def _map_fields(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Map efinance Chinese field names to standard English names."""
        column_map = {
            "时间": "time",
            "价格": "price",
            "成交量": "volume",
            "成交额": "amount",
            "性质": "nature",
            "股票名称": "name",
            "股票代码": "symbol",
            "昨收": "prev_close",
            "成交价": "deal_price",
            "单数": "order_count",
        }

        df = raw_df.copy()

        rename_cols = {}
        for cn_name, en_name in column_map.items():
            if cn_name in df.columns:
                rename_cols[cn_name] = en_name

        if rename_cols:
            df = df.rename(columns=rename_cols)

        numeric_cols = ["price", "volume", "amount", "prev_close", "deal_price", "order_count"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def get_block_deal(self, symbol: str | None, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get block deal transaction details from efinance.

        Note: efinance doesn't support block deal data, this method raises NotImplementedError.
        """
        raise NotImplementedError("efinance does not support block deal data. Use 'eastmoney' provider instead.")

    def get_block_deal_summary(self, start_date: str, end_date: str, group_by: str) -> pd.DataFrame:
        """
        Get block deal summary statistics from efinance.

        Note: efinance doesn't support block deal summary data, this method raises NotImplementedError.
        """
        raise NotImplementedError("efinance does not support block deal summary. Use 'eastmoney' provider instead.")
