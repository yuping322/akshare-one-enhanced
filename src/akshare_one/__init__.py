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

# AkShare compatibility adapter for handling function drift
from .akshare_compat import (
    AkShareAdapter,
    call_akshare,
    check_akshare_function,
    get_adapter,
)
from .constants import DEFAULT_RANDOM_STATE
from .http_client import configure_ssl_verification

# Import from new module locations
from .modules.core.base import apply_data_filter, BaseProvider
from .modules.core.factory import BaseFactory
from .modules.core.router import MultiSourceRouter, EmptyDataPolicy, ExecutionResult
from .modules.core.exceptions import (
    MarketDataError,
    InvalidParameterError,
    DataSourceUnavailableError,
    NoDataError,
    UpstreamChangedError,
    RateLimitError,
    DataValidationError,
    handle_upstream_error,
    map_to_standard_exception,
    raise_mapped_exception,
)
from .modules.core.cache import cache as cache_data, clear_cache, smart_cache
from .modules.core.calendar import (
    get_all_trade_days,
    transform_date,
    get_trade_dates_between,
    is_trade_date,
)


# Lazy imports for factories - imported on demand to avoid circular imports
def _get_financial_factory():
    from .modules.providers.equities.fundamentals.financial import FinancialDataFactory

    return FinancialDataFactory


def _get_historical_factory():
    from .modules.providers.equities.quotes.historical import HistoricalDataFactory

    return HistoricalDataFactory


def _get_info_factory():
    from .modules.providers.equities.fundamentals.info import InfoDataFactory

    return InfoDataFactory


def _get_insider_factory():
    from .modules.providers.equities.corporate_events.insider import InsiderDataFactory

    return InsiderDataFactory


def _get_news_factory():
    from .modules.providers.news import NewsDataFactory

    return NewsDataFactory


def _get_options_factory():
    from .modules.providers.derivatives.options import OptionsDataFactory

    return OptionsDataFactory


def _get_realtime_factory():
    from .modules.providers.equities.quotes.realtime import RealtimeDataFactory

    return RealtimeDataFactory


def _get_etf_factory():
    from .modules.providers.funds.etf import ETFFactory

    return ETFFactory


def _get_index_factory():
    from .modules.providers.indices import IndexFactory

    return IndexFactory


def _get_bond_factory():
    from .modules.providers.fixed_income.bonds import BondFactory

    return BondFactory


def _get_valuation_factory():
    from .modules.providers.equities.fundamentals.valuation import ValuationFactory

    return ValuationFactory


def _get_shareholder_factory():
    from .modules.providers.equities.corporate_events.shareholder import ShareholderFactory

    return ShareholderFactory


def _get_performance_factory():
    from .modules.providers.equities.fundamentals.performance import PerformanceFactory

    return PerformanceFactory


def _get_analyst_factory():
    from .modules.providers.equities.corporate_events.analyst import AnalystFactory

    return AnalystFactory


def _get_sentiment_factory():
    from .modules.providers.sentiment import SentimentFactory

    return SentimentFactory


def _get_concept_factory():
    from .modules.providers.sectors.concept import ConceptFactory

    return ConceptFactory


def _get_industry_factory():
    from .modules.providers.sectors.industry import IndustryFactory

    return IndustryFactory


def _get_hkus_factory():
    from .modules.providers.hk_equities import HKUSFactory

    return HKUSFactory


def _get_suspended_factory():
    from .modules.providers.equities.corporate_events.status import SuspendedFactory

    return SuspendedFactory


def _get_st_factory():
    from .modules.providers.equities.corporate_events.status import STFactory

    return STFactory


def _get_ipo_factory():
    from .modules.providers.equities.corporate_events.ipo import IPOFactory

    return IPOFactory


def _get_board_factory():
    from .modules.providers.sectors.boards import BoardFactory

    return BoardFactory


def _get_northbound_factory():
    from .modules.providers.equities.capital.northbound import NorthboundFactory

    return NorthboundFactory


def _get_fundflow_factory():
    from .modules.providers.equities.capital.fundflow import FundFlowFactory

    return FundFlowFactory


def _get_dragon_tiger_factory():
    from .modules.providers.equities.trading_events.dragon_tiger import DragonTigerFactory

    return DragonTigerFactory


def _get_futures_factory():
    from .modules.providers.derivatives.futures import FuturesDataFactory

    return FuturesDataFactory


def _get_limitup_factory():
    from .modules.providers.equities.trading_events.limit_up import LimitUpDownFactory

    return LimitUpDownFactory


def _get_disclosure_factory():
    from .modules.providers.equities.fundamentals.disclosure import DisclosureFactory

    return DisclosureFactory


def _get_macro_factory():
    from .modules.providers.macro import MacroFactory

    return MacroFactory


def _get_blockdeal_factory():
    from .modules.providers.equities.trading_events.block_deal import BlockDealFactory

    return BlockDealFactory


def _get_margin_factory():
    from .modules.providers.equities.capital.margin import MarginFactory

    return MarginFactory


def _get_pledge_factory():
    from .modules.providers.equities.corporate_events.pledge import EquityPledgeFactory

    return EquityPledgeFactory


def _get_restricted_factory():
    from .modules.providers.equities.corporate_events.restricted import RestrictedReleaseFactory

    return RestrictedReleaseFactory


def _get_convertbond_factory():
    from .modules.providers.fixed_income.convertible_bonds import ConvertBondFactory

    return ConvertBondFactory


def _get_callauction_factory():
    from .modules.providers.equities.trading_events.call_auction import CallAuctionFactory

    return CallAuctionFactory


