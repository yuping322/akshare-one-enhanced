"""基金持仓 (Fund Portfolio) data module."""

from typing import Any

import pandas as pd

from ..core.factory import api_endpoint
from .base import FundPortfolioFactory
from . import akshare as akshare_provider


@api_endpoint(FundPortfolioFactory)
def get_fund_portfolio(
    fund_code: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取基金持仓明细

    Args:
        fund_code: 基金代码
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        pd.DataFrame: 基金持仓数据，包含字段:
        - fund_code: 基金代码
        - stock_code: 股票代码
        - stock_name: 股票名称
        - holding_shares: 持仓股数
        - holding_value: 持仓市值
        - weight: 占净值比例(%)
        - report_date: 报告期
    """
    pass


@api_endpoint(FundPortfolioFactory)
def get_fund_portfolio_all(
    date: str = "",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取所有基金持仓汇总"""
    pass


__all__ = ["get_fund_portfolio", "get_fund_portfolio_all", "FundPortfolioFactory"]
