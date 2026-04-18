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
from .modules.base import apply_data_filter

from .modules.financial import FinancialDataFactory

from .modules.historical import HistoricalDataFactory
from .modules.info import InfoDataFactory
from .modules.insider import InsiderDataFactory
from .modules.multi_source import (
    EmptyDataPolicy,
    ExecutionResult,
    MultiSourceRouter,
    create_financial_router,
    create_historical_router,
    create_realtime_router,
    create_northbound_router,
    create_fundflow_router,
    create_dragon_tiger_router,
    create_limit_up_down_router,
    create_block_deal_router,
)
from .modules.news import NewsDataFactory
from .modules.options import OptionsDataFactory
from .modules.realtime import RealtimeDataFactory
from .modules.etf import (
    ETFFactory,
    get_etf_hist_data,
    get_etf_realtime_data,
    get_etf_list,
    get_fund_manager_info,
    get_fund_rating_data,
)
from .modules.index import (
    IndexFactory,
    get_index_hist_data,
    get_index_realtime_data,
    get_index_list,
    get_index_constituents,
)
from .modules.bond import (
    BondFactory,
    get_bond_list,
    get_bond_hist_data,
    get_bond_realtime_data,
)
from .modules.valuation import (
    ValuationFactory,
    get_stock_valuation,
    get_market_valuation,
)
from .modules.shareholder import (
    ShareholderFactory,
    get_shareholder_changes,
    get_top_shareholders,
    get_institution_holdings,
    get_top10_stock_holder_info,
    get_latest_holder_number,
)
from .modules.performance import PerformanceFactory
from .modules.analyst import AnalystFactory
from .modules.sentiment import SentimentFactory
from .modules.concept import ConceptFactory, get_concept_list, get_concept_stocks
from .modules.industry import IndustryFactory, get_industry_list, get_industry_stocks
from .modules.hkus import HKUSFactory, get_hk_stocks, get_us_stocks
from .modules.suspended import SuspendedFactory, get_suspended_stocks
from .modules.st import STFactory, get_st_stocks
from .modules.ipo import IPOFactory, get_new_stocks, get_ipo_info
from .modules.board import BoardFactory, get_kcb_stocks, get_cyb_stocks
from .modules.northbound import (
    NorthboundFactory,
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks,
)
from .modules.fundflow import (
    FundFlowFactory,
    get_stock_fund_flow,
    get_sector_fund_flow,
    get_main_fund_flow_rank,
)
from .modules.lhb import (
    DragonTigerFactory,
    get_dragon_tiger_list,
    get_dragon_tiger_summary,
    get_dragon_tiger_broker_stats,
)
from .modules.futures import (
    FuturesDataFactory,
    get_futures_hist_data,
    get_futures_main_contracts,
    get_futures_realtime_data,
    get_futures_all_quotes,
)
from .modules.limitup import (
    LimitUpDownFactory,
    get_limit_up_pool,
    get_limit_down_pool,
    get_limit_up_stats,
)
from .modules.disclosure import (
    DisclosureFactory,
    get_disclosure_news,
    get_dividend_data,
    get_repurchase_data,
    get_st_delist_data,
)
from .modules.macro import (
    MacroFactory,
    get_lpr_rate,
    get_pmi_index,
    get_cpi_data,
    get_ppi_data,
    get_m2_supply,
    get_shibor_rate,
    get_social_financing,
)
from .modules.blockdeal import (
    BlockDealFactory,
    get_block_deal,
    get_block_deal_summary,
    get_deal_detail,
)
from .modules.margin import (
    MarginFactory,
    get_margin_data,
    get_margin_summary,
)
from .modules.pledge import (
    EquityPledgeFactory,
    get_equity_pledge,
    get_equity_pledge_ratio_rank,
)
from .modules.restricted import (
    RestrictedReleaseFactory,
    get_restricted_release,
    get_restricted_release_calendar,
)
from .modules.convertbond import (
    ConvertBondFactory,
    get_convert_bond_list,
    get_convert_bond_info,
    get_convert_bond_hist,
    get_convert_bond_spot,
    get_convert_bond_premium,
    get_convert_bond_by_stock,
    get_convert_bond_quote,
    calculate_conversion_value,
    calculate_premium_rate,
    get_convert_bond_daily,
)
from .modules.callauction import (
    CallAuctionFactory,
    get_call_auction,
    get_call_auction_batch,
)
from .modules.lof import (
    LOFFactory,
    get_lof_list,
    get_lof_hist_data,
    get_lof_spot,
    get_lof_nav,
)
from .modules.fundof import (
    FOFFactory,
    get_fof_list,
    get_fof_nav,
    get_fof_info,
)
from .modules.optiongreeks import (
    OptionGreeksFactory,
    get_option_greeks,
    calculate_option_implied_vol,
    calculate_implied_vol,
    calculate_greeks,
    black_scholes_price,
)
from .modules.indexweights import (
    IndexWeightsFactory,
    get_index_weights,
    get_index_weights_history,
    get_index_info,
)
from .modules.companydepth import (
    CompanyDepthFactory,
    get_security_status,
    get_name_history,
    get_management_info,
    get_employee_info,
    get_listing_info,
    get_industry_info,
)
from .modules.dividendcalc import (
    DividendCalcFactory,
    calculate_ex_rights_price,
    calculate_adjust_price,
    get_stock_bonus,
    get_rights_issue,
    get_dividend_by_date,
)
from .modules.sharechangedepth import (
    ShareChangeDepthFactory,
    get_freeze_info,
    get_capital_change,
    get_topholder_change,
    get_major_holder_trade,
)
from .modules.industryanalytics import (
    IndustryAnalyticsFactory,
    get_stock_industry,
    get_industry_performance,
    get_concept_performance,
    search_concept,
    get_all_concept_stocks as get_all_concept_stocks_module,
    get_all_industries,
    filter_stocks_by_industry,
    query_industry_sw,
)
from .modules.northbounddepth import (
    NorthboundDepthFactory,
    get_north_stock_detail,
    get_north_quota_info,
    get_north_calendar,
    compute_north_money_signal,
)
from .modules.macroakshare import (
    MacroAkShareFactory,
    get_macro_gdp,
    get_macro_cpi,
    get_macro_ppi,
    get_macro_pmi,
    get_macro_interest_rate,
    get_macro_exchange_rate,
    get_macro_china_gdp,
    get_macro_china_cpi,
    get_macro_china_ppi,
    get_macro_china_pmi,
    get_macro_china_interest_rate,
    get_macro_china_exchange_rate,
)
from .modules.futuresmargin import (
    FuturesMarginFactory,
    get_contract_multiplier,
    get_margin_rate_for_contract,
    calculate_position_value,
    calculate_required_margin,
    get_contract_info,
    get_margin_rate,
    CONTRACT_MULTIPLIERS,
)
from .modules.shareholderdepth import (
    ShareholderDepthFactory,
    get_shareholder_structure,
    get_shareholder_concentration,
)
from .modules.goodwill import (
    GoodwillFactory,
    get_goodwill_data,
    get_goodwill_impairment,
    get_goodwill_by_industry,
)
from .modules.esg import (
    ESGFactory,
    get_esg_rating,
    get_esg_rating_rank,
)
from .modules.special import (
    SpecialDataFactory,
    get_chip_distribution,
    get_broker_forecast,
    get_institutional_research,
)
from .jq_compat import (
    get_price,
    get_bars,
    history,
    attribute_history,
    get_valuation,
    get_index_valuation,
    get_all_securities,
    get_security_info,
    get_shifted_date,
    get_previous_trade_date,
    get_next_trade_date,
    transform_date,
    is_trade_date,
    get_trade_dates_between,
    count_trade_dates_between,
    get_concepts,
    get_concept_stocks,
    get_concept,
    get_all_concepts,
    get_locked_shares,
    get_fund_info,
    get_fundamentals_continuously,
    get_recent_limit_up_stock,
    get_recent_limit_down_stock,
    get_mtss,
    get_margincash_stocks,
    get_marginsec_stocks,
    get_billboard_list,
    get_institutional_holdings,
    get_dominant_future,
    get_futures_info,
    get_future_contracts,
    get_north_factor,
    get_comb_factor,
    get_factor_momentum,
    MA,
    EMA,
    MACD,
    KDJ,
    RSI,
    BOLL,
)

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
    # 北向资金多源API
    "get_northbound_flow_multi_source",
    "get_northbound_holdings_multi_source",
    "get_northbound_top_stocks_multi_source",
    # 资金流多源API
    "get_stock_fund_flow_multi_source",
    "get_sector_fund_flow_multi_source",
    "get_main_fund_flow_rank_multi_source",
    # 龙虎榜多源API
    "get_dragon_tiger_list_multi_source",
    "get_dragon_tiger_summary_multi_source",
    # 涨跌停多源API
    "get_limit_up_pool_multi_source",
    "get_limit_down_pool_multi_source",
    # 大宗交易多源API
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
    "get_macro_china_gdp",
    "get_macro_china_cpi",
    "get_macro_china_ppi",
    "get_macro_china_pmi",
    "get_macro_china_interest_rate",
    "get_macro_china_exchange_rate",
    "get_adapter",
    "get_cache_manager",
    # JQ Compatibility (Merge from jk2bt)
    "get_price",
    "get_bars",
    "history",
    "attribute_history",
    "get_valuation",
    "get_index_valuation",
    "risk",
    "strategy",
]