def _get_lof_factory():
    from .modules.providers.funds.lof import LOFFactory

    return LOFFactory


def _get_fundof_factory():
    from .modules.providers.funds.fund_of import FOFFactory

    return FOFFactory


def _get_optiongreeks_factory():
    from .modules.providers.derivatives.options.greeks import OptionGreeksFactory

    return OptionGreeksFactory


def _get_indexweights_factory():
    from .modules.providers.indices.weights import IndexWeightsFactory

    return IndexWeightsFactory


def _get_companydepth_factory():
    from .modules.providers.equities.fundamentals.info import CompanyDepthFactory

    return CompanyDepthFactory


def _get_dividendcalc_factory():
    from .modules.providers.equities.fundamentals.dividend import DividendCalcFactory

    return DividendCalcFactory


def _get_sharechangedepth_factory():
    from .modules.providers.equities.corporate_events.shareholder import ShareChangeDepthFactory

    return ShareChangeDepthFactory


def _get_industryanalytics_factory():
    from .modules.providers.sectors.industry import IndustryAnalyticsFactory

    return IndustryAnalyticsFactory


def _get_northbounddepth_factory():
    from .modules.providers.equities.capital.northbound import NorthboundDepthFactory

    return NorthboundDepthFactory


def _get_macroakshare_factory():
    from .modules.providers.macro import MacroAkShareFactory

    return MacroAkShareFactory


def _get_futuresmargin_factory():
    from .modules.providers.derivatives.futures import FuturesMarginFactory

    return FuturesMarginFactory


def _get_shareholderdepth_factory():
    from .modules.providers.equities.corporate_events.shareholder import ShareholderDepthFactory

    return ShareholderDepthFactory


def _get_goodwill_factory():
    from .modules.providers.equities.corporate_events.goodwill import GoodwillFactory

    return GoodwillFactory


def _get_esg_factory():
    from .modules.providers.equities.fundamentals.esg import ESGFactory

    return ESGFactory


def _get_special_factory():
    from .modules.providers.equities.corporate_events.status import SpecialDataFactory

    return SpecialDataFactory


# Router creation functions
def _create_router(factory_class, method_name, default_sources):
    from .modules.core.factory import create_router

    return create_router(factory_class, method_name, default_sources)


def create_financial_router(sources=None, **kwargs):
    return _create_router(
        _get_financial_factory(), "get_financial_data", sources or ["sina", "eastmoney_direct", "lixinger"]
    )


def create_historical_router(sources=None, **kwargs):
    return _create_router(
        _get_historical_factory(),
        "get_hist_data",
        sources or ["sina", "lixinger", "eastmoney_direct", "eastmoney", "tencent", "netease"],
    )


def create_realtime_router(sources=None, **kwargs):
    return _create_router(
        _get_realtime_factory(), "get_current_data", sources or ["sina", "eastmoney_direct", "eastmoney", "xueqiu"]
    )


def create_northbound_router(sources=None, **kwargs):
    return _create_router(_get_northbound_factory(), "get_northbound_data", sources or ["sina", "eastmoney"])


def create_fundflow_router(sources=None, **kwargs):
    return _create_router(_get_fundflow_factory(), "get_fundflow_data", sources or ["sina", "eastmoney"])


def create_dragon_tiger_router(sources=None, **kwargs):
    return _create_router(_get_dragon_tiger_factory(), "get_dragon_tiger_data", sources or ["sina", "eastmoney"])


def create_limit_up_down_router(sources=None, **kwargs):
    return _create_router(_get_limitup_factory(), "get_limit_up_down_data", sources or ["sina", "eastmoney"])


def create_block_deal_router(sources=None, **kwargs):
    return _create_router(_get_blockdeal_factory(), "get_block_deal_data", sources or ["sina", "eastmoney"])


# JQ compat - lazy imports to avoid circular dependencies
def _get_jq_compat():
    from . import jq_compat

    return jq_compat


