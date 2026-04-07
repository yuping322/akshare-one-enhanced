"""
Mock fixtures for northbound capital data.

Provides sample data for testing northbound module without network access.
"""

import pandas as pd


def get_mock_northbound_flow_data() -> pd.DataFrame:
    """
    Get mock northbound flow data matching akshare stock_hsgt_hist_em format.

    Returns:
        pd.DataFrame: Mock northbound flow data with Chinese column names
    """
    return pd.DataFrame({
        "日期": ["2024-01-15", "2024-01-16", "2024-01-17"],
        "当日成交净买额": [50.25, -30.18, 42.56],  # 亿元
        "买入成交额": [150.50, 120.30, 145.60],  # 亿元
        "卖出成交额": [100.25, 150.48, 103.04],  # 亿元
        "当日余额": [1550.25, 1520.07, 1562.63],  # 亿元
    })


def get_mock_northbound_holdings_individual_data() -> pd.DataFrame:
    """
    Get mock northbound holdings data for individual stock.

    Returns:
        pd.DataFrame: Mock holdings data for individual stock
    """
    return pd.DataFrame({
        "日期": ["2024-01-15", "2024-01-16", "2024-01-17"],
        "持股数量": [15000000, 15500000, 16000000],
        "持股市值": [225000000, 232500000, 240000000],
        "持股占比": [3.5, 3.6, 3.7],
        "持股变化": [100000, 500000, 500000],
    })


def get_mock_northbound_holdings_all_data() -> pd.DataFrame:
    """
    Get mock northbound holdings data for all stocks.

    Returns:
        pd.DataFrame: Mock holdings data for all stocks
    """
    return pd.DataFrame({
        "代码": ["600000", "600001", "000001", "300001", "600002"],
        "名称": ["浦发银行", "邯郸钢铁", "平安银行", "特锐德", "齐鲁石化"],
        "持股日期": ["2024-01-17", "2024-01-17", "2024-01-17", "2024-01-17", "2024-01-17"],
        "持股数量(股)": [15000000, 8500000, 12000000, 6500000, 9200000],
        "持股市值(元)": [225000000, 127500000, 180000000, 97500000, 138000000],
        "持股占比(%)": [3.5, 2.8, 4.2, 1.9, 3.1],
        "持股数量增减": [500000, 300000, 450000, 200000, 350000],
    })


def get_mock_northbound_top_stocks_data() -> pd.DataFrame:
    """
    Get mock northbound top stocks ranking data.

    Returns:
        pd.DataFrame: Mock top stocks data
    """
    return pd.DataFrame({
        "代码": ["600000", "600519", "000001", "300750", "600036"],
        "名称": ["浦发银行", "贵州茅台", "平安银行", "宁德时代", "招商银行"],
        "今日持股-股数": [150000000, 85000000, 120000000, 65000000, 92000000],
        "今日持股-市值": [2250000000, 1275000000, 1800000000, 975000000, 1380000000],
        "今日持股-占流通股比": [5.5, 6.8, 7.2, 4.9, 5.1],
        "持股市值变化-1日": [22500000, 12750000, 18000000, 9750000, 13800000],
        "5日增持估计-市值": [112500000, 63750000, 90000000, 48750000, 69000000],
    })