"""Akshare One - Unified interface for Chinese market data

Provides standardized access to various financial data sources with:
- Consistent symbol formats
- Unified data schemas
- Cleaned and normalized outputs

Example:
    >>> from akshare_one import get_hist_data, get_realtime_data
    >>> # 获取股票历史数据
    >>> df = get_hist_data("600000", interval="day")
    >>> print(df.head())
    >>> # 获取股票实时数据
    >>> df = get_realtime_data(symbol="600000")
"""

from typing import Any, Dict, Literal

import pandas as pd

from .http_client import configure_ssl_verification


def apply_data_filter(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    通用数据过滤方法（行列过滤），用于 LLM Skills 数据筛选。

    Args:
        df: 原始 DataFrame
        columns: 需要保留的列名列表
        row_filter: 行过滤配置字典，支持：
            - top_n: 返回前 N 行
            - sample: 随机采样比例 (0-1)
            - query: pandas query 表达式
            - sort_by: 排序字段
            - ascending: 是否升序排序（默认 False 降序）

    Returns:
        过滤后的 DataFrame
    """
    if df.empty:
        return df

    df = df.copy()

    if row_filter:
        if "sort_by" in row_filter:
            sort_col = row_filter["sort_by"]
            if sort_col in df.columns:
                ascending = row_filter.get("ascending", False)
                df = df.sort_values(by=sort_col, ascending=ascending).reset_index(drop=True)

        if "query" in row_filter:
            try:
                df = df.query(row_filter["query"]).reset_index(drop=True)
            except Exception:
                pass

        if "sample" in row_filter:
            frac = row_filter["sample"]
            if 0 < frac <= 1:
                df = df.sample(frac=frac, random_state=42).reset_index(drop=True)

        if "top_n" in row_filter:
            df = df.head(row_filter["top_n"])

    if columns:
        available_cols = [col for col in columns if col in df.columns]
        if available_cols:
            df = df[available_cols]

    return df


_apply_data_filter = apply_data_filter

from .modules.financial.factory import FinancialDataFactory
from .modules.futures.factory import FuturesDataFactory
from .modules.historical.factory import HistoricalDataFactory
from .modules.info.factory import InfoDataFactory
from .modules.insider.factory import InsiderDataFactory
from .modules.multi_source import (
    ExecutionResult,
    MultiSourceRouter,
    create_financial_router,
    create_historical_router,
    create_realtime_router,
)
from .modules.news.factory import NewsDataFactory
from .modules.options.factory import OptionsDataFactory
from .modules.realtime.factory import RealtimeDataFactory
from .modules.etf.factory import ETFFactory
from .modules.index.factory import IndexFactory
from .modules.bond.factory import BondFactory
from .modules.valuation.factory import ValuationFactory
from .modules.shareholder.factory import ShareholderFactory
from .modules.performance.factory import PerformanceFactory
from .modules.analyst.factory import AnalystFactory
from .modules.sentiment.factory import SentimentFactory
from .modules.concept import ConceptFactory, get_concept_list, get_concept_stocks
from .modules.industry import IndustryFactory, get_industry_list, get_industry_stocks
from .modules.hkus import HKUSFactory, get_hk_stocks, get_us_stocks
from .modules.suspended import SuspendedFactory, get_suspended_stocks
from .modules.st import STFactory, get_st_stocks
from .modules.ipo import IPOFactory, get_new_stocks, get_ipo_info
from .modules.board import BoardFactory, get_kcb_stocks, get_cyb_stocks

__all__ = [
    # 配置
    "configure_ssl_verification",
    # 工具函数
    "apply_data_filter",
    # 多数据源
    "ExecutionResult",
    "MultiSourceRouter",
    "create_historical_router",
    "create_realtime_router",
    "create_financial_router",
    # 基础数据
    "get_basic_info",
    "get_hist_data",
    "get_realtime_data",
    "get_news_data",
    # 财务数据
    "get_balance_sheet",
    "get_income_statement",
    "get_cash_flow",
    "get_financial_metrics",
    # 其他数据
    "get_inner_trade_data",
    "get_futures_hist_data",
    "get_futures_realtime_data",
    "get_futures_main_contracts",
    "get_options_chain",
    "get_options_realtime",
    "get_options_expirations",
    "get_options_hist",
    # ETF/基金数据
    "get_etf_hist_data",
    "get_etf_realtime_data",
    "get_etf_list",
    "get_fund_manager_info",
    "get_fund_rating_data",
    # 指数数据
    "get_index_hist_data",
    "get_index_realtime_data",
    "get_index_list",
    "get_index_constituents",
    # 可转债数据
    "get_bond_list",
    "get_bond_hist_data",
    "get_bond_realtime_data",
    # 估值数据
    "get_stock_valuation",
    "get_market_valuation",
    # 股东数据
    "get_shareholder_changes",
    "get_top_shareholders",
    "get_institution_holdings",
    # 业绩数据
    "get_performance_forecast",
    "get_performance_express",
    # 分析师数据
    "get_analyst_rank",
    "get_research_report",
    # 市场情绪
    "get_hot_rank",
    "get_stock_sentiment",
    # 概念板块
    "get_concept_list",
    "get_concept_stocks",
    # 行业板块
    "get_industry_list",
    "get_industry_stocks",
    # 港美股
    "get_hk_stocks",
    "get_us_stocks",
    # 停复牌
    "get_suspended_stocks",
    # ST股票
    "get_st_stocks",
    # 新股IPO
    "get_new_stocks",
    "get_ipo_info",
    # 科创板/创业板
    "get_kcb_stocks",
    "get_cyb_stocks",
    # 多源API
    "get_basic_info_multi_source",
    "get_hist_data_multi_source",
    "get_realtime_data_multi_source",
    "get_news_data_multi_source",
    "get_inner_trade_data_multi_source",
    "get_financial_data_multi_source",
    "get_financial_metrics_multi_source",
]


def get_basic_info(symbol: str, source: Literal["eastmoney"] = "eastmoney") -> pd.DataFrame:
    """获取股票基础信息

    Args:
        symbol: 股票代码 (e.g. '600000')
        source: 数据源 ('eastmoney')

    Returns:
        pd.DataFrame:
        - price: 最新价
        - symbol: 股票代码
        - name: 股票简称
        - total_shares: 总股本
        - float_shares: 流通股
        - total_market_cap: 总市值
        - float_market_cap: 流通市值
        - industry: 行业
        - listing_date: 上市时间
    """
    provider = InfoDataFactory.get_provider(source, symbol=symbol)
    return provider.get_basic_info()


def get_hist_data(
    symbol: str,
    interval: Literal["minute", "hour", "day", "week", "month", "year"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: Literal["none", "qfq", "hfq"] = "none",
    source: Literal["eastmoney", "eastmoney_direct", "sina"] = "eastmoney_direct",
) -> pd.DataFrame:
    """Get historical market data

    Args:
        symbol: 股票代码 (e.g. '600000')
        interval: 时间间隔 ('minute','hour','day','week','month','year')
        interval_multiplier: 时间间隔倍数 (e.g. 5 for 5 minutes)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        adjust: 复权类型 ('none','qfq','hfq')
        source: 数据源 ('eastmoney', 'eastmoney_direct', 'sina')

    Returns:
        pd.DataFrame:
        - timestamp: 时间戳
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
    """
    kwargs = {
        "symbol": symbol,
        "interval": interval,
        "interval_multiplier": interval_multiplier,
        "start_date": start_date,
        "end_date": end_date,
        "adjust": adjust,
    }
    provider = HistoricalDataFactory.get_provider(source, **kwargs)
    return provider.get_hist_data()


def get_realtime_data(
    symbol: str | None = None,
    source: Literal["eastmoney", "eastmoney_direct", "xueqiu"] = "eastmoney_direct",
) -> pd.DataFrame:
    """Get real-time market quotes

    Args:
        symbol: 股票代码 (如 "600000")
        source: 数据源 ('eastmoney', 'eastmoney_direct', 'xueqiu')

    Returns:
        pd.DataFrame:
        - symbol: 股票代码
        - price: 最新价
        - change: 涨跌额
        - pct_change: 涨跌幅(%)
        - timestamp: 时间戳
        - volume: 成交量(手)
        - amount: 成交额(元)
        - open: 今开
        - high: 最高
        - low: 最低
        - prev_close: 昨收
    """
    provider = RealtimeDataFactory.get_provider(source, symbol=symbol)
    return provider.get_current_data()


def get_news_data(symbol: str, source: Literal["eastmoney"] = "eastmoney") -> pd.DataFrame:
    """获取个股新闻数据

    Args:
        symbol: 股票代码 (如 "300059")
        source: 数据源 ('eastmoney')

    Returns:
        pd.DataFrame:
        - keyword: 关键词
        - title: 新闻标题
        - content: 新闻内容
        - publish_time: 发布时间
        - source: 文章来源
        - url: 新闻链接
    """
    provider = NewsDataFactory.get_provider(source, symbol=symbol)
    return provider.get_news_data()


def get_balance_sheet(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame:
    """获取资产负债表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 资产负债表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_balance_sheet()


def get_income_statement(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame:
    """获取利润表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 利润表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_income_statement()


def get_cash_flow(symbol: str, source: Literal["sina"] = "sina") -> pd.DataFrame:
    """获取现金流量表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 现金流量表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_cash_flow()


def get_financial_metrics(symbol: str, source: Literal["eastmoney_direct"] = "eastmoney_direct") -> pd.DataFrame:
    """获取三大财务报表关键指标

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ('eastmoney_direct')

    Returns:
        pd.DataFrame: 财务关键指标数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    return provider.get_financial_metrics()


def get_inner_trade_data(symbol: str, source: Literal["xueqiu"] = "xueqiu") -> pd.DataFrame:
    """获取雪球内部交易数据

    Args:
        symbol: 股票代码，如"600000"
        source: 数据源 (目前支持 "xueqiu")

    Returns:
        pd.DataFrame: 内部交易数据
    """
    provider = InsiderDataFactory.get_provider(source, symbol=symbol)
    return provider.get_inner_trade_data()


# ==================== Futures API ====================


def get_futures_hist_data(
    symbol: str,
    contract: str = "main",
    interval: Literal["minute", "hour", "day", "week", "month"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期货历史数据

    Args:
        symbol: 期货代码 (e.g., 'AG0' for 白银)
        contract: 合约代码 (默认 'main' 为主力合约，也可指定如 '2602')
        interval: 时间间隔 ('minute', 'hour', 'day', 'week', 'month')
        interval_multiplier: 时间间隔倍数 (e.g. 5 for 5 minutes)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - timestamp: 时间戳
        - symbol: 期货代码
        - contract: 合约代码
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
        - open_interest: 持仓量
        - settlement: 结算价
    """
    kwargs = {
        "symbol": symbol,
        "contract": contract,
        "interval": interval,
        "interval_multiplier": interval_multiplier,
        "start_date": start_date,
        "end_date": end_date,
    }
    provider = FuturesDataFactory.get_historical_provider(source, **kwargs)
    return provider.get_hist_data()


def get_futures_realtime_data(
    symbol: str | None = None,
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期货实时行情数据

    Args:
        symbol: 期货代码 (如 "CF")，为 None 时返回所有期货
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - symbol: 期货代码
        - contract: 合约代码
        - price: 最新价
        - change: 涨跌额
        - pct_change: 涨跌幅(%)
        - timestamp: 时间戳
        - volume: 成交量
        - open_interest: 持仓量
        - open: 今开
        - high: 最高
        - low: 最低
        - prev_settlement: 昨结算
        - settlement: 最新结算价
    """
    provider = FuturesDataFactory.get_realtime_provider(source, symbol=symbol or "")
    if symbol:
        return provider.get_current_data()
    return provider.get_all_quotes()


def get_futures_main_contracts(
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期货主力合约列表

    Args:
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - symbol: 期货代码
        - name: 期货名称
        - contract: 主力合约代码
        - exchange: 交易所
    """
    from .modules.futures.sina import SinaFuturesHistorical

    provider = SinaFuturesHistorical(symbol="")
    return provider.get_main_contracts()


# ==================== Options API ====================


def get_options_chain(
    underlying_symbol: str,
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期权链数据

    Args:
        underlying_symbol: 标的代码 (e.g., '510300' for 300ETF期权)
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - underlying: 标的代码
        - symbol: 期权代码
        - name: 期权名称
        - option_type: 期权类型 (call/put)
        - strike: 行权价
        - expiration: 到期日
        - price: 最新价
        - change: 涨跌额
        - pct_change: 涨跌幅(%)
        - volume: 成交量
        - open_interest: 持仓量
        - implied_volatility: 隐含波动率
    """
    provider = OptionsDataFactory.get_provider(source, underlying_symbol=underlying_symbol)
    return provider.get_options_chain()


def get_options_realtime(
    symbol: str | None = None,
    underlying_symbol: str | None = None,
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期权实时行情数据

    Args:
        symbol: 期权代码 (如 "10004005")
        underlying_symbol: 标的代码 (e.g., '510300' for 300ETF期权)，获取该标的所有期权
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - symbol: 期权代码
        - underlying: 标的代码
        - price: 最新价
        - change: 涨跌额
        - pct_change: 涨跌幅(%)
        - timestamp: 时间戳
        - volume: 成交量
        - open_interest: 持仓量
        - iv: 隐含波动率

    Raises:
        ValueError: 当同时提供或都不提供 symbol 和 underlying_symbol 时
    """
    if symbol is not None and underlying_symbol is not None:
        raise ValueError("Cannot specify both 'symbol' and 'underlying_symbol'. Provide one or the other.")
    if symbol is None and underlying_symbol is None:
        raise ValueError("Must specify either 'symbol' or 'underlying_symbol'.")

    if symbol:
        provider = OptionsDataFactory.get_provider(source, underlying_symbol="")
        return provider.get_options_realtime(symbol)
    else:
        provider = OptionsDataFactory.get_provider(source, underlying_symbol=underlying_symbol)
        return provider.get_options_realtime("")


def get_options_expirations(
    underlying_symbol: str,
    source: Literal["sina"] = "sina",
) -> list[str]:
    """获取期权可用到期日列表

    Args:
        underlying_symbol: 标的代码
        source: 数据源 ('sina')

    Returns:
        list[str]: 可用的到期日列表
    """
    provider = OptionsDataFactory.get_provider(source, underlying_symbol=underlying_symbol)
    return provider.get_options_expirations(underlying_symbol)


def get_options_hist(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["sina"] = "sina",
) -> pd.DataFrame:
    """获取期权历史数据

    Args:
        symbol: 期权代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        source: 数据源 ('sina')

    Returns:
        pd.DataFrame:
        - timestamp: 时间戳
        - symbol: 期权代码
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
        - open_interest: 持仓量
        - settlement: 结算价
    """
    provider = OptionsDataFactory.get_provider(source, underlying_symbol="")
    return provider.get_options_history(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )


# ==================== Multi-Source API with Auto-Failover ====================


def get_basic_info_multi_source(
    symbol: str,
    sources: list[str] | None = None,
) -> pd.DataFrame:
    """获取股票基础信息（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。

    Args:
        symbol: 股票代码 (e.g. '600000')
        sources: 数据源列表，默认 ["eastmoney", "sina"]

    Returns:
        pd.DataFrame: 股票基础信息
    """
    import logging
    from .modules.info.factory import InfoDataFactory

    if sources is None:
        sources = ["eastmoney", "sina"]

    providers = []
    for source in sources:
        try:
            provider = InfoDataFactory.get_provider(source, symbol=symbol)
            providers.append((source, provider))
        except Exception as e:
            logging.warning(f"Failed to initialize info provider '{source}': {e}")

    router = MultiSourceRouter(providers)
    return router.execute("get_basic_info")


def get_hist_data_multi_source(
    symbol: str,
    interval: Literal["minute", "hour", "day", "week", "month", "year"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: Literal["none", "qfq", "hfq"] = "none",
    sources: list[str] | None = None,
) -> pd.DataFrame:
    """获取历史数据（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。
    日线及以上数据使用天级缓存（24小时），分钟/小时数据使用小时缓存。

    Args:
        symbol: 股票代码 (e.g. '600000')
        interval: 时间间隔 ('minute','hour','day','week','month','year')
        interval_multiplier: 时间间隔倍数 (e.g. 5 for 5 minutes)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        adjust: 复权类型 ('none','qfq','hfq')
        sources: 数据源列表，默认 ["eastmoney_direct", "eastmoney", "sina"]

    Returns:
        pd.DataFrame: 历史数据

    Example:
        >>> df = get_hist_data_multi_source("600000", interval="day")
        >>> df = get_hist_data_multi_source(
        ...     "000001",
        ...     sources=["eastmoney_direct", "sina"]  # 自定义数据源优先级
        ... )
    """
    router = create_historical_router(
        symbol=symbol,
        interval=interval,
        interval_multiplier=interval_multiplier,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
        sources=sources,
    )
    return router.execute("get_hist_data")


def get_realtime_data_multi_source(
    symbol: str | None = None,
    sources: list[str] | None = None,
) -> pd.DataFrame:
    """获取实时数据（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。

    Args:
        symbol: 股票代码 (如 "600000")
        sources: 数据源列表，默认 ["eastmoney_direct", "eastmoney", "xueqiu"]

    Returns:
        pd.DataFrame: 实时行情数据

    Example:
        >>> df = get_realtime_data_multi_source("600000")
        >>> df = get_realtime_data_multi_source(
        ...     "000001",
        ...     sources=["eastmoney_direct", "xueqiu"]
        ... )
    """
    router = create_realtime_router(symbol=symbol, sources=sources)
    return router.execute("get_current_data")


def get_news_data_multi_source(
    symbol: str,
    sources: list[str] | None = None,
) -> pd.DataFrame:
    """获取个股新闻（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。

    Args:
        symbol: 股票代码 (如 "300059")
        sources: 数据源列表，默认 ["eastmoney"]

    Returns:
        pd.DataFrame: 新闻数据
    """
    import logging
    from .modules.news.factory import NewsDataFactory

    if sources is None:
        sources = ["eastmoney", "sina"]

    providers = []
    for source in sources:
        try:
            provider = NewsDataFactory.get_provider(source, symbol=symbol)
            providers.append((source, provider))
        except Exception as e:
            logging.warning(f"Failed to initialize news provider '{source}': {e}")

    router = MultiSourceRouter(providers)
    return router.execute("get_news_data")


def get_inner_trade_data_multi_source(
    symbol: str,
    sources: list[str] | None = None,
) -> pd.DataFrame:
    """获取内部交易数据（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。

    Args:
        symbol: 股票代码 (如 "600000")
        sources: 数据源列表，默认 ["xueqiu"]

    Returns:
        pd.DataFrame: 内部交易数据
    """
    import logging
    from .modules.insider.factory import InsiderDataFactory

    if sources is None:
        sources = ["xueqiu"]

    providers = []
    for source in sources:
        try:
            provider = InsiderDataFactory.get_provider(source, symbol=symbol)
            providers.append((source, provider))
        except Exception as e:
            logging.warning(f"Failed to initialize insider provider '{source}': {e}")

    router = MultiSourceRouter(providers)
    return router.execute("get_inner_trade_data")


def get_financial_data_multi_source(
    symbol: str,
    data_type: Literal["balance_sheet", "income_statement", "cash_flow"],
    sources: list[str] | None = None,
) -> pd.DataFrame:
    """获取财务数据（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。

    Args:
        symbol: 股票代码 (如 "600600")
        data_type: 数据类型 ('balance_sheet', 'income_statement', 'cash_flow')
        sources: 数据源列表，默认 ["eastmoney_direct", "sina"]

    Returns:
        pd.DataFrame: 财务数据
    """
    import logging
    from .modules.financial.factory import FinancialDataFactory

    if sources is None:
        sources = ["eastmoney_direct", "sina", "cninfo"]

    providers = []
    for source in sources:
        try:
            provider = FinancialDataFactory.get_provider(source, symbol=symbol)
            providers.append((source, provider))
        except Exception as e:
            logging.warning(f"Failed to initialize financial provider '{source}': {e}")

    router = MultiSourceRouter(providers)

    method_map = {
        "balance_sheet": "get_balance_sheet",
        "income_statement": "get_income_statement",
        "cash_flow": "get_cash_flow",
    }

    return router.execute(method_map[data_type])


def get_financial_metrics_multi_source(
    symbol: str,
    sources: list[str] | None = None,
) -> pd.DataFrame:
    """获取财务指标（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。
    数据缓存24小时。

    Args:
        symbol: 股票代码 (如 "600600")
        sources: 数据源列表，默认 ["eastmoney_direct", "sina", "cninfo"]

    Returns:
        pd.DataFrame: 财务指标数据

    Example:
        >>> df = get_financial_metrics_multi_source("600000")
    """
    router = create_financial_router(symbol=symbol, sources=sources)
    return router.execute("get_financial_metrics")
