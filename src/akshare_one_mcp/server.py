"""MCP server implementation for akshare-one.

Provides tools for accessing Chinese stock market data through MCP protocol.
"""

from datetime import datetime
from typing import Annotated, Literal

import akshare as ak
from fastmcp import FastMCP
from pydantic import Field

import akshare_one as ako
from akshare_one import indicators

mcp = FastMCP(name="akshare-one-mcp")


@mcp.tool
def get_hist_data(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    interval: Annotated[
        Literal["minute", "hour", "day", "week", "month", "year"],
        Field(description="Time interval"),
    ] = "day",
    interval_multiplier: Annotated[int, Field(description="Interval multiplier", ge=1)] = 1,
    start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")] = "2030-12-31",
    adjust: Annotated[Literal["none", "qfq", "hfq"], Field(description="Adjustment type")] = "none",
    source: Annotated[
        Literal["eastmoney", "eastmoney_direct", "sina"],
        Field(description="Data source"),
    ] = "sina",
    indicators_list: Annotated[
        list[
            Literal[
                "SMA",
                "EMA",
                "RSI",
                "MACD",
                "BOLL",
                "STOCH",
                "ATR",
                "CCI",
                "ADX",
                "WILLR",
                "OBV",
                "TRIX",
                "ROC",
                "MOM",
            ]
        ],
        Field(description="List of technical indicators to calculate"),
    ] = None,
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = None,
) -> str:
    """Get historical stock market data with optional technical indicators.

    Returns OHLCV data with optional technical indicators calculated.
    """
    df = ako.get_hist_data(
        symbol=symbol,
        interval=interval,
        interval_multiplier=interval_multiplier,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
        source=source,
    )

    if indicators_list:
        indicator_map = {
            "SMA": (indicators.get_sma, {"window": 20}),
            "EMA": (indicators.get_ema, {"window": 20}),
            "RSI": (indicators.get_rsi, {"window": 14}),
            "MACD": (
                indicators.get_macd,
                {"fast_period": 12, "slow_period": 26, "signal_period": 9},
            ),
            "BOLL": (
                indicators.get_bollinger_bands,
                {"window": 20, "num_std": 2},
            ),
            "STOCH": (
                indicators.get_stoch,
                {"window": 14, "smooth_d": 3, "smooth_k": 3},
            ),
            "ATR": (indicators.get_atr, {"window": 14}),
            "CCI": (indicators.get_cci, {"window": 20}),
            "ADX": (indicators.get_adx, {"window": 14}),
            "WILLR": (indicators.get_willr, {"window": 14}),
            "OBV": (indicators.get_obv, {}),
            "TRIX": (indicators.get_trix, {"window": 30}),
            "ROC": (indicators.get_roc, {"window": 10}),
            "MOM": (indicators.get_mom, {"window": 10}),
        }
        temp = []
        for indicator in indicators_list:
            if indicator in indicator_map:
                func, params = indicator_map[indicator]
                indicator_df = func(df, **params)
                temp.append(indicator_df)
        if temp:
            df = df.join(temp)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_realtime_data(
    symbol: Annotated[str | None, Field(description="Stock symbol/ticker (e.g. '000001')")] = None,
    source: Annotated[
        Literal["xueqiu", "eastmoney", "eastmoney_direct"],
        Field(description="Data source"),
    ] = "xueqiu",
) -> str:
    """Get real-time stock market data. 'eastmoney_direct' support all A,B,H shares"""
    df = ako.get_realtime_data(symbol=symbol, source=source)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_news_data(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """Get stock-related news data."""
    df = ako.get_news_data(symbol=symbol, source="eastmoney")
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_balance_sheet(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """Get company balance sheet data."""
    df = ako.get_balance_sheet(symbol=symbol, source="sina")
    if recent_n is not None:
        df = df.head(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_income_statement(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """Get company income statement data."""
    df = ako.get_income_statement(symbol=symbol, source="sina")
    if recent_n is not None:
        df = df.head(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_cash_flow(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    source: Annotated[Literal["sina"], Field(description="Data source")] = "sina",
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """Get company cash flow statement data."""
    df = ako.get_cash_flow(symbol=symbol, source=source)
    if recent_n is not None:
        df = df.head(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_inner_trade_data(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
) -> str:
    """Get company insider trading data."""
    df = ako.get_inner_trade_data(symbol, source="xueqiu")
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_financial_metrics(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = 10,
) -> str:
    """Get key financial metrics from the three major financial statements."""
    df = ako.get_financial_metrics(symbol)
    if recent_n is not None:
        df = df.head(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_time_info() -> dict:
    """Get current time with ISO format, timestamp, and the last trading day."""
    local_time = datetime.now().astimezone()
    current_date = local_time.date()

    # Get trading calendar
    trade_date_df = ak.tool_trade_date_hist_sina()
    trade_dates = [d for d in trade_date_df["trade_date"]]

    # Filter dates <= current date and sort descending
    past_dates = sorted([d for d in trade_dates if d <= current_date], reverse=True)
    # Find the most recent trading day
    last_trading_day = past_dates[0].strftime("%Y-%m-%d") if past_dates else None
    return {
        "iso_format": local_time.isoformat(),
        "timestamp": local_time.timestamp(),
        "last_trading_day": last_trading_day,
    }


@mcp.tool
def get_hist_data_multi_source(
    symbol: Annotated[str, Field(description="Stock symbol/ticker (e.g. '000001')")],
    interval: Annotated[
        Literal["minute", "hour", "day", "week", "month", "year"],
        Field(description="Time interval"),
    ] = "day",
    interval_multiplier: Annotated[int, Field(description="Interval multiplier", ge=1)] = 1,
    start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")] = "2030-12-31",
    adjust: Annotated[Literal["none", "qfq", "hfq"], Field(description="Adjustment type")] = "none",
    sources: Annotated[
        list[str] | None,
        Field(description="List of data sources to try in order"),
    ] = None,
    recent_n: Annotated[
        int | None, Field(description="Number of most recent records to return", ge=1)
    ] = None,
) -> str:
    """Get historical stock data with automatic multi-source failover.

    Automatically tries multiple data sources and falls back to the next
    when one fails. Daily data is cached for 24 hours.
    """
    from akshare_one import get_hist_data_multi_source as _get_hist_data_multi_source

    df = _get_hist_data_multi_source(
        symbol=symbol,
        interval=interval,
        interval_multiplier=interval_multiplier,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
        sources=sources,
    )

    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_realtime_data_multi_source(
    symbol: Annotated[str | None, Field(description="Stock symbol/ticker (e.g. '000001')")] = None,
    sources: Annotated[
        list[str] | None,
        Field(description="List of data sources to try in order"),
    ] = None,
) -> str:
    """Get real-time stock data with automatic multi-source failover."""
    from akshare_one import get_realtime_data_multi_source as _get_realtime_data_multi_source

    df = _get_realtime_data_multi_source(symbol=symbol, sources=sources)
    return df.to_json(orient="records") or "[]"


# ==================== Fund Flow MCP Tools ====================


@mcp.tool
def get_stock_fund_flow(
    symbol: Annotated[str, Field(description="Stock symbol (e.g. '600000')")],
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get individual stock fund flow data.

    Returns fund flow data including main net inflow, super large orders,
    large orders, medium orders, and small orders.
    """
    from akshare_one.modules.fundflow import get_stock_fund_flow as _get_stock_fund_flow

    df = _get_stock_fund_flow(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_sector_fund_flow(
    sector_type: Annotated[Literal["industry", "concept"], Field(description="Sector type")],
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
) -> str:
    """Get sector fund flow data (industry or concept sectors)."""
    from akshare_one.modules.fundflow import get_sector_fund_flow as _get_sector_fund_flow

    df = _get_sector_fund_flow(sector_type=sector_type, start_date=start_date, end_date=end_date)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_main_fund_flow_rank(
    date: Annotated[str, Field(description="Query date (YYYY-MM-DD)")],
    indicator: Annotated[
        Literal["net_inflow", "net_inflow_rate"], Field(description="Ranking indicator")
    ] = "net_inflow",
) -> str:
    """Get main fund flow ranking by date."""
    from akshare_one.modules.fundflow import get_main_fund_flow_rank as _get_main_fund_flow_rank

    df = _get_main_fund_flow_rank(date=date, indicator=indicator)
    return df.to_json(orient="records") or "[]"


# ==================== Northbound MCP Tools ====================


@mcp.tool
def get_northbound_flow(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    market: Annotated[Literal["sh", "sz", "all"], Field(description="Market type")] = "all",
) -> str:
    """Get northbound capital flow data (Shanghai/Shenzhen Connect)."""
    from akshare_one.modules.northbound import get_northbound_flow as _get_northbound_flow

    df = _get_northbound_flow(start_date=start_date, end_date=end_date, market=market)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_northbound_holdings(
    symbol: Annotated[str, Field(description="Stock symbol (e.g. '600000')")],
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get northbound capital holdings for a specific stock."""
    from akshare_one.modules.northbound import get_northbound_holdings as _get_northbound_holdings

    df = _get_northbound_holdings(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_northbound_top_stocks(
    date: Annotated[str, Field(description="Query date (YYYY-MM-DD)")],
    market: Annotated[Literal["sh", "sz", "all"], Field(description="Market type")] = "all",
    top_n: Annotated[int, Field(description="Number of top stocks to return", ge=1, le=1000)] = 100,
) -> str:
    """Get northbound capital top stocks ranking."""
    from akshare_one.modules.northbound import (
        get_northbound_top_stocks as _get_northbound_top_stocks,
    )

    df = _get_northbound_top_stocks(date=date, market=market, top_n=top_n)
    return df.to_json(orient="records") or "[]"


# ==================== Dragon Tiger (LHB) MCP Tools ====================


@mcp.tool
def get_dragon_tiger_list(
    date: Annotated[str, Field(description="Query date (YYYY-MM-DD)")],
    symbol: Annotated[
        str | None, Field(description="Stock symbol (optional, None for all stocks)")
    ] = None,
) -> str:
    """Get dragon tiger list (trading anomaly data) for a specific date."""
    from akshare_one.modules.lhb import get_dragon_tiger_list as _get_dragon_tiger_list

    df = _get_dragon_tiger_list(date=date, symbol=symbol)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_dragon_tiger_summary(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")],
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")],
    group_by: Annotated[
        Literal["stock", "broker", "reason"], Field(description="Grouping dimension")
    ] = "stock",
) -> str:
    """Get dragon tiger list summary statistics."""
    from akshare_one.modules.lhb import get_dragon_tiger_summary as _get_dragon_tiger_summary

    df = _get_dragon_tiger_summary(start_date=start_date, end_date=end_date, group_by=group_by)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_dragon_tiger_broker_stats(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")],
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")],
    top_n: Annotated[int, Field(description="Number of top brokers to return", ge=1, le=100)] = 50,
) -> str:
    """Get broker statistics from dragon tiger list."""
    from akshare_one.modules.lhb import (
        get_dragon_tiger_broker_stats as _get_dragon_tiger_broker_stats,
    )

    df = _get_dragon_tiger_broker_stats(start_date=start_date, end_date=end_date, top_n=top_n)
    return df.to_json(orient="records") or "[]"


# ==================== Limit Up/Down MCP Tools ====================


@mcp.tool
def get_limit_up_pool(
    date: Annotated[str, Field(description="Query date (YYYY-MM-DD)")],
) -> str:
    """Get limit up pool (stocks hitting upper limit)."""
    from akshare_one.modules.limitup import get_limit_up_pool as _get_limit_up_pool

    df = _get_limit_up_pool(date=date)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_limit_down_pool(
    date: Annotated[str, Field(description="Query date (YYYY-MM-DD)")],
) -> str:
    """Get limit down pool (stocks hitting lower limit)."""
    from akshare_one.modules.limitup import get_limit_down_pool as _get_limit_down_pool

    df = _get_limit_down_pool(date=date)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_limit_up_stats(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")],
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")],
) -> str:
    """Get limit up/down statistics."""
    from akshare_one.modules.limitup import get_limit_up_stats as _get_limit_up_stats

    df = _get_limit_up_stats(start_date=start_date, end_date=end_date)
    return df.to_json(orient="records") or "[]"


# ==================== Disclosure MCP Tools ====================


@mcp.tool
def get_disclosure_news(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    category: Annotated[
        Literal["all", "dividend", "repurchase", "st", "major_event"],
        Field(description="News category"),
    ] = "all",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get disclosure news data (announcements, dividends, repurchases, ST risk)."""
    from akshare_one.modules.disclosure import get_disclosure_news as _get_disclosure_news

    df = _get_disclosure_news(
        symbol=symbol, start_date=start_date, end_date=end_date, category=category
    )
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_dividend_data(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get dividend data for stocks."""
    from akshare_one.modules.disclosure import get_dividend_data as _get_dividend_data

    df = _get_dividend_data(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_repurchase_data(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get stock repurchase data."""
    from akshare_one.modules.disclosure import get_repurchase_data as _get_repurchase_data

    df = _get_repurchase_data(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_st_delist_data(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get ST/delist risk data for stocks."""
    from akshare_one.modules.disclosure import get_st_delist_data as _get_st_delist_data

    df = _get_st_delist_data(symbol=symbol)
    if recent_n is not None:
        df = df.head(recent_n)
    return df.to_json(orient="records") or "[]"


# ==================== Macro MCP Tools ====================


@mcp.tool
def get_lpr_rate(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get LPR (Loan Prime Rate) interest rate data."""
    from akshare_one.modules.macro import get_lpr_rate as _get_lpr_rate

    df = _get_lpr_rate(start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_pmi_index(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    pmi_type: Annotated[
        Literal["manufacturing", "non_manufacturing", "caixin"],
        Field(description="PMI type"),
    ] = "manufacturing",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get PMI (Purchasing Managers' Index) data."""
    from akshare_one.modules.macro import get_pmi_index as _get_pmi_index

    df = _get_pmi_index(start_date=start_date, end_date=end_date, pmi_type=pmi_type)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_cpi_data(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get CPI (Consumer Price Index) data."""
    from akshare_one.modules.macro import get_cpi_data as _get_cpi_data

    df = _get_cpi_data(start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_ppi_data(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get PPI (Producer Price Index) data."""
    from akshare_one.modules.macro import get_ppi_data as _get_ppi_data

    df = _get_ppi_data(start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_m2_supply(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get M2 money supply data."""
    from akshare_one.modules.macro import get_m2_supply as _get_m2_supply

    df = _get_m2_supply(start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_shibor_rate(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get Shibor (Shanghai Interbank Offered Rate) interest rate data."""
    from akshare_one.modules.macro import get_shibor_rate as _get_shibor_rate

    df = _get_shibor_rate(start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_social_financing(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get social financing scale data."""
    from akshare_one.modules.macro import get_social_financing as _get_social_financing

    df = _get_social_financing(start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


# ==================== Block Deal MCP Tools ====================


@mcp.tool
def get_block_deal(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get block deal (大宗交易) transaction details."""
    from akshare_one.modules.blockdeal import get_block_deal as _get_block_deal

    df = _get_block_deal(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_block_deal_summary(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    group_by: Annotated[
        Literal["stock", "date", "broker"],
        Field(description="Grouping dimension"),
    ] = "stock",
) -> str:
    """Get block deal (大宗交易) summary statistics."""
    from akshare_one.modules.blockdeal import get_block_deal_summary as _get_block_deal_summary

    df = _get_block_deal_summary(start_date=start_date, end_date=end_date, group_by=group_by)
    return df.to_json(orient="records") or "[]"


# ==================== Margin MCP Tools ====================


@mcp.tool
def get_margin_data(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get margin financing (融资融券) data for stocks."""
    from akshare_one.modules.margin import get_margin_data as _get_margin_data

    df = _get_margin_data(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_margin_summary(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    market: Annotated[
        Literal["sh", "sz", "all"],
        Field(description="Market type"),
    ] = "all",
) -> str:
    """Get margin financing (融资融券) summary data by market."""
    from akshare_one.modules.margin import get_margin_summary as _get_margin_summary

    df = _get_margin_summary(start_date=start_date, end_date=end_date, market=market)
    return df.to_json(orient="records") or "[]"


# ==================== Equity Pledge MCP Tools ====================


@mcp.tool
def get_equity_pledge(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get equity pledge (股权质押) data for stocks."""
    from akshare_one.modules.pledge import get_equity_pledge as _get_equity_pledge

    df = _get_equity_pledge(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_equity_pledge_ratio_rank(
    date: Annotated[str, Field(description="Query date (YYYY-MM-DD)")],
    top_n: Annotated[int, Field(description="Number of top stocks to return", ge=1, le=500)] = 100,
) -> str:
    """Get equity pledge (股权质押) ratio ranking."""
    from akshare_one.modules.pledge import (
        get_equity_pledge_ratio_rank as _get_equity_pledge_ratio_rank,
    )

    df = _get_equity_pledge_ratio_rank(date=date, top_n=top_n)
    return df.to_json(orient="records") or "[]"


# ==================== Restricted Release MCP Tools ====================


@mcp.tool
def get_restricted_release(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get restricted stock release (限售解禁) data."""
    from akshare_one.modules.restricted import get_restricted_release as _get_restricted_release

    df = _get_restricted_release(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_restricted_release_calendar(
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
) -> str:
    """Get restricted stock release (限售解禁) calendar."""
    from akshare_one.modules.restricted import (
        get_restricted_release_calendar as _get_restricted_release_calendar,
    )

    df = _get_restricted_release_calendar(start_date=start_date, end_date=end_date)
    return df.to_json(orient="records") or "[]"


# ==================== Goodwill MCP Tools ====================


@mcp.tool
def get_goodwill_data(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get goodwill (商誉) data for stocks."""
    from akshare_one.modules.goodwill import get_goodwill_data as _get_goodwill_data

    df = _get_goodwill_data(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_goodwill_impairment(
    date: Annotated[str, Field(description="Query date (YYYY-MM-DD)")],
) -> str:
    """Get goodwill impairment (商誉减值) expectations."""
    from akshare_one.modules.goodwill import get_goodwill_impairment as _get_goodwill_impairment

    df = _get_goodwill_impairment(date=date)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_goodwill_by_industry(
    date: Annotated[str, Field(description="Query date (YYYY-MM-DD)")],
) -> str:
    """Get goodwill (商誉) statistics by industry."""
    from akshare_one.modules.goodwill import get_goodwill_by_industry as _get_goodwill_by_industry

    df = _get_goodwill_by_industry(date=date)
    return df.to_json(orient="records") or "[]"


# ==================== ESG MCP Tools ====================


@mcp.tool
def get_esg_rating(
    symbol: Annotated[
        str | None, Field(description="Stock symbol (e.g. '600000'), None for all")
    ] = None,
    start_date: Annotated[str, Field(description="Start date (YYYY-MM-DD)")] = "1970-01-01",
    end_date: Annotated[str, Field(description="End date (YYYY-MM-DD)")] = "2030-12-31",
    recent_n: Annotated[int | None, Field(description="Return most recent N records", ge=1)] = None,
) -> str:
    """Get ESG rating data for stocks."""
    from akshare_one.modules.esg import get_esg_rating as _get_esg_rating

    df = _get_esg_rating(symbol=symbol, start_date=start_date, end_date=end_date)
    if recent_n is not None:
        df = df.tail(recent_n)
    return df.to_json(orient="records") or "[]"


@mcp.tool
def get_esg_rating_rank(
    date: Annotated[str, Field(description="Query date (YYYY-MM-DD)")],
    industry: Annotated[str | None, Field(description="Industry filter (optional)")] = None,
    top_n: Annotated[int, Field(description="Number of top stocks to return", ge=1, le=500)] = 100,
) -> str:
    """Get ESG rating rankings."""
    from akshare_one.modules.esg import get_esg_rating_rank as _get_esg_rating_rank

    df = _get_esg_rating_rank(date=date, industry=industry, top_n=top_n)
    return df.to_json(orient="records") or "[]"


def run_server() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    run_server()