from . import risk
from . import strategy


def get_basic_info(
    symbol: str,
    source: Literal["eastmoney", "sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取股票基础信息

    Args:
        symbol: 股票代码 (e.g. '600000')
        source: 数据源 ('sina', 'eastmoney')

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
    """Get historical market data

    Args:
        symbol: 股票代码 (e.g. '600000')
        interval: 时间间隔 ('minute','hour','day','week','month','year')
        interval_multiplier: 时间间隔倍数 (e.g. 5 for 5 minutes)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        adjust: 复权类型 ('none','qfq','hfq')
        source: 数据源 ('sina', 'lixinger', 'eastmoney', 'eastmoney_direct')

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
    df = provider.get_hist_data()
    return apply_data_filter(df, columns, row_filter)


def get_realtime_data(
    symbol: str | None = None,
    source: Literal["eastmoney", "eastmoney_direct", "xueqiu"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Get real-time market quotes

    Args:
        symbol: 股票代码 (如 "600000")
        source: 数据源 ('eastmoney', 'eastmoney_direct', 'xueqiu')
        注意：实时数据目前不支持 sina 数据源

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
    df = provider.get_current_data()
    return apply_data_filter(df, columns, row_filter)


def get_news_data(
    symbol: str,
    source: Literal["eastmoney", "sina"] = "eastmoney",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取个股新闻数据

    Args:
        symbol: 股票代码 (如 "300059")
        source: 数据源 ('eastmoney', 'sina')

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
    df = provider.get_news_data()
    return apply_data_filter(df, columns, row_filter)


def get_balance_sheet(
    symbol: str,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取资产负债表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 资产负债表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    df = provider.get_balance_sheet()
    return apply_data_filter(df, columns, row_filter)


def get_income_statement(
    symbol: str,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取利润表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 利润表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    df = provider.get_income_statement()
    return apply_data_filter(df, columns, row_filter)


def get_cash_flow(
    symbol: str,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取现金流量表数据

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ("sina")

    Returns:
        pd.DataFrame: 现金流量表数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    df = provider.get_cash_flow()
    return apply_data_filter(df, columns, row_filter)


def get_financial_metrics(
    symbol: str,
    source: Literal["sina", "eastmoney_direct", "lixinger"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取三大财务报表关键指标

    Args:
        symbol: 股票代码 (如 "600600")
        source: 数据源 ('sina', 'eastmoney_direct', 'lixinger')

    Returns:
        pd.DataFrame: 财务关键指标数据
    """
    provider = FinancialDataFactory.get_provider(source, symbol=symbol)
    df = provider.get_financial_metrics()
    return apply_data_filter(df, columns, row_filter)


def get_inner_trade_data(
    symbol: str,
    source: Literal["xueqiu"] = "xueqiu",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取雪球内部交易数据

    Args:
        symbol: 股票代码，如"600000"
        source: 数据源 (目前支持 "xueqiu")

    Returns:
        pd.DataFrame: 内部交易数据
    """
    provider = InsiderDataFactory.get_provider(source, symbol=symbol)
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
    df = provider.get_hist_data()
    return apply_data_filter(df, columns, row_filter)


def get_futures_realtime_data(
    symbol: str | None = None,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
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
        df = provider.get_current_data()
        return apply_data_filter(df, columns, row_filter)
    df = provider.get_all_quotes()
    return apply_data_filter(df, columns, row_filter)


def get_futures_main_contracts(
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
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
    df = provider.get_main_contracts()
    return apply_data_filter(df, columns, row_filter)


# ==================== Options API ====================


def get_options_chain(
    underlying_symbol: str,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
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
    df = provider.get_options_chain()
    return apply_data_filter(df, columns, row_filter)


def get_options_realtime(
    symbol: str | None = None,
    underlying_symbol: str | None = None,
    source: Literal["sina"] = "sina",
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
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
        df = provider.get_options_realtime(symbol)
        return apply_data_filter(df, columns, row_filter)
    provider = OptionsDataFactory.get_provider(source, underlying_symbol=underlying_symbol)
    df = provider.get_options_realtime("")
    return apply_data_filter(df, columns, row_filter)


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
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
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
    """获取股票基础信息（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。

    Args:
        symbol: 股票代码 (e.g. '600000')
        sources: 数据源列表，默认 ["sina", "eastmoney"]

    Returns:
        pd.DataFrame: 股票基础信息
    """
    from .modules.info import InfoDataFactory

    return _get_data_multi_source(
        method_name="get_basic_info",
        symbol=symbol,
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        factory_class=InfoDataFactory,
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
    """获取个股新闻（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。

    Args:
        symbol: 股票代码 (如 "300059")
        sources: 数据源列表，默认 ["eastmoney", "sina"]

    Returns:
        pd.DataFrame: 新闻数据
    """
    from .modules.news import NewsDataFactory

    return _get_data_multi_source(
        method_name="get_news_data",
        symbol=symbol,
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        factory_class=NewsDataFactory,
        default_sources=["eastmoney", "sina"],
    )


def get_inner_trade_data_multi_source(
    symbol: str,
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """获取内部交易数据（多数据源自动切换）

    自动尝试多个数据源，当一个源失败时自动切换到下一个。

    Args:
        symbol: 股票代码 (如 "600000")
        sources: 数据源列表，默认 ["xueqiu"]

    Returns:
        pd.DataFrame: 内部交易数据
    """
    from .modules.insider import InsiderDataFactory

    return _get_data_multi_source(
        method_name="get_inner_trade_data",
        symbol=symbol,
        sources=sources,
        columns=columns,
        row_filter=row_filter,
        factory_class=InsiderDataFactory,
        default_sources=["xueqiu"],
    )


def get_financial_data_multi_source(
    symbol: str,
    data_type: Literal["balance_sheet", "income_statement", "cash_flow"],
    sources: list[str] | None = None,
    columns: list[str] | None = None,
    row_filter: dict[str, Any] | None = None,
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
    from .modules.financial import FinancialDataFactory

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
        factory_class=FinancialDataFactory,
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
    from .modules.margin import MarginFactory

    provider = MarginFactory.get_provider("eastmoney", symbol=symbol)
    return provider.get_margin_data(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


# 业绩预测别名
def get_forecast_data(symbol: str, **kwargs) -> pd.DataFrame:
    """获取业绩预测(jk2bt兼容)"""
    from .modules.performance import PerformanceFactory

    provider = PerformanceFactory.get_provider("eastmoney", symbol=symbol)
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
    from .modules.industry import IndustryFactory

    provider = IndustryFactory.get_provider("eastmoney", industry_name="")
    return provider.get_industry_classify(level=f"sw_l{level}")


def get_industry_stocks_module(industry_name: str, **kwargs) -> list:
    """获取行业成分股(jk2bt兼容)"""
    from .modules.industry import IndustryFactory

    provider = IndustryFactory.get_provider("eastmoney", industry_name=industry_name)
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
    from .modules.macroakshare import get_macro_china_gdp as _gdp

    return _gdp(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_cpi(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国CPI(jk2bt兼容)"""
    from .modules.macroakshare import get_macro_china_cpi as _cpi

    return _cpi(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_ppi(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国PPI(jk2bt兼容)"""
    from .modules.macroakshare import get_macro_china_ppi as _ppi

    return _ppi(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_pmi(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国PMI(jk2bt兼容)"""
    from .modules.macroakshare import get_macro_china_pmi as _pmi

    return _pmi(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_interest_rate(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国利率(jk2bt兼容)"""
    from .modules.macroakshare import get_macro_china_interest_rate as _rate

    return _rate(start_date=start_date or "1970-01-01", end_date=end_date or "2030-12-31")


def get_macro_china_exchange_rate(start_date=None, end_date=None, **kwargs) -> pd.DataFrame:
    """获取中国汇率(jk2bt兼容)"""
    from .modules.macroakshare import get_macro_china_exchange_rate as _fx

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