__all__ = [
    # 配置
    "configure_ssl_verification",
    # AkShare兼容性适配器
    "AkShareAdapter",
    "call_akshare",
    "check_akshare_function",
    "get_adapter",
    # 工具函数
    "apply_data_filter",
    # 多数据源
    "EmptyDataPolicy",
    "ExecutionResult",
    "MultiSourceRouter",
    "create_historical_router",
    "create_realtime_router",
    "create_financial_router",
    "create_northbound_router",
    "create_fundflow_router",
    "create_dragon_tiger_router",
    "create_limit_up_down_router",
    "create_block_deal_router",
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
    "get_top10_stock_holder_info",
    "get_latest_holder_number",
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
    "get_northbound_flow_multi_source",
    "get_northbound_holdings_multi_source",
    "get_northbound_top_stocks_multi_source",
    "get_stock_fund_flow_multi_source",
    "get_sector_fund_flow_multi_source",
    "get_main_fund_flow_rank_multi_source",
    "get_dragon_tiger_list_multi_source",
    "get_dragon_tiger_summary_multi_source",
    "get_limit_up_pool_multi_source",
    "get_limit_down_pool_multi_source",
    "get_block_deal_multi_source",
    # 北向资金
    "get_northbound_flow",
    "get_northbound_holdings",
    "get_northbound_top_stocks",
    # 资金流
    "get_stock_fund_flow",
    "get_sector_fund_flow",
    "get_main_fund_flow_rank",
    # 龙虎榜
    "get_dragon_tiger_list",
    "get_dragon_tiger_summary",
    "get_dragon_tiger_broker_stats",
    # 涨跌停
    "get_limit_up_pool",
    "get_limit_down_pool",
    "get_limit_up_stats",
    # 公告披露
    "get_disclosure_news",
    "get_dividend_data",
    "get_repurchase_data",
    "get_st_delist_data",
    # 宏观数据
    "get_lpr_rate",
    "get_pmi_index",
    "get_cpi_data",
    "get_ppi_data",
    "get_m2_supply",
    "get_shibor_rate",
    "get_social_financing",
    # 大宗交易
    "get_block_deal",
    "get_block_deal_summary",
    "get_deal_detail",
    # 融资融券
    "get_margin_data",
    "get_margin_summary",
    # 股权质押
    "get_equity_pledge",
    "get_equity_pledge_ratio_rank",
    # 限售解禁
    "get_restricted_release",
    "get_restricted_release_calendar",
    # 商誉
    "get_goodwill_data",
    "get_goodwill_impairment",
    "get_goodwill_by_industry",
    # ESG
    "get_esg_rating",
    "get_esg_rating_rank",
    # 特色数据
    "get_chip_distribution",
    "get_broker_forecast",
    "get_institutional_research",
    # 可转债深度
    "get_convert_bond_list",
    "get_convert_bond_info",
    "get_convert_bond_hist",
    "get_convert_bond_spot",
    "get_convert_bond_premium",
    "get_convert_bond_by_stock",
    "get_convert_bond_quote",
    "calculate_conversion_value",
    "calculate_premium_rate",
    "get_convert_bond_daily",
    # 集合竞价
    "get_call_auction",
    "get_call_auction_batch",
    # LOF/FOF
    "get_lof_list",
    "get_lof_hist_data",
    "get_lof_spot",
    "get_lof_nav",
    "get_fof_list",
    "get_fof_nav",
    "get_fof_info",
    # 期权Greeks
    "get_option_greeks",
    "calculate_option_implied_vol",
    "calculate_implied_vol",
    "calculate_greeks",
    "black_scholes_price",
    # 指数权重
    "get_index_weights",
    "get_index_weights_history",
    "get_index_info",
    # 公司深度
    "get_security_status",
    "get_name_history",
    "get_management_info",
    "get_employee_info",
    "get_listing_info",
    "get_industry_info",
    # 分红计算
    "calculate_ex_rights_price",
    "calculate_adjust_price",
    "get_stock_bonus",
    "get_rights_issue",
    "get_dividend_by_date",
    # 股权变动深度
    "get_freeze_info",
    "get_capital_change",
    "get_topholder_change",
    "get_major_holder_trade",
    # 行业分析
    "get_stock_industry",
    "get_industry_performance",
    "get_concept_performance",
    "search_concept",
    "get_all_concept_stocks",
    "get_all_industries",
    "filter_stocks_by_industry",
    "query_industry_sw",
    # 北向深度
    "get_north_stock_detail",
    "get_north_quota_info",
    "get_north_calendar",
    "compute_north_money_signal",
    # 宏观akshare
    "get_macro_gdp",
    "get_macro_cpi",
    "get_macro_ppi",
    "get_macro_pmi",
    "get_macro_interest_rate",
    "get_macro_exchange_rate",
    "get_macro_china_gdp",
    "get_macro_china_cpi",
    "get_macro_china_ppi",
    "get_macro_china_pmi",
    "get_macro_china_interest_rate",
    "get_macro_china_exchange_rate",
    # 期货保证金
    "get_contract_multiplier",
    "get_margin_rate_for_contract",
    "calculate_position_value",
    "calculate_required_margin",
    "get_contract_info",
    "get_margin_rate",
    # 股东深度
    "get_shareholder_structure",
    "get_shareholder_concentration",
    # jk2bt兼容别名
    "get_stock_daily",
    "get_stock_price",
    "get_etf_daily",
    "get_index_daily",
    "get_stock_minute",
    "get_etf_minute",
    "get_money_flow",
    "get_north_money_flow",
    "get_north_money_holdings",
    "get_north_money_stock_flow",
    "get_company_info",
    "get_shareholders",
    "get_income",
    "get_cashflow",
    "get_fund_net_value",
    "get_margin_data_module",
    "get_forecast_data",
    "get_unlock",
    "get_unlock_calendar",
    "get_stock_concepts",
    "get_all_concept_stocks",
    "get_sw_industry_list",
    "get_industry_stocks_module",
    "get_dominant_contract",
    "get_future_contracts",
    "get_future_daily",
    "get_adapter",
    "get_cache_manager",
    # JQ Compatibility
    "get_price",
    "get_bars",
    "history",
    "attribute_history",
    "get_valuation",
    "get_index_valuation",
    "risk",
    "strategy",
]


# Risk and strategy - lazy imports to avoid circular dependencies
def _get_risk():
    from . import risk

    return risk


def _get_strategy():
    from . import strategy

    return strategy


