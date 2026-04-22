from ..core.base import BaseProvider
import pandas as pd
from .base import NorthDailyFactory


@NorthDailyFactory.register("eastmoney")
class EastMoneyNorthDailyProvider(BaseProvider):
    def get_source_name(self) -> str:
        return "eastmoney"

    def get_north_daily(self, date: str = "") -> dict:
        """获取北向单日汇总"""
        df = self.akshare_adapter.call("stock_hsgt_north_net_flow_in_em")
        if df.empty:
            return {"net_inflow": 0, "inflow": 0, "outflow": 0}

        # 取最新或指定日期
        if date:
            date_col = "日期" if "日期" in df.columns else "date"
            if date_col in df.columns:
                df = df[df[date_col] == date]

        if df.empty:
            row = df.iloc[-1]
        else:
            row = df.iloc[0]

        return {
            "net_inflow": float(row.get("当日净流入", row.get("net_flow", 0))),
            "inflow": float(row.get("当日买入", row.get("inflow", 0))),
            "outflow": float(row.get("当日卖出", row.get("outflow", 0))),
        }
