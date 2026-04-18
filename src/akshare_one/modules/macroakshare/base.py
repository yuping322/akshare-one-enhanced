from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd


class MacroAkShareProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "macroakshare"

    def get_macro_gdp(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_macro_gdp", start_date=start_date, end_date=end_date)

    def get_macro_cpi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_macro_cpi", start_date=start_date, end_date=end_date)

    def get_macro_ppi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_macro_ppi", start_date=start_date, end_date=end_date)

    def get_macro_pmi(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_macro_pmi", start_date=start_date, end_date=end_date)

    def get_macro_interest_rate(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_macro_interest_rate", start_date=start_date, end_date=end_date)

    def get_macro_exchange_rate(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_macro_exchange_rate", start_date=start_date, end_date=end_date)


class MacroAkShareFactory(BaseFactory[MacroAkShareProvider]):
    _providers: dict[str, type[MacroAkShareProvider]] = {}
