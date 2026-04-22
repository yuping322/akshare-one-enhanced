import pandas as pd

from .base import ShareChangeDepthFactory, ShareChangeDepthProvider


@ShareChangeDepthFactory.register("eastmoney")
class EastMoneyShareChangeDepthProvider(ShareChangeDepthProvider):
    def get_source_name(self) -> str:
        return "eastmoney"

    def get_freeze_info(self, symbol: str) -> pd.DataFrame:
        return self.akshare_adapter.call("stock_gdfx_freeze_holding_detail_em", symbol=symbol)

    def get_capital_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("stock_zgb_change_em", symbol=symbol)

    def get_topholder_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("stock_gdfx_holding_change_em", symbol=symbol)

    def get_major_holder_trade(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("stock_gdfx_holding_analyse_em", symbol=symbol)
