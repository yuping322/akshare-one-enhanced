"""
Mock fixtures for block deal data.

Provides sample data for testing blockdeal module without network access.
"""

import pandas as pd


def get_mock_block_deal_data() -> pd.DataFrame:
    """
    Get mock block deal data.

    Returns:
        pd.DataFrame: Mock block deal data
    """
    return pd.DataFrame({
        "交易日期": ["2024-01-15", "2024-01-16", "2024-01-17"],
        "证券代码": ["600000", "000001", "300001"],
        "证券简称": ["浦发银行", "平安银行", "特锐德"],
        "成交价格": [15.50, 12.30, 28.90],
        "成交量": [5000000, 3500000, 2100000],
        "成交金额": [77500000, 43050000, 60690000],
        "买方营业部": ["机构专用", "中信证券", "国泰君安"],
        "卖方营业部": ["海通证券", "华泰证券", "招商证券"],
    })


def get_mock_block_deal_summary_data() -> pd.DataFrame:
    """
    Get mock block deal summary data.

    Returns:
        pd.DataFrame: Mock block deal summary data
    """
    return pd.DataFrame({
        "证券代码": ["600000", "000001", "300001"],
        "证券简称": ["浦发银行", "平安银行", "特锐德"],
        "交易次数": [5, 3, 2],
        "总成交量": [25000000, 10500000, 4200000],
        "总成交金额": [387500000, 129150000, 121380000],
    })