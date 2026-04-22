from typing import Any
import pandas as pd
from ..core.factory import api_endpoint
from .base import NorthDailyFactory
from . import akshare as akshare_provider


@api_endpoint(NorthDailyFactory)
def get_north_daily(
    date: str = "",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> dict:
    """获取北向资金单日汇总

    Args:
        date: 查询日期，默认最新

    Returns:
        dict: 包含 net_inflow, inflow, outflow 等字段
    """
    pass


def get_macro_data(
    indicator: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """通用宏观数据查询

    Args:
        indicator: 指标名称 (gdp/cpi/ppi/pmi/m2/interest_rate/exchange_rate)
    """
    from ..providers.macro.akshare_source import AkShareMacroAkShareProvider

    ak_func_map = {
        "gdp": "get_macro_gdp",
        "cpi": "get_macro_cpi",
        "ppi": "get_macro_ppi",
        "pmi": "get_macro_pmi",
        "m2": "get_macro_cpi",  # fallback
        "interest_rate": "get_macro_interest_rate",
        "exchange_rate": "get_macro_exchange_rate",
    }

    func_name = ak_func_map.get(indicator.lower())
    if func_name is None:
        raise ValueError(f"Unknown macro indicator: {indicator}")

    provider = AkShareMacroAkShareProvider()
    method = getattr(provider, func_name)
    return method(start_date=start_date, end_date=end_date)


def get_macro_indicators() -> list[str]:
    """获取所有可用的宏观指标列表"""
    return ["gdp", "cpi", "ppi", "pmi", "m2", "interest_rate", "exchange_rate"]


def get_macro_series(
    indicators: list[str],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: str | None = None,
) -> pd.DataFrame:
    """获取多个宏观指标的时间序列"""
    results = []
    for ind in indicators:
        try:
            df = get_macro_data(ind, start_date=start_date, end_date=end_date, source=source)
            if not df.empty:
                results.append(df)
        except Exception:
            continue

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


__all__ = [
    "get_north_daily",
    "get_macro_data",
    "get_macro_indicators",
    "get_macro_series",
    "NorthDailyFactory",
]
