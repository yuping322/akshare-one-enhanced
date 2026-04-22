"""Industry sector providers."""

from typing import Any, List, Optional

import pandas as pd

from .analytics import EastMoneyIndustryAnalyticsProvider, IndustryAnalyticsFactory, IndustryAnalyticsProvider
from .base import IndustryFactory, IndustryProvider
from .eastmoney import EastmoneyIndustryProvider
from .lixinger import LixingerIndustryProvider
from .sw_provider import SWIndustryProvider


def get_industry_list(
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Get industry sector list."""
    from .....http_client import apply_data_filter

    if isinstance(source, list) or source is None:
        from .....modules.core.router import MultiSourceRouter

        providers = []
        for s in source or ["eastmoney"]:
            try:
                providers.append((s, IndustryFactory.get_provider(source=s)))
            except Exception:
                pass
        router = MultiSourceRouter(providers)
        df = router.execute("get_industry_list")
    else:
        provider = IndustryFactory.get_provider(source=source)
        df = provider.get_industry_list()

    return apply_data_filter(df, columns, row_filter)


def get_industry_stocks(
    industry: str,
    source: str | list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Get stocks in an industry sector."""
    from .....http_client import apply_data_filter

    if isinstance(source, list) or source is None:
        from .....modules.core.router import MultiSourceRouter

        providers = []
        for s in source or ["eastmoney"]:
            try:
                providers.append((s, IndustryFactory.get_provider(source=s)))
            except Exception:
                pass
        router = MultiSourceRouter(providers)
        df = router.execute("get_industry_stocks", industry)
    else:
        provider = IndustryFactory.get_provider(source=source)
        df = provider.get_industry_stocks(industry)

    return apply_data_filter(df, columns, row_filter)


def get_industry_classify(level: str = "sw_l1") -> pd.DataFrame:
    """Get industry classification list."""
    provider = IndustryFactory.get_provider("eastmoney", industry_name="")
    return provider.get_industry_classify(level=level)


def get_industry_stocks_jq(industry: str) -> list[str]:
    """Get constituent stocks for a given industry (JQ-compatible)."""
    from .....constants import SYMBOL_ZFILL_WIDTH

    df = get_industry_stocks(industry)
    if df is not None and not df.empty and "symbol" in df.columns:
        stocks = df["symbol"].tolist()
        return [
            f"{str(s).zfill(SYMBOL_ZFILL_WIDTH)}.XSHG"
            if str(s).startswith("6")
            else f"{str(s).zfill(SYMBOL_ZFILL_WIDTH)}.XSHE"
            for s in stocks
        ]
    return []


def get_industry_daily(date: str = "", industry: str = "") -> pd.DataFrame:
    """Get industry daily performance."""
    provider = IndustryAnalyticsFactory.get_provider("eastmoney")
    return provider.get_industry_performance(date=date)


def get_market_breadth(date: str = "") -> pd.DataFrame:
    """Get market breadth data."""
    provider = IndustryAnalyticsFactory.get_provider("eastmoney")
    return provider.get_industry_performance(date=date)


__all__ = [
    "IndustryFactory",
    "IndustryProvider",
    "EastmoneyIndustryProvider",
    "LixingerIndustryProvider",
    "SWIndustryProvider",
    "IndustryAnalyticsFactory",
    "IndustryAnalyticsProvider",
    "EastMoneyIndustryAnalyticsProvider",
    "get_industry_list",
    "get_industry_stocks",
    "get_industry_classify",
    "get_industry_stocks_jq",
    "get_industry_daily",
    "get_market_breadth",
]
