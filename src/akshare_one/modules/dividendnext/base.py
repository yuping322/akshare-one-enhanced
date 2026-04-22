from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd


class DividendNextProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "dividendnext"

    def get_next_dividend(self, symbol: str) -> pd.DataFrame:
        return self._execute_api_mapped("get_next_dividend", symbol=symbol)


class DividendNextFactory(BaseFactory[DividendNextProvider]):
    _providers: dict[str, type[DividendNextProvider]] = {}
