import akshare as ak
import pandas as pd

from ..cache import cache
from .base import InfoDataFactory, InfoDataProvider


@InfoDataFactory.register("eastmoney")
class EastmoneyInfoProvider(InfoDataProvider):
    """Eastmoney stock basic info provider"""

    def get_source_name(self) -> str:
        return "eastmoney"

    _basic_info_rename_map = {
        "最新": "price",
        "股票代码": "symbol",
        "股票简称": "name",
        "总股本": "total_shares",
        "流通股": "float_shares",
        "总市值": "total_market_cap",
        "流通市值": "float_market_cap",
        "行业": "industry",
        "上市时间": "listing_date",
    }

    @cache(
        "info_cache",
        key=lambda self: f"eastmoney_{self.symbol}",
    )
    def get_basic_info(self, columns: list | None = None, row_filter: dict | None = None) -> pd.DataFrame:
        """获取东方财富个股信息"""
        info_df = ak.stock_individual_info_em(symbol=self.symbol)
        info_df = info_df.set_index("item").T
        info_df.reset_index(drop=True, inplace=True)
        return self.standardize_and_filter(info_df, "eastmoney", columns=columns, row_filter=row_filter)

EastmoneyInfo = EastmoneyInfoProvider
