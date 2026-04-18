from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd


class ShareChangeDepthProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "sharechangedepth"

    def get_freeze_info(self, symbol: str) -> pd.DataFrame:
        return self._execute_api_mapped("get_freeze_info", symbol=symbol)

    def get_capital_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_capital_change", symbol=symbol, start_date=start_date, end_date=end_date)

    def get_topholder_change(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_topholder_change", symbol=symbol, start_date=start_date, end_date=end_date)

    def get_major_holder_trade(self, symbol: str, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped(
            "get_major_holder_trade", symbol=symbol, start_date=start_date, end_date=end_date
        )


class ShareChangeDepthFactory(BaseFactory[ShareChangeDepthProvider]):
    _providers: dict[str, type[ShareChangeDepthProvider]] = {}
