"""
Base provider class for fund portfolio (基金持仓) data.

This module defines the abstract interface for fund portfolio data providers.
"""

import pandas as pd

from ..core.base import BaseProvider
from ..core.factory import BaseFactory


class FundPortfolioProvider(BaseProvider):
    """
    Base class for fund portfolio data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "fundportfolio"

    def get_update_frequency(self) -> str:
        """Fund portfolio data is updated quarterly."""
        return "quarterly"

    def get_delay_minutes(self) -> int:
        """Fund portfolio data has minimal delay."""
        return 0

    def get_fund_portfolio(
        self,
        fund_code: str,
        start_date: str = "",
        end_date: str = "",
        **kwargs,
    ) -> pd.DataFrame:
        """
        获取基金持仓明细

        Args:
            fund_code: 基金代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 基金持仓数据
        """
        return self._execute_api_mapped(
            "get_fund_portfolio",
            fund_code=fund_code,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

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
        return self._execute_api_mapped("get_fund_portfolio_all", date=date, **kwargs)


class FundPortfolioFactory(BaseFactory["FundPortfolioProvider"]):
    """
    Factory class for creating fund portfolio data providers.
    """

    _providers: dict[str, type["FundPortfolioProvider"]] = {}
