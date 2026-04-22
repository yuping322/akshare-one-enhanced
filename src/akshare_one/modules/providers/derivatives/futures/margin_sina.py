"""
Futures margin data provider using Sina data source.
"""

import pandas as pd

from .margin import FuturesMarginFactory, FuturesMarginProvider


@FuturesMarginFactory.register("sina")
class SinaFuturesMarginProvider(FuturesMarginProvider):
    """Futures margin data provider using Sina."""

    def get_source_name(self) -> str:
        return "sina"

    def get_margin_rate(self, contract_code: str) -> pd.DataFrame:
        """Get margin rate."""
        return self.akshare_adapter.call("futures_margin_sina")

    def get_contract_info(self, contract_code: str) -> pd.DataFrame:
        """Get contract information."""
        exchange = self._infer_exchange(contract_code)
        func_name = f"futures_contract_info_{exchange}"
        return self.akshare_adapter.call(func_name)

    def _infer_exchange(self, contract_code: str) -> str:
        """Infer exchange from contract code."""
        code = contract_code.upper()
        if code.startswith(("IF", "IC", "IH", "IM", "T", "TF", "TS")):
            return "cffex"
        elif code.startswith(("CU", "AL", "ZN", "PB", "NI", "SN", "AU", "AG", "RB", "HC", "FU", "BU", "SP")):
            return "shfe"
        elif code.startswith(("I", "J", "JM", "M", "Y", "P", "C", "CS", "L", "V", "PP", "EG", "PG", "JD", "EB", "LH")):
            return "dce"
        else:
            return "czce"