def get_basic_info(
    symbol: str,
    source: Literal["eastmoney", "sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取股票基础信息"""
    provider = _get_info_factory().get_provider(source, symbol=symbol)
    df = provider.get_basic_info()
    return apply_data_filter(df, columns, row_filter)


def get_hist_data(
    symbol: str,
    interval: Literal["minute", "hour", "day", "week", "month", "year"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: Literal["none", "qfq", "hfq"] = "none",
    source: Literal["sina", "lixinger", "eastmoney", "eastmoney_direct"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Get historical market data"""
    kwargs = {
        "symbol": symbol,
        "interval": interval,
        "interval_multiplier": interval_multiplier,
        "start_date": start_date,
        "end_date": end_date,
        "adjust": adjust,
    }
    provider = _get_historical_factory().get_provider(source, **kwargs)
    df = provider.get_hist_data()
    return apply_data_filter(df, columns, row_filter)


def get_realtime_data(
    symbol: str | None = None,
    source: Literal["eastmoney", "eastmoney_direct", "xueqiu"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Get real-time market quotes"""
    provider = _get_realtime_factory().get_provider(source, symbol=symbol)
    df = provider.get_current_data()
    return apply_data_filter(df, columns, row_filter)


def get_news_data(
    symbol: str,
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取个股新闻数据"""
    provider = _get_news_factory().get_provider(source, symbol=symbol)
    df = provider.get_news_data()
    return apply_data_filter(df, columns, row_filter)


def get_balance_sheet(
    symbol: str,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取资产负债表数据"""
    provider = _get_financial_factory().get_provider(source, symbol=symbol)
    df = provider.get_balance_sheet()
    return apply_data_filter(df, columns, row_filter)


def get_income_statement(
    symbol: str,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取利润表数据"""
    provider = _get_financial_factory().get_provider(source, symbol=symbol)
    df = provider.get_income_statement()
    return apply_data_filter(df, columns, row_filter)


def get_cash_flow(
    symbol: str,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取现金流量表数据"""
    provider = _get_financial_factory().get_provider(source, symbol=symbol)
    df = provider.get_cash_flow()
    return apply_data_filter(df, columns, row_filter)


def get_financial_metrics(
    symbol: str,
    source: Literal["sina", "eastmoney_direct", "lixinger"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取三大财务报表关键指标"""
    provider = _get_financial_factory().get_provider(source, symbol=symbol)
    df = provider.get_financial_metrics()
    return apply_data_filter(df, columns, row_filter)


def get_inner_trade_data(
    symbol: str,
    source: Literal["xueqiu"] = "xueqiu",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取雪球内部交易数据"""
    provider = _get_insider_factory().get_provider(source, symbol=symbol)
    df = provider.get_inner_trade_data()
    return apply_data_filter(df, columns, row_filter)


# ==================== Futures API ====================


def get_futures_hist_data(
    symbol: str,
    contract: str = "main",
    interval: Literal["minute", "hour", "day", "week", "month"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取期货历史数据"""
    kwargs = {
        "symbol": symbol,
        "contract": contract,
        "interval": interval,
        "interval_multiplier": interval_multiplier,
        "start_date": start_date,
        "end_date": end_date,
    }
    provider = _get_futures_factory().get_historical_provider(source, **kwargs)
    df = provider.get_hist_data()
    return apply_data_filter(df, columns, row_filter)


def get_futures_realtime_data(
    symbol: str | None = None,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取期货实时行情数据"""
    provider = _get_futures_factory().get_realtime_provider(source, symbol=symbol or "")
    if symbol:
        df = provider.get_current_data()
        return apply_data_filter(df, columns, row_filter)
    df = provider.get_all_quotes()
    return apply_data_filter(df, columns, row_filter)


def get_futures_main_contracts(
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取期货主力合约列表"""
    from .modules.providers.derivatives.futures.sina import SinaFuturesHistorical

    provider = SinaFuturesHistorical(symbol="")
    df = provider.get_main_contracts()
    return apply_data_filter(df, columns, row_filter)


# ==================== Options API ====================


def get_options_chain(
    underlying_symbol: str,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取期权链数据"""
    provider = _get_options_factory().get_provider(source, underlying_symbol=underlying_symbol)
    df = provider.get_options_chain()
    return apply_data_filter(df, columns, row_filter)


def get_options_realtime(
    symbol: str | None = None,
    underlying_symbol: str | None = None,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取期权实时行情数据"""
    if symbol is not None and underlying_symbol is not None:
        raise ValueError("Cannot specify both 'symbol' and 'underlying_symbol'. Provide one or the other.")
    if symbol is None and underlying_symbol is None:
        raise ValueError("Must specify either 'symbol' or 'underlying_symbol'.")

    if symbol:
        provider = _get_options_factory().get_provider(source, underlying_symbol="")
        df = provider.get_options_realtime(symbol)
        return apply_data_filter(df, columns, row_filter)
    provider = _get_options_factory().get_provider(source, underlying_symbol=underlying_symbol)
    df = provider.get_options_realtime("")
    return apply_data_filter(df, columns, row_filter)


def get_options_expirations(
    underlying_symbol: str,
    source: Literal["sina"] = "sina",
) -> list[str]:
    """获取期权可用到期日列表"""
    provider = _get_options_factory().get_provider(source, underlying_symbol=underlying_symbol)
    return provider.get_options_expirations(underlying_symbol)


def get_options_hist(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取期权历史数据"""
    provider = _get_options_factory().get_provider(source, underlying_symbol="")
    df = provider.get_options_history(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )
    return apply_data_filter(df, columns, row_filter)


# ==================== Multi-Source API泛型函数 ====================


def _get_data_multi_source(
    method_name: str,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
    method_map: dict[str, str] | None = None,
    execute_args: tuple = (),
    execute_kwargs: dict | None = None,
    router_factory=None,
    factory_class=None,
    default_sources: list[str] | None = None,
    router_kwargs: dict | None = None,
    **factory_kwargs,
) -> pd.DataFrame:
    """Generic multi-source data fetcher.

    Args:
        method_name: Method name to call on router.execute()
        sources: Data source list
        columns: Columns to select
        row_filter: Row filter configuration
        method_map: Dict mapping data_type to method_name (for financial_data)
        execute_args: Positional args for router.execute()
        execute_kwargs: Keyword args for router.execute()
        router_factory: Router creation function (e.g., create_historical_router)
        factory_class: Factory class for direct provider creation
        default_sources: Default sources if not provided
        router_kwargs: Additional kwargs for router_factory
        **factory_kwargs: Additional kwargs passed to factory.get_provider
    """
    import logging

    if sources is None:
        sources = default_sources

    if execute_kwargs is None:
        execute_kwargs = {}

    if router_kwargs is None:
        router_kwargs = {}

    if router_factory is not None:
        router_kwargs.update(factory_kwargs)
        router = router_factory(sources=sources, **router_kwargs)
    elif factory_class is not None:
        providers = []
        symbol = factory_kwargs.get("symbol")
        for source in sources or []:
            try:
                provider = factory_class.get_provider(
                    source, symbol=symbol, **{k: v for k, v in factory_kwargs.items() if k != "symbol"}
                )
                providers.append((source, provider))
            except Exception as e:
                logging.warning(f"Failed to initialize provider '{source}': {e}")
        router = MultiSourceRouter(providers)
    else:
        raise ValueError("Either router_factory or factory_class must be provided")

    actual_method = method_name
    if method_map and method_name in method_map:
        actual_method = method_map[method_name]

    df = router.execute(actual_method, *execute_args, **execute_kwargs)
    return apply_data_filter(df, columns, row_filter)


# ==================== Multi-Source API with Auto-Failover ====================


def get_basic_info_multi_source(
    symbol: str,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取股票基础信息（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_basic_info",
        symbol=symbol,
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        factory_class=_get_info_factory(),
        default_sources=["sina", "eastmoney"],
    )


def get_hist_data_multi_source(
    symbol: str,
    interval: Literal["minute", "hour", "day", "week", "month", "year"] = "day",
    interval_multiplier: int = 1,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    adjust: Literal["none", "qfq", "hfq"] = "none",
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
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
        sources: 数据源列表，默认 ["sina", "lixinger", "eastmoney_direct", "eastmoney"]

    Returns:
        pd.DataFrame: 历史数据

    Example:
        >>> df = get_hist_data_multi_source("600000", interval="day")
        >>> df = get_hist_data_multi_source(
        ...     "000001",
        ...     sources=["sina", "lixinger"]  # 自定义数据源优先级
        ... )
    """
    return _get_data_multi_source(
        method_name="get_hist_data",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_historical_router,
        symbol=symbol,
        interval=interval,
        interval_multiplier=interval_multiplier,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )


def get_realtime_data_multi_source(
    symbol: str | None = None,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取实时数据（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。

    Args:
        symbol: 股票代码 (如 "600000")
        sources: 数据源列表，默认 ["sina", "eastmoney_direct", "eastmoney", "xueqiu"]

    Returns:
        pd.DataFrame: 实时行情数据

    Example:
        >>> df = get_realtime_data_multi_source("600000")
        >>> df = get_realtime_data_multi_source(
        ...     "000001",
        ...     sources=["sina", "xueqiu"]
        ... )
    """
    return _get_data_multi_source(
        method_name="get_current_data",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_realtime_router,
        symbol=symbol,
    )


def get_news_data_multi_source(
    symbol: str,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取个股新闻（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_news_data",
        symbol=symbol,
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        factory_class=_get_news_factory(),
        default_sources=["eastmoney", "sina"],
    )


def get_inner_trade_data_multi_source(
    symbol: str,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取内部交易数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_inner_trade_data",
        symbol=symbol,
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        factory_class=_get_insider_factory(),
        default_sources=["xueqiu"],
    )


def get_financial_data_multi_source(
    symbol: str,
    data_type: Literal["balance_sheet", "income_statement", "cash_flow"],
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取财务数据（多数据源自动切换）"""
    method_map = {
        "balance_sheet": "get_balance_sheet",
        "income_statement": "get_income_statement",
        "cash_flow": "get_cash_flow",
    }

    return _get_data_multi_source(
        method_name=data_type,
        method_map=method_map,
        symbol=symbol,
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        factory_class=_get_financial_factory(),
        default_sources=["eastmoney_direct", "sina", "cninfo"],
    )


def get_financial_metrics_multi_source(
    symbol: str,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
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
    return _get_data_multi_source(
        method_name="get_financial_metrics",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_financial_router,
        symbol=symbol,
    )


# ==================== 北向资金多源API ====================
def get_northbound_flow_multi_source(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    market: Literal["sh", "sz", "all"] = "all",
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取北向资金流量数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_northbound_flow",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_northbound_router,
        execute_args=(start_date, end_date, market),
    )


def get_northbound_holdings_multi_source(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取北向资金持仓数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_northbound_holdings",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_northbound_router,
        execute_args=(symbol, start_date, end_date),
    )


def get_northbound_top_stocks_multi_source(
    date: str,
    market: Literal["sh", "sz", "all"] = "all",
    top_n: int = 100,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取北向资金持仓排名（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_northbound_top_stocks",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_northbound_router,
        execute_args=(date, market, top_n),
    )


# ==================== 资金流多源API ====================
def get_stock_fund_flow_multi_source(
    symbol: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取个股资金流数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_stock_fund_flow",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_fundflow_router,
        symbol=symbol,
        execute_args=(start_date, end_date),
    )


def get_sector_fund_flow_multi_source(
    sector_type: Literal["industry", "concept"],
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取板块资金流数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_sector_fund_flow",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_fundflow_router,
        execute_args=(sector_type, start_date, end_date),
    )


def get_main_fund_flow_rank_multi_source(
    date: str,
    indicator: Literal["net_inflow", "net_inflow_rate"] = "net_inflow",
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取主力资金流排名（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_main_fund_flow_rank",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_fundflow_router,
        execute_args=(date, indicator),
    )


# ==================== 龙虎榜多源API ====================
def get_dragon_tiger_list_multi_source(
    date: str,
    symbol: str | None = None,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取龙虎榜数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_dragon_tiger_list",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_dragon_tiger_router,
        execute_args=(date, symbol),
    )


def get_dragon_tiger_summary_multi_source(
    start_date: str,
    end_date: str,
    group_by: Literal["stock", "broker", "reason"] = "stock",
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取龙虎榜统计数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_dragon_tiger_summary",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_dragon_tiger_router,
        execute_args=(start_date, end_date, group_by),
    )


# ==================== 涨跌停多源API ====================
def get_limit_up_pool_multi_source(
    date: str,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取涨停池数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_limit_up_pool",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_limit_up_down_router,
        execute_args=(date,),
    )


def get_limit_down_pool_multi_source(
    date: str,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取跌停池数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_limit_down_pool",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_limit_up_down_router,
        execute_args=(date,),
    )


# ==================== 大宗交易多源API ====================
def get_block_deal_multi_source(
    symbol: str | None = None,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取大宗交易数据（多数据源自动切换）"""
    return _get_data_multi_source(
        method_name="get_block_deal",
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        router_factory=create_block_deal_router,
        symbol=symbol,
        execute_args=(start_date, end_date),
    )


# ==================== jk2bt 兼容别名 ====================


# 股票日线别名
def get_stock_daily(symbol: str, start: str, end: str, adjust: str = "qfq", **kwargs) -> pd.DataFrame:
    """获取股票日线数据(jk2bt兼容)"""
    return get_hist_data(symbol, interval="day", start_date=start, end_date=end, adjust=adjust, source="sina", **kwargs)


def get_stock_price(securities, start_date=None, end_date=None, count=None, fields=None, adjust="qfq", **kwargs):
    """获取股票价格(jk2bt兼容)"""
    from .jq_compat import get_price

    return get_price(
        security=securities,
        start_date=start_date,
        end_date=end_date,
        count=count,
        fields=fields,
        fq="pre" if adjust == "qfq" else "post" if adjust == "hfq" else None,
        **kwargs,
    )


# ETF日线别名
def get_etf_daily(symbol: str, start: str, end: str, **kwargs) -> pd.DataFrame:
    """获取ETF日线数据(jk2bt兼容)"""
    return get_etf_hist_data(symbol, start_date=start, end_date=end, **kwargs)


# 指数日线别名
def get_index_daily(symbol: str, start: str, end: str, **kwargs) -> pd.DataFrame:
    """获取指数日线数据(jk2bt兼容)"""
    return get_index_hist_data(symbol, start_date=start, end_date=end, **kwargs)


# 分钟线别名
def get_stock_minute(
    symbol: str, start: str, end: str, period: str = "1m", adjust: str = "qfq", **kwargs
) -> pd.DataFrame:
    """获取股票分钟线数据(jk2bt兼容)"""
    interval_map = {"1m": "minute", "5m": "minute", "15m": "minute", "30m": "minute", "60m": "hour"}
    interval = interval_map.get(period, "minute")
    multiplier = int(period.replace("m", "")) if period.endswith("m") else 1
    if interval == "hour":
        return get_hist_data(
            symbol,
            interval="hour",
            interval_multiplier=multiplier,
            start_date=start,
            end_date=end,
            adjust=adjust,
            source="sina",
            **kwargs,
        )
    return get_hist_data(
        symbol,
        interval="minute",
        interval_multiplier=multiplier,
        start_date=start,
        end_date=end,
        adjust=adjust,
        source="sina",
        **kwargs,
    )


def get_etf_minute(symbol: str, start: str, end: str, period: str = "1m", **kwargs) -> pd.DataFrame:
    """获取ETF分钟线数据(jk2bt兼容)"""
    interval_map = {"1m": "minute", "5m": "minute", "15m": "minute", "30m": "minute", "60m": "hour"}
    interval = interval_map.get(period, "minute")
    multiplier = int(period.replace("m", "")) if period.endswith("m") else 1
    if interval == "hour":
        return get_etf_hist_data(
            symbol, start_date=start, end_date=end, interval="hour", interval_multiplier=multiplier, **kwargs
        )
    return get_etf_hist_data(
        symbol, start_date=start, end_date=end, interval="minute", interval_multiplier=multiplier, **kwargs
    )


# 资金流别名
def get_money_flow(security_list=None, start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取资金流数据(jk2bt兼容)"""
    from .jq_compat import get_money_flow as jq_get_money_flow

    return jq_get_money_flow(security=security_list, start_date=start_date, end_date=end_date)


# 北向资金别名
def get_north_money_flow(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取北向资金流(jk2bt兼容)"""
    return get_northbound_flow(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_north_money_holdings(date=None, top_n=50, **kwargs) -> pd.DataFrame:
    """获取北向持仓(jk2bt兼容)"""
    return get_northbound_top_stocks(date=date or "", top_n=top_n)


def get_north_money_stock_flow(symbol=None, start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取北向个股资金流(jk2bt兼容)"""
    return get_northbound_holdings(
        symbol=symbol, start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31"
    )


# 公司信息别名
def get_company_info(symbol: str, **kwargs) -> pd.DataFrame:
    """获取公司信息(jk2bt兼容)"""
    return get_basic_info(symbol, source="sina", **kwargs)


# 股东别名
def get_shareholders(symbol: str, date=None, **kwargs):
    """获取股东信息(jk2bt兼容)"""
    return get_top_shareholders(symbol, date=date or "")


# 财务别名
def get_income(symbol: str, **kwargs) -> pd.DataFrame:
    """获取利润表(jk2bt兼容)"""
    return get_income_statement(symbol, **kwargs)


def get_cashflow(symbol: str, **kwargs) -> pd.DataFrame:
    """获取现金流量表(jk2bt兼容)"""
    return get_cash_flow(symbol, **kwargs)


def get_fund_net_value(symbol: str, start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取基金净值(jk2bt兼容)"""
    from .jq_compat import get_fund_nav

    return get_fund_nav(symbol, start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


# 融资融券别名
def get_margin_data_module(symbol: str, start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取融资融券数据(jk2bt兼容)"""
    provider = _get_margin_factory().get_provider("eastmoney", symbol=symbol)
    return provider.get_margin_data(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


# 业绩预测别名
def get_forecast_data(symbol: str, **kwargs) -> pd.DataFrame:
    """获取业绩预测(jk2bt兼容)"""
    provider = _get_performance_factory().get_provider("eastmoney", symbol=symbol)
    return provider.get_performance_forecast(start_date="1970-01-01", end_date="2030-12-31")


# 限售解禁别名
def get_unlock(symbol: str, **kwargs) -> pd.DataFrame:
    """获取限售解禁(jk2bt兼容)"""
    return get_restricted_release(symbol, start_date="1970-01-01", end_date="2030-12-31")


def get_unlock_calendar(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取解禁日历(jk2bt兼容)"""
    return get_restricted_release_calendar(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


# 概念别名
def get_stock_concepts(security, date=None, **kwargs):
    """获取股票概念(jk2bt兼容)"""
    from .jq_compat import get_concept

    return get_concept(security, date=date)


def get_all_concept_stocks(date=None, **kwargs) -> pd.DataFrame:
    """获取所有概念股(jk2bt兼容)"""
    return get_all_concept_stocks_module(**kwargs)


# 行业别名
def get_sw_industry_list(level=1, **kwargs) -> pd.DataFrame:
    """获取申万行业列表(jk2bt兼容)"""
    provider = _get_industry_factory().get_provider("eastmoney", industry_name="")
    return provider.get_industry_classify(level=f"sw_l{level}")


def get_industry_stocks_module(industry_name: str, **kwargs) -> list:
    """获取行业成分股(jk2bt兼容)"""
    provider = _get_industry_factory().get_provider("eastmoney", industry_name=industry_name)
    return provider.get_industry_stocks(industry_name)


# 期货别名
def get_dominant_contract(product: str, date=None, **kwargs) -> str:
    """获取主力合约(jk2bt兼容)"""
    from .jq_compat import get_dominant_future

    return get_dominant_future(product, date=date)


def get_future_contracts(product=None, exchange=None, date=None, **kwargs) -> pd.DataFrame:
    """获取期货合约列表(jk2bt兼容)"""
    from .jq_compat import get_future_contracts as jq_get_future_contracts

    return jq_get_future_contracts(product or "", exchange=exchange, date=date)


def get_future_daily(contract_code: str, start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取期货日线(jk2bt兼容)"""
    return get_futures_hist_data(
        contract_code, start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31"
    )


# 宏观别名
def get_macro_china_gdp(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国GDP(jk2bt兼容)"""
    from .modules.providers.macro.akshare_source import get_macro_china_gdp as _gdp

    return _gdp(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_cpi(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国CPI(jk2bt兼容)"""
    from .modules.providers.macro.akshare_source import get_macro_china_cpi as _cpi

    return _cpi(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_ppi(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国PPI(jk2bt兼容)"""
    from .modules.providers.macro.akshare_source import get_macro_china_ppi as _ppi

    return _ppi(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_pmi(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国PMI(jk2bt兼容)"""
    from .modules.providers.macro.akshare_source import get_macro_china_pmi as _pmi

    return _pmi(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_interest_rate(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国利率(jk2bt兼容)"""
    from .modules.providers.macro.akshare_source import get_macro_china_interest_rate as _rate

    return _rate(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_exchange_rate(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国汇率(jk2bt兼容)"""
    from .modules.providers.macro.akshare_source import get_macro_china_exchange_rate as _fx

    return _fx(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


# 缓存/数据源别名
def get_adapter():
    """获取数据适配器"""
    from .akshare_compat import get_adapter as _get_adapter

    return _get_adapter()


def get_cache_manager(db_path=None):
    """获取缓存管理器"""
    from .cache.manager import get_cache_manager as _get_cache_manager

    return _get_cache_manager()


# ==================== 新增模块导出 ====================


# 基金持仓
def get_fund_portfolio(
    fund_code: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
) -> pd.DataFrame:
    """获取基金持仓明细"""
    from .modules.fundportfolio import get_fund_portfolio as _fp

    return _fp(fund_code, start_date=start_date, end_date=end_date, **kwargs)


# 行业内个股表现
def get_industry_stocks_performance(industry_name: str, **kwargs) -> pd.DataFrame:
    """获取行业内所有个股表现"""
    from .modules.industryperformance import get_industry_stocks_performance as _isp

    return _isp(industry_name, **kwargs)


def get_all_industry_mapping(level: int = 1, **kwargs) -> pd.DataFrame:
    """获取全市场股票行业映射"""
    from .modules.industryperformance import get_all_industry_mapping as _aim

    return _aim(level=level, **kwargs)


def get_market_breadth(date: str = "", method: str = "method2", **kwargs) -> float:
    """获取市场宽度指标"""
    from .modules.industryperformance import get_market_breadth as _mb

    return _mb(date=date, method=method, **kwargs)


# Mock数据源
def create_mock_with_sample_data():
    """创建带样本数据的Mock提供者"""
    from .modules.mockdata import create_mock_with_sample_data as _mock

    return _mock()


def create_mock_with_error(error_msg: str = "Mock error"):
    """创建总是报错的Mock提供者"""
    from .modules.mockdata import create_mock_with_error as _mock

    return _mock(error_msg)


# 下次分红
def get_next_dividend(symbol: str, **kwargs) -> pd.DataFrame:
    """获取下一次分红预测"""
    from .modules.dividendnext import get_next_dividend as _nd

    return _nd(symbol, **kwargs)


# LOF回退
def get_lof_daily_with_fallback(symbol: str, start: str, end: str, prefer_nav: bool = False, **kwargs) -> pd.DataFrame:
    """获取LOF日线数据（带回退）"""
    from .modules.dividendnext import get_lof_daily_with_fallback as _lof

    return _lof(symbol, start, end, prefer_nav=prefer_nav, **kwargs)


# 分析函数
def analyze_share_change_trend(symbol: str, period_days: int = 90, **kwargs) -> dict:
    """分析股东变动趋势"""
    from .modules.analysis import analyze_share_change_trend as _analyze

    return _analyze(symbol, period_days=period_days, **kwargs)


def analyze_unlock_impact(symbol: str, days_ahead: int = 30, **kwargs) -> dict:
    """分析解禁压力"""
    from .modules.analysis import analyze_unlock_impact as _analyze

    return _analyze(symbol, days_ahead=days_ahead, **kwargs)


# 批量查询
def query_shareholder_top10(symbols: list[str], **kwargs) -> pd.DataFrame:
    """批量查询前十大股东"""
    from .modules.batchquery import query_shareholder_top10 as _q

    return _q(symbols, **kwargs)


def query_shareholder_float_top10(symbols: list[str], **kwargs) -> pd.DataFrame:
    """批量查询前十大流通股东"""
    from .modules.batchquery import query_shareholder_float_top10 as _q

    return _q(symbols, **kwargs)


def query_shareholder_num(symbols: list[str], **kwargs) -> pd.DataFrame:
    """批量查询股东户数"""
    from .modules.batchquery import query_shareholder_num as _q

    return _q(symbols, **kwargs)


def query_dividend(
    symbols: list[str], start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
) -> pd.DataFrame:
    """批量查询分红数据"""
    from .modules.batchquery import query_dividend as _q

    return _q(symbols, start_date=start_date, end_date=end_date, **kwargs)


def query_share_change(symbols: list[str], **kwargs) -> pd.DataFrame:
    """批量查询股东变动"""
    from .modules.batchquery import query_share_change as _q

    return _q(symbols, **kwargs)


def query_unlock(symbols: list[str], **kwargs) -> pd.DataFrame:
    """批量查询解禁数据"""
    from .modules.batchquery import query_unlock as _q

    return _q(symbols, **kwargs)


def query_pledge_data(symbols: list[str], **kwargs) -> pd.DataFrame:
    """批量查询质押数据"""
    from .modules.batchquery import query_pledge_data as _q

    return _q(symbols, **kwargs)


def query_freeze_data(symbols: list[str], **kwargs) -> pd.DataFrame:
    """批量查询冻结数据"""
    from .modules.batchquery import query_freeze_data as _q

    return _q(symbols, **kwargs)


def query_capital_change(symbols: list[str], **kwargs) -> pd.DataFrame:
    """批量查询股本变动"""
    from .modules.batchquery import query_capital_change as _q

    return _q(symbols, **kwargs)


def query_index_components(index_codes: list[str], **kwargs) -> pd.DataFrame:
    """批量查询指数成分股"""
    from .modules.batchquery import query_index_components as _q

    return _q(index_codes, **kwargs)


def query_company_basic_info(symbols: list[str], **kwargs) -> pd.DataFrame:
    """批量查询公司基本信息"""
    from .modules.batchquery import query_company_basic_info as _q

    return _q(symbols, **kwargs)


def query_conversion_bond(bond_codes: list[str], **kwargs) -> pd.DataFrame:
    """批量查询可转债信息"""
    from .modules.batchquery import query_conversion_bond as _q

    return _q(bond_codes, **kwargs)


# 北向单日汇总
def get_north_money_daily(date: str = "", **kwargs) -> dict:
    """获取北向资金单日汇总"""
    from .modules.northdaily import get_north_daily as _nd

    return _nd(date=date, **kwargs)


# 通用宏观接口
def get_macro_data(
    indicator: str, start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
) -> pd.DataFrame:
    """通用宏观数据查询"""
    from .modules.northdaily import get_macro_data as _md

    return _md(indicator, start_date=start_date, end_date=end_date, **kwargs)


def get_macro_indicators() -> list[str]:
    """获取所有可用的宏观指标"""
    from .modules.northdaily import get_macro_indicators as _mi

    return _mi()


def get_macro_series(
    indicators: list[str], start_date: str = "1970-01-01", end_date: str = "2030-12-31", **kwargs
) -> pd.DataFrame:
    """获取多个宏观指标时间序列"""
    from .modules.northdaily import get_macro_series as _ms

    return _ms(indicators, start_date=start_date, end_date=end_date, **kwargs)
