from typing import Any
import pandas as pd
from ..factory_base import api_endpoint
from .base import DividendNextFactory
from . import akshare as akshare_provider


@api_endpoint(DividendNextFactory)
def get_next_dividend(
    symbol: str,
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取下一次分红预测

    返回已公告但尚未执行的分红信息。

    Args:
        symbol: 股票代码

    Returns:
        pd.DataFrame: 下次分红信息，包含:
        - symbol: 股票代码
        - report_date: 报告期
        - plan_date: 预案公告日
        - div_cash: 每股现金分红(元)
        - bonus_shares: 送股比例
        - transfer_shares: 转增比例
        - ex_date: 除权除息日
        - status: 状态(已公告/已实施)
    """
    pass


def get_lof_daily_with_fallback(
    symbol: str,
    start: str,
    end: str,
    prefer_nav: bool = False,
) -> pd.DataFrame:
    """获取LOF基金日线数据（带回退逻辑）

    优先获取场内交易行情，如果不可用则回退到净值数据。

    Args:
        symbol: LOF基金代码
        start: 开始日期
        end: 结束日期
        prefer_nav: 是否优先使用净值数据

    Returns:
        pd.DataFrame: LOF日线数据
    """
    from ..lof import get_lof_hist_data
    from ..lof import get_lof_nav

    if not prefer_nav:
        try:
            df = get_lof_hist_data(symbol, start_date=start, end_date=end)
            if not df.empty:
                return df
        except Exception:
            pass

    # 回退到净值数据
    return get_lof_nav(symbol, start_date=start, end_date=end)


__all__ = ["get_next_dividend", "get_lof_daily_with_fallback", "DividendNextFactory"]
