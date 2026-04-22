from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd


class IndustryPerformanceProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "industryperformance"

    def get_industry_stocks_performance(self, industry_name: str) -> pd.DataFrame:
        return self._execute_api_mapped("get_industry_stocks_performance", industry_name=industry_name)

    def get_all_industry_mapping(self, level: int = 1) -> pd.DataFrame:
        return self._execute_api_mapped("get_all_industry_mapping", level=level)

    def get_market_breadth(self, date: str = "", method: str = "method2") -> float:
        return self._execute_api_mapped("get_market_breadth", date=date, method=method)


class IndustryPerformanceFactory(BaseFactory[IndustryPerformanceProvider]):
    _providers: dict[str, type[IndustryPerformanceProvider]] = {}
