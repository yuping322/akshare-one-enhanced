from ..base import BaseProvider
import pandas as pd
from .base import MacroAkShareFactory


@MacroAkShareFactory.register("akshare")
class AkShareMacroAkShareProvider(BaseProvider):
    def get_source_name(self) -> str:
        return "akshare"

    def get_data_type(self) -> str:
        return "macroakshare"

    def get_macro_gdp(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_gdp")

    def get_macro_cpi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_cpi")

    def get_macro_ppi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_ppi")

    def get_macro_pmi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_pmi")

    def get_macro_interest_rate(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_interest_rate")

    def get_macro_exchange_rate(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self.akshare_adapter.call("macro_china_exchange_rate")
