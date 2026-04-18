from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd
from typing import List, Dict


class IndustryAnalyticsProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "industryanalytics"

    def get_stock_industry(self, symbol: str) -> pd.DataFrame:
        return self._execute_api_mapped("get_stock_industry", symbol=symbol)

    def get_industry_performance(self, date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_industry_performance", date=date)

    def get_concept_performance(self, date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_concept_performance", date=date)

    def search_concept(self, keyword: str) -> pd.DataFrame:
        return self._execute_api_mapped("search_concept", keyword=keyword)

    def get_all_concept_stocks(self) -> pd.DataFrame:
        return self._execute_api_mapped("get_all_concept_stocks")

    def get_all_industries(self, level: int = 1) -> pd.DataFrame:
        return self._execute_api_mapped("get_all_industries", level=level)


class IndustryAnalyticsFactory(BaseFactory[IndustryAnalyticsProvider]):
    _providers: dict[str, type[IndustryAnalyticsProvider]] = {}
