"""
Mock fixtures for fund flow data.

Provides sample data for testing fundflow module without network access.
"""

import pandas as pd


def get_mock_stock_fund_flow_data() -> pd.DataFrame:
    """
    Get mock stock fund flow data.

    Returns:
        pd.DataFrame: Mock stock fund flow data
    """
    return pd.DataFrame({
        "日期": ["2024-01-15", "2024-01-16", "2024-01-17"],
        "股票代码": ["600000", "600000", "600000"],
        "股票简称": ["浦发银行", "浦发银行", "浦发银行"],
        "收盘价": [15.50, 15.65, 15.40],
        "涨跌幅": [1.2, 0.97, -1.6],
        "主力净流入": [50000000, 35000000, -28000000],
        "小单净流入": [-15000000, -12000000, 8000000],
        "中单净流入": [-20000000, -15000000, 12000000],
        "大单净流入": [30000000, 20000000, -18000000],
        "超大单净流入": [20000000, 15000000, -10000000],
    })


def get_mock_sector_fund_flow_data() -> pd.DataFrame:
    """
    Get mock sector fund flow data.

    Returns:
        pd.DataFrame: Mock sector fund flow data
    """
    return pd.DataFrame({
        "名称": ["电子", "半导体", "计算机"],
        "今日主力净流入": [2487623680, 1923111424, 1500000000],
        "今日主力净流入占比": [-0.13, -0.15, 0.12],
        "今日超大单净流入": [1500000000, 1200000000, 900000000],
        "今日大单净流入": [987623680, 723111424, 600000000],
        "今日中单净流入": [-500000000, -400000000, -300000000],
        "今日小单净流入": [-1987623680, -1523111424, -1200000000],
        "领涨股": ["深科技", "兆易创新", "中科曙光"],
        "领涨股涨跌幅": [5.2, 3.8, 4.1],
    })


def get_mock_industry_list_data() -> pd.DataFrame:
    """
    Get mock industry list data.

    Returns:
        pd.DataFrame: Mock industry list
    """
    return pd.DataFrame({
        "板块代码": ["0", "1", "2"],
        "板块名称": ["电子", "半导体", "计算机"],
        "板块类型": ["industry", "industry", "industry"],
    })


def get_mock_concept_list_data() -> pd.DataFrame:
    """
    Get mock concept list data.

    Returns:
        pd.DataFrame: Mock concept list
    """
    return pd.DataFrame({
        "板块代码": ["100", "101", "102"],
        "板块名称": ["人工智能", "新能源", "芯片"],
        "板块类型": ["concept", "concept", "concept"],
    })