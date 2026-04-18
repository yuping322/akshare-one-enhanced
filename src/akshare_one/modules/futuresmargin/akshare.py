from ..base import BaseProvider
import pandas as pd
from .base import FuturesMarginFactory, FuturesMarginProvider


@FuturesMarginFactory.register("akshare")
class AkShareFuturesMarginProvider(FuturesMarginProvider):
    def get_source_name(self) -> str:
        return "akshare"

    def get_contract_info(self, contract_code: str) -> pd.DataFrame:
        """获取合约信息 - ak.futures_contract_info_shfe/dce/czce/cffex"""
        exchange = self._infer_exchange(contract_code)
        func_name = f"futures_contract_info_{exchange}"
        return self.akshare_adapter.call(func_name)

    def get_margin_rate(self, contract_code: str) -> pd.DataFrame:
        """获取保证金率 - ak.futures_margin_sina"""
        return self.akshare_adapter.call("futures_margin_sina")

    def _infer_exchange(self, contract_code: str) -> str:
        """根据合约代码推断交易所"""
        code = contract_code.upper()
        if code.startswith(("IF", "IC", "IH", "IM", "T", "TF", "TS")):
            return "cffex"
        elif code.startswith(("CU", "AL", "ZN", "PB", "NI", "SN", "AU", "AG", "RB", "HC", "FU", "BU", "SP")):
            return "shfe"
        elif code.startswith(("I", "J", "JM", "M", "Y", "P", "C", "CS", "L", "V", "PP", "EG", "PG", "JD", "EB", "LH")):
            return "dce"
        else:
            return "czce"
