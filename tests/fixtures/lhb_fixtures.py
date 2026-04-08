"""
Mock fixtures for dragon tiger list (龙虎榜) data testing.

This module provides mock data for dragon tiger list tests,
allowing tests to run offline without requiring network access.
"""

import pandas as pd
import numpy as np


def get_mock_dragon_tiger_list():
    """Mock dragon tiger list data"""
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01"],
            "symbol": ["600000", "300001"],
            "name": ["浦发银行", "特锐德"],
            "close": [10.50, 8.30],
            "pct_change": [5.23, 3.45],
            "turnover": [12.5, 8.6],
            "reason": ["涨停", "连续涨停"],
            "buy_amount": [5000000, 3000000],
            "sell_amount": [3000000, 2000000],
            "net_amount": [2000000, 1000000],
        }
    )


def get_mock_dragon_tiger_summary():
    """Mock dragon tiger summary data"""
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "total_stocks": [50, 45],
            "total_amount": [100000000, 90000000],
            "buy_amount": [60000000, 55000000],
            "sell_amount": [40000000, 35000000],
            "net_amount": [20000000, 20000000],
        }
    )


def get_mock_dragon_tiger_broker_stats():
    """Mock broker statistics data"""
    return pd.DataFrame(
        {
            "broker": ["中信证券", "华泰证券", "招商证券"],
            "buy_count": [10, 8, 7],
            "sell_count": [5, 4, 3],
            "buy_amount": [50000000, 40000000, 35000000],
            "sell_amount": [30000000, 25000000, 20000000],
            "net_amount": [20000000, 15000000, 15000000],
        }
    )


def get_mock_dragon_tiger_empty():
    """Mock empty dragon tiger data"""
    return pd.DataFrame()
