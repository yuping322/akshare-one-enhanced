"""
Efinance performance data provider.
"""

import pandas as pd

from ......logging_config import get_logger
from .....core.cache import cache
from .base import PerformanceFactory, PerformanceProvider

try:
    import efinance as ef

    EFINANCE_AVAILABLE = True
except ImportError:
    EFINANCE_AVAILABLE = False


@PerformanceFactory.register("efinance")
class EfinancePerformanceProvider(PerformanceProvider):
    """Efinance performance data provider"""

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
        "performance_cache",
        key=lambda self, date, **kwargs: f"efinance_all_company_performance_{date}",
    )
    def get_all_company_performance(self, date: str, **kwargs) -> pd.DataFrame:
        """
        Get all company performance data for a specific date.

        Args:
            date: Report date (e.g., '20231231', '2023-12-31')

        Returns:
            DataFrame with quarterly performance data for all companies
        """
        try:
            formatted_date = date.replace("-", "")
            df = ef.stock.get_all_company_performance(date=formatted_date)
            if df.empty:
                return pd.DataFrame()

            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "报告期": "report_period",
                    "净利润": "net_profit",
                    "净利润同比增长": "net_profit_yoy_growth",
                    "营业收入": "revenue",
                    "营业收入同比增长": "revenue_yoy_growth",
                    "每股收益": "eps",
                    "净资产收益率": "roe",
                }
            )

            cols = [
                "symbol",
                "report_period",
                "net_profit",
                "net_profit_yoy_growth",
                "revenue",
                "revenue_yoy_growth",
                "eps",
                "roe",
            ]
            return df[[c for c in cols if c in df.columns]]
        except Exception as e:
            self.logger.error(f"Failed to fetch all company performance for {date}: {e}")
            return pd.DataFrame()


EfinancePerformance = EfinancePerformanceProvider
