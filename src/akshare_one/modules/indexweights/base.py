from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd


class IndexWeightsProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "indexweights"

    def get_index_weights(self, index_code: str, date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_index_weights", index_code=index_code, date=date)

    def get_index_weights_history(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        return self._execute_api_mapped(
            "get_index_weights_history", index_code=index_code, start_date=start_date, end_date=end_date
        )

    def get_index_info(self, index_code: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_index_info", index_code=index_code)


class IndexWeightsFactory(BaseFactory[IndexWeightsProvider]):
    _providers: dict[str, type[IndexWeightsProvider]] = {}
