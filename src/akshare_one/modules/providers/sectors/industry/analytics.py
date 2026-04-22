"""
Industry analytics provider - industry performance and concept analysis.
"""


import pandas as pd

from ....core.base import BaseProvider
from .base import IndustryFactory


class IndustryAnalyticsProvider(BaseProvider):
    """Provider for industry analytics data."""

    def get_data_type(self) -> str:
        return "industryanalytics"

    def get_stock_industry(self, symbol: str) -> pd.DataFrame:
        """Get industry classification for a stock."""
        return self._execute_api_mapped("get_stock_industry", symbol=symbol)

    def get_industry_performance(self, date: str = "") -> pd.DataFrame:
        """Get industry sector performance."""
        return self._execute_api_mapped("get_industry_performance", date=date)

    def get_concept_performance(self, date: str = "") -> pd.DataFrame:
        """Get concept sector performance."""
        return self._execute_api_mapped("get_concept_performance", date=date)

    def search_concept(self, keyword: str) -> pd.DataFrame:
        """Search concept sectors."""
        return self._execute_api_mapped("search_concept", keyword=keyword)

    def get_all_concept_stocks(self) -> pd.DataFrame:
        """Get all concepts and their constituent stocks."""
        return self._execute_api_mapped("get_all_concept_stocks")

    def get_all_industries(self, level: int = 1) -> pd.DataFrame:
        """Get all industry classifications."""
        return self._execute_api_mapped("get_all_industries", level=level)


class IndustryAnalyticsFactory(IndustryFactory):
    """Factory for industry analytics data providers."""

    pass


@IndustryAnalyticsFactory.register("eastmoney")
class EastMoneyIndustryAnalyticsProvider(IndustryAnalyticsProvider):
    """Industry analytics data provider using EastMoney."""

    _API_MAP = {
        "get_stock_industry": {
            "ak_func": "stock_individual_info_em",
            "params": {"symbol": "symbol"},
        },
        "get_industry_performance": {
            "ak_func": "stock_board_industry_name_em",
        },
        "get_concept_performance": {
            "ak_func": "stock_board_concept_name_em",
        },
        "search_concept": {
            "ak_func": "stock_board_concept_name_em",
        },
        "get_all_concept_stocks": {
            "ak_func": "stock_board_concept_name_em",
        },
        "get_all_industries": {
            "ak_func": "stock_board_industry_name_em",
        },
    }

    def get_source_name(self) -> str:
        return "eastmoney"

    def get_stock_industry(self, symbol: str) -> pd.DataFrame:
        """Get stock industry classification."""
        return self._execute_api_mapped("get_stock_industry", symbol=symbol)

    def get_industry_performance(self, date: str = "") -> pd.DataFrame:
        """Get industry sector performance."""
        return self._execute_api_mapped("get_industry_performance")

    def get_concept_performance(self, date: str = "") -> pd.DataFrame:
        """Get concept sector performance."""
        return self._execute_api_mapped("get_concept_performance")

    def search_concept(self, keyword: str) -> pd.DataFrame:
        """Search concept sectors."""
        df = self._execute_api_mapped("search_concept")
        if not df.empty:
            for col in ["板块名称", "name"]:
                if col in df.columns:
                    return df[df[col].str.contains(keyword, na=False)]
        return df

    def get_all_concept_stocks(self) -> pd.DataFrame:
        """Get all concepts and their constituent stocks."""
        concepts = self._execute_api_mapped("get_all_concept_stocks")
        results = []
        if not concepts.empty:
            for _, row in concepts.head(50).iterrows():
                code = row.get("板块代码", row.get("code", ""))
                if code:
                    try:
                        stocks = self.akshare_adapter.call("stock_board_concept_cons_em", symbol=code)
                        if not stocks.empty:
                            results.append(stocks)
                    except Exception:
                        continue
        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()

    def get_all_industries(self, level: int = 1) -> pd.DataFrame:
        """Get all industry classifications."""
        return self._execute_api_mapped("get_all_industries")


def filter_stocks_by_industry(industry_name: str, codes: list[str] | None = None, level: int = 1) -> list[str]:
    """Filter stocks by industry."""
    from . import get_industry_stocks

    industry_stocks = get_industry_stocks(industry_name)
    if codes:
        return [c for c in industry_stocks if c in codes]
    return industry_stocks


def query_industry_sw(symbols: list[str]) -> pd.DataFrame:
    """Batch query Shenwan industry classification."""
    results = []
    for sym in symbols:
        try:
            df = get_stock_industry(sym)
            if not df.empty:
                results.append(df)
        except Exception:
            continue
    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()
