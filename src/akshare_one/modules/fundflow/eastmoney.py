"""
Eastmoney fund flow data provider.

This module implements the fund flow data provider using Eastmoney as the data source.
"""

import pandas as pd

from .base import FundFlowProvider, FundFlowFactory


@FundFlowFactory.register("eastmoney")
class EastmoneyFundFlowProvider(FundFlowProvider):
    _API_MAP = {
        "get_industry_list": {
            "ak_func": "stock_board_industry_name_em",
        },
        "get_industry_constituents": {
            "ak_func": "stock_board_industry_cons_em",
            "params": {"symbol": "industry_code"},
        },
        "get_concept_list": {
            "ak_func": "stock_board_concept_name_em",
        },
        "get_concept_constituents": {
            "ak_func": "stock_board_concept_cons_em",
            "params": {"symbol": "concept_code"},
        },
        "get_main_fund_flow_rank": {
            "ak_func": "stock_individual_fund_flow_rank",
            "params": {"indicator": "indicator_raw"},
        },
    }

    def get_source_name(self) -> str:
        return "eastmoney"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_stock_fund_flow(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """Get individual stock fund flow data from Eastmoney."""
        self.validate_symbol(symbol)
        self.validate_date_range(start_date, end_date)
        
        import akshare as ak
        market = "sh" if symbol.startswith("6") else "sz"
        raw_df = ak.stock_individual_fund_flow(stock=symbol, market=market)
        
        # 使用 standardize_and_filter 自动处理
        df = self.standardize_and_filter(raw_df, "eastmoney", **kwargs)
        if not df.empty:
            df["symbol"] = symbol
            # 简单日期过滤
            if "date" in df.columns:
                df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        return df

    def get_sector_fund_flow(self, sector_type: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """Get sector fund flow data from Eastmoney."""
        if sector_type not in ["industry", "concept"]:
            raise ValueError(f"Invalid sector_type: {sector_type}")
        
        import akshare as ak
        ak_sector = "行业资金流" if sector_type == "industry" else "概念资金流"
        raw_df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type=ak_sector)
        
        df = self.standardize_and_filter(raw_df, "eastmoney", **kwargs)
        if not df.empty:
            df["sector_type"] = sector_type
            # akshare 这里没日期，手动加一个
            from datetime import datetime
            df["date"] = datetime.now().strftime("%Y-%m-%d")
        return df

    def get_main_fund_flow_rank(self, date: str, indicator: str, **kwargs) -> pd.DataFrame:
        """Get main fund flow ranking from Eastmoney."""
        self.validate_date(date)
        # 简单转换参数名并调用映射方法
        kwargs["indicator_raw"] = "今日" # 目前 akshare 主要是获取当日排名
        return self._execute_api_mapped("get_main_fund_flow_rank", **kwargs)
