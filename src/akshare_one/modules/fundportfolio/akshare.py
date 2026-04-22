"""
AkShare fund portfolio data providers.

This module implements fund portfolio data providers using AkShare and Tushare as data sources.
"""

import pandas as pd

from ..core.base import BaseProvider
from .base import FundPortfolioFactory


@FundPortfolioFactory.register("eastmoney")
class EastMoneyFundPortfolioProvider(BaseProvider):
    """
    Fund portfolio provider using AkShare (eastmoney) as the data source.
    """

    def get_source_name(self) -> str:
        return "eastmoney"

    def get_fund_portfolio(
        self,
        fund_code: str,
        start_date: str = "",
        end_date: str = "",
        **kwargs,
    ) -> pd.DataFrame:
        """
        获取基金持仓 - ak.fund_portfolio_hold_em

        Args:
            fund_code: 基金代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 基金持仓数据
        """
        return self.akshare_adapter.call("fund_portfolio_hold_em", symbol=fund_code)

    def get_fund_portfolio_all(
        self,
        date: str = "",
        **kwargs,
    ) -> pd.DataFrame:
        """
        获取所有基金持仓汇总

        Args:
            date: 报告期

        Returns:
            pd.DataFrame: 所有基金持仓汇总数据
        """
        return self.akshare_adapter.call("fund_portfolio_hold_em", symbol="all")


@FundPortfolioFactory.register("tushare")
class TushareFundPortfolioProvider(BaseProvider):
    """
    Fund portfolio provider using Tushare as the data source.
    """

    def get_source_name(self) -> str:
        return "tushare"

    def get_fund_portfolio(
        self,
        fund_code: str,
        start_date: str = "",
        end_date: str = "",
        **kwargs,
    ) -> pd.DataFrame:
        """
        获取基金持仓 - tushare fund_portfolio

        Args:
            fund_code: 基金代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 基金持仓数据
        """
        from ...tushare_client import get_tushare_client

        client = get_tushare_client()
        return client.query("fund_portfolio", ts_code=fund_code, start_date=start_date, end_date=end_date)

    def get_fund_portfolio_all(
        self,
        date: str = "",
        **kwargs,
    ) -> pd.DataFrame:
        """
        获取所有基金持仓汇总

        Args:
            date: 报告期

        Returns:
            pd.DataFrame: 所有基金持仓汇总数据
        """
        from ...tushare_client import get_tushare_client

        client = get_tushare_client()
        return client.query("fund_portfolio", trade_date=date)
