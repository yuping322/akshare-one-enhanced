import pandas as pd

from ..base import BaseProvider
from .base import IndustryPerformanceFactory


@IndustryPerformanceFactory.register("eastmoney")
class EastMoneyIndustryPerformanceProvider(BaseProvider):
    def get_source_name(self) -> str:
        return "eastmoney"

    def get_industry_stocks_performance(self, industry_name: str) -> pd.DataFrame:
        from ..providers.sectors.industry import IndustryFactory

        stocks = IndustryFactory.get_provider("eastmoney").get_industry_stocks(industry_name)
        if not stocks:
            return pd.DataFrame()

        df = self.akshare_adapter.call("stock_zh_a_spot_em")
        if df.empty:
            return pd.DataFrame()

        code_col = "代码" if "代码" in df.columns else "symbol"
        if code_col in df.columns:
            df = df[df[code_col].isin(stocks)]

        return df

    def get_all_industry_mapping(self, level: int = 1) -> pd.DataFrame:
        industries = self.akshare_adapter.call("stock_board_industry_name_em")
        if industries.empty:
            return pd.DataFrame()

        results = []
        for _, row in industries.iterrows():
            industry_name = row.get("板块名称", "")
            industry_code = row.get("板块代码", "")
            if not industry_name:
                continue

            try:
                stocks = self.akshare_adapter.call("stock_board_industry_cons_em", symbol=industry_code)
                if not stocks.empty:
                    code_col = "代码" if "代码" in stocks.columns else "symbol"
                    if code_col in stocks.columns:
                        stocks["industry"] = industry_name
                        stocks["industry_code"] = industry_code
                        results.append(stocks[[code_col, "名称", "industry", "industry_code"]])
            except Exception:
                continue

        if results:
            df = pd.concat(results, ignore_index=True)
            df.columns = ["symbol", "name", "industry", "industry_code"]
            return df
        return pd.DataFrame()

    def get_market_breadth(self, date: str = "", method: str = "method2") -> float:
        df = self.akshare_adapter.call("stock_zh_a_spot_em")
        if df.empty:
            return 0.5

        change_col = "涨跌幅" if "涨跌幅" in df.columns else "change_pct"
        if change_col not in df.columns:
            return 0.5

        total = len(df)
        up_count = len(df[df[change_col] > 0]) if method == "method2" else len(df[df[change_col] > 2.0])

        return round(up_count / total, 4) if total > 0 else 0.5
