import pandas as pd

from ......logging_config import get_logger
from .....core.cache import cache
from .base import InfoDataFactory, InfoDataProvider

try:
    import efinance as ef

    EFINANCE_AVAILABLE = True
except ImportError:
    EFINANCE_AVAILABLE = False


@InfoDataFactory.register("efinance")
class EfinanceInfoProvider(InfoDataProvider):
    """Efinance stock basic info provider"""

    def __init__(self, symbol: str, **kwargs):
        super().__init__(symbol, **kwargs)
        self.logger = get_logger(__name__)

        if not EFINANCE_AVAILABLE:
            raise ImportError("efinance is not installed. Please install it using: pip install efinance")

    def get_source_name(self) -> str:
        return "efinance"

    _basic_info_rename_map = {
        "股票代码": "symbol",
        "股票名称": "name",
        "总市值": "market_cap",
        "流通市值": "float_market_cap",
        "行业": "industry",
        "上市时间": "list_date",
    }

    @cache(
        "info_cache",
        key=lambda self, **kwargs: f"efinance_base_info_{self.symbol}",
    )
    def get_basic_info(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Get basic stock information"""
        try:
            df = ef.stock.get_base_info(self.symbol)
            return self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch base info for {self.symbol}: {e}")
            return pd.DataFrame()

    @cache(
        "info_cache",
        key=lambda self, **kwargs: f"efinance_quote_snapshot_{self.symbol}",
    )
    def get_quote_snapshot(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Get stock quote snapshot"""
        try:
            df = ef.stock.get_quote_snapshot(self.symbol)
            return self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch quote snapshot for {self.symbol}: {e}")
            return pd.DataFrame()

    @cache(
        "info_cache",
        key=lambda self, **kwargs: f"efinance_latest_quote_{self.symbol}",
    )
    def get_latest_quote(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Get latest stock quote"""
        try:
            df = ef.stock.get_latest_quote(self.symbol)
            return self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch latest quote for {self.symbol}: {e}")
            return pd.DataFrame()


EfinanceInfo = EfinanceInfoProvider
