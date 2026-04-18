import pandas as pd

from ......logging_config import get_logger
from .base import IPOFactory, IPOProvider

try:
    import efinance as ef

    EFINANCE_AVAILABLE = True
except ImportError:
    EFINANCE_AVAILABLE = False


@IPOFactory.register("efinance")
class EfinanceIPOProvider(IPOProvider):
    """Efinance IPO data provider"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = get_logger(__name__)

        if not EFINANCE_AVAILABLE:
            raise ImportError("efinance is not installed. Please install it using: pip install efinance")

    def get_source_name(self) -> str:
        return "efinance"

    def fetch_data(self) -> pd.DataFrame:
        return self.get_latest_ipo_info()

    def get_new_stocks(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """Get newly listed stocks"""
        try:
            df = ef.stock.get_latest_ipo_info()
            return self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch new stocks: {e}")
            return pd.DataFrame()

    def get_ipo_info(
        self,
        columns: list | None = None,
        row_filter: dict | None = None,
    ) -> pd.DataFrame:
        """Get IPO information"""
        try:
            df = ef.stock.get_latest_ipo_info()
            return self.standardize_and_filter(df, "efinance", columns=columns, row_filter=row_filter)
        except Exception as e:
            self.logger.error(f"Failed to fetch IPO info: {e}")
            return pd.DataFrame()
