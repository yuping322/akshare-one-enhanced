import pandas as pd

from .base import ShareChangeDepthFactory, ShareChangeDepthProvider


@ShareChangeDepthFactory.register("akshare")
class AkShareShareChangeDepthProvider(ShareChangeDepthProvider):
    def get_source_name(self) -> str:
        return "akshare"

    def get_freeze_info(self, symbol: str) -> pd.DataFrame:
        """获取股份冻结 - ak.stock_gdfx_freeze_holding_detail_em"""
        return self.akshare_adapter.call("stock_gdfx_freeze_holding_detail_em", symbol=symbol)

    def get_capital_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """获取股本变动 - ak.stock_zgb_change_em"""
        return self.akshare_adapter.call("stock_zgb_change_em", symbol=symbol)

    def get_topholder_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """获取十大股东变动 - ak.stock_gdfx_holding_change_em"""
        return self.akshare_adapter.call("stock_gdfx_holding_change_em", symbol=symbol)

    def get_major_holder_trade(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """获取大股东交易 - ak.stock_gdfx_holding_analyse_em"""
        return self.akshare_adapter.call("stock_gdfx_holding_analyse_em", symbol=symbol)
