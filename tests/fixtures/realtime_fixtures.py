"""
Mock fixtures for realtime data testing.

This module provides mock data for realtime stock data tests,
allowing tests to run offline without requiring network access.
"""

import pandas as pd
import numpy as np


def get_mock_realtime_data():
    """Mock realtime stock data"""
    return pd.DataFrame(
        {
            "symbol": ["600000"],
            "price": [10.50],
            "change": [0.25],
            "pct_change": [2.38],
            "timestamp": ["2024-01-01 15:00:00"],
            "volume": [100000],
            "amount": [1050000],
            "open": [10.25],
            "high": [10.75],
            "low": [10.20],
            "prev_close": [10.25],
        }
    )


def get_mock_realtime_data_multi():
    """Mock realtime data for multiple stocks"""
    return pd.DataFrame(
        {
            "symbol": ["600000", "000001", "300001"],
            "price": [10.50, 15.20, 8.30],
            "change": [0.25, -0.10, 0.05],
            "pct_change": [2.38, -0.65, 0.60],
            "timestamp": ["2024-01-01 15:00:00", "2024-01-01 15:00:00", "2024-01-01 15:00:00"],
            "volume": [100000, 150000, 80000],
            "amount": [1050000, 2280000, 664000],
            "open": [10.25, 15.30, 8.25],
            "high": [10.75, 15.50, 8.40],
            "low": [10.20, 15.10, 8.20],
            "prev_close": [10.25, 15.30, 8.25],
        }
    )


def get_mock_realtime_data_empty():
    """Mock empty realtime data"""
    return pd.DataFrame()
