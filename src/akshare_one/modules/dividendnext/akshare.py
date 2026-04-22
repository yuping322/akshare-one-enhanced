from ..base import BaseProvider
import pandas as pd
from .base import DividendNextFactory


@DividendNextFactory.register("eastmoney")
class EastMoneyDividendNextProvider(BaseProvider):
    def get_source_name(self) -> str:
        return "eastmoney"

    def get_next_dividend(self, symbol: str) -> pd.DataFrame:
        """获取下次分红预测"""
        # 获取历史分红
        df = self.akshare_adapter.call("stock_fhps_em", symbol=symbol)
        if df.empty:
            return df

        # 过滤未实施的分红
        status_col = "实施方案" if "实施方案" in df.columns else "status"
        if status_col in df.columns:
            df = df[df[status_col].str.contains("预案|提议|未实施", na=False)]

        return df
