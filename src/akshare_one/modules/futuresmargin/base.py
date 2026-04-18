from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd


class FuturesMarginProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "futuresmargin"

    def get_contract_info(self, contract_code: str) -> pd.DataFrame:
        return self._execute_api_mapped("get_contract_info", contract_code=contract_code)

    def get_margin_rate(self, contract_code: str) -> pd.DataFrame:
        return self._execute_api_mapped("get_margin_rate", contract_code=contract_code)


class FuturesMarginFactory(BaseFactory[FuturesMarginProvider]):
    _providers: dict[str, type[FuturesMarginProvider]] = {}
