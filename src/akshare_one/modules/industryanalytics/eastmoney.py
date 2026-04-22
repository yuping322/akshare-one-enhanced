import pandas as pd

from .base import IndustryAnalyticsFactory, IndustryAnalyticsProvider


@IndustryAnalyticsFactory.register("eastmoney")
class EastMoneyIndustryAnalyticsProvider(IndustryAnalyticsProvider):
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
        return self._execute_api_mapped("get_stock_industry", symbol=symbol)

    def get_industry_performance(self, date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_industry_performance")

    def get_concept_performance(self, date: str = "") -> pd.DataFrame:
        return self._execute_api_mapped("get_concept_performance")

    def search_concept(self, keyword: str) -> pd.DataFrame:
        df = self._execute_api_mapped("search_concept")
        if not df.empty:
            for col in ["板块名称", "name"]:
                if col in df.columns:
                    return df[df[col].str.contains(keyword, na=False)]
        return df

    def get_all_concept_stocks(self) -> pd.DataFrame:
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
        return self._execute_api_mapped("get_all_industries")
