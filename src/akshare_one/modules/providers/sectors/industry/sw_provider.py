"""
src/akshare_one/modules/industry/sw_provider.py
Shenwan (SW) index-based industry data provider.
"""

import akshare as ak
import pandas as pd

from .....constants import SYMBOL_ZFILL_WIDTH
from .base import IndustryFactory, IndustryProvider

SW_LEVEL1_CODES = {
    "农林牧渔": "801010",
    "采掘": "801020",
    "化工": "801030",
    "钢铁": "801040",
    "有色金属": "801050",
    "电子": "801080",
    "家用电器": "801110",
    "食品饮料": "801120",
    "纺织服装": "801130",
    "轻工制造": "801140",
    "医药生物": "801150",
    "公用事业": "801160",
    "交通运输": "801170",
    "房地产": "801180",
    "商业贸易": "801190",
    "休闲服务": "801200",
    "综合": "801210",
    "建筑材料": "801710",
    "建筑装饰": "801720",
    "电气设备": "801730",
    "国防军工": "801740",
    "计算机": "801750",
    "传媒": "801760",
    "通信": "801770",
    "银行": "801780",
    "非银金融": "801790",
    "汽车": "801880",
    "机械设备": "801890",
}


@IndustryFactory.register("sw")
class SWIndustryProvider(IndustryProvider):
    def get_source_name(self) -> str:
        return "sw"

    def get_industry_list(self) -> pd.DataFrame:
        return pd.DataFrame(
            [{"industry_code": v, "industry_name": k, "source": "sw"} for k, v in SW_LEVEL1_CODES.items()]
        )

    def get_industry_stocks(self, industry: str) -> pd.DataFrame:
        """Fetch industry constituents using SW index code."""
        code = SW_LEVEL1_CODES.get(industry, industry)
        try:
            df = ak.sw_index_cons(index_code=code)
            if df.empty:
                return pd.DataFrame()
            df = df.rename(columns={"成分券代码": "symbol", "成分券名称": "name"})
            return df[["symbol", "name"]]
        except Exception:
            return pd.DataFrame()

    def get_industry_stocks_jq(self, industry_name: str) -> list[str]:
        """JQ-compatible stock symbols for a given Shenwan industry."""
        df = self.get_industry_stocks(industry_name)
        if df.empty:
            return []
        stocks = []
        for c in df["symbol"]:
            stocks.append(
                f"{str(c).zfill(SYMBOL_ZFILL_WIDTH)}.XSHG"
                if str(c).startswith("6")
                else f"{str(c).zfill(SYMBOL_ZFILL_WIDTH)}.XSHE"
            )
        return stocks

    def get_industry_daily(self, industry_name: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        code = SW_LEVEL1_CODES.get(industry_name, industry_name)
        try:
            df = ak.sw_index_daily(index_code=code)
            df = df.rename(columns={"日期": "date", "收盘": "close"})
            df["date"] = pd.to_datetime(df["date"])
            if start_date:
                df = df[df["date"] >= start_date]
            if end_date:
                df = df[df["date"] <= end_date]
            return df
        except Exception:
            return pd.DataFrame()
