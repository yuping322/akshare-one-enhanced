"""
Mock fixtures for historical data testing.

This module provides mock data for historical stock data tests,
allowing tests to run offline without requiring network access.
"""

import pandas as pd
import numpy as np


def get_mock_hist_data_daily():
    """Mock daily historical stock data"""
    return pd.DataFrame(
        {
            "日期": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "开盘": [10.0, 11.0, 12.0, 13.0, 14.0],
            "收盘": [10.5, 11.5, 12.5, 13.5, 14.5],
            "最高": [11.0, 12.0, 13.0, 14.0, 15.0],
            "最低": [9.5, 10.5, 11.5, 12.5, 13.5],
            "成交量": [100000, 110000, 120000, 130000, 140000],
        }
    )


def get_mock_hist_data_minute():
    """Mock minute historical stock data"""
    return pd.DataFrame(
        {
            "时间": [
                "2024-01-01 09:30:00",
                "2024-01-01 09:31:00",
                "2024-01-01 09:32:00",
                "2024-01-01 09:33:00",
                "2024-01-01 09:34:00",
            ],
            "开盘": [10.0, 10.1, 10.2, 10.3, 10.4],
            "收盘": [10.5, 10.6, 10.7, 10.8, 10.9],
            "最高": [11.0, 11.1, 11.2, 11.3, 11.4],
            "最低": [9.5, 9.6, 9.7, 9.8, 9.9],
            "成交量": [10000, 11000, 12000, 13000, 14000],
            "成交额": [100000, 110000, 120000, 130000, 140000],
            "均价": [10.25, 10.35, 10.45, 10.55, 10.65],
        }
    )


def get_mock_hist_data_hour():
    """Mock hourly historical stock data"""
    return pd.DataFrame(
        {
            "时间": [
                "2024-01-01 10:00:00",
                "2024-01-01 11:00:00",
                "2024-01-01 14:00:00",
            ],
            "开盘": [10.0, 10.5, 11.0],
            "收盘": [10.3, 10.8, 11.3],
            "最高": [10.5, 11.0, 11.5],
            "最低": [9.8, 10.3, 10.8],
            "成交量": [50000, 55000, 60000],
        }
    )


def get_mock_hist_data_weekly():
    """Mock weekly historical stock data"""
    return pd.DataFrame(
        {
            "日期": ["2024-01-01", "2024-01-08", "2024-01-15"],
            "开盘": [10.0, 12.0, 14.0],
            "收盘": [11.5, 13.5, 15.5],
            "最高": [12.0, 14.0, 16.0],
            "最低": [9.5, 11.5, 13.5],
            "成交量": [500000, 600000, 700000],
        }
    )


def get_mock_hist_data_monthly():
    """Mock monthly historical stock data"""
    return pd.DataFrame(
        {
            "日期": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "开盘": [10.0, 15.0, 20.0],
            "收盘": [14.5, 19.5, 24.5],
            "最高": [15.0, 20.0, 25.0],
            "最低": [9.5, 14.5, 19.5],
            "成交量": [2000000, 2500000, 3000000],
        }
    )


def get_mock_hist_data_empty():
    """Mock empty historical data"""
    return pd.DataFrame()


def get_mock_hist_data_with_nan():
    """Mock historical data with NaN values"""
    return pd.DataFrame(
        {
            "日期": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "开盘": [10.0, np.nan, 12.0],
            "收盘": [10.5, 11.5, np.nan],
            "最高": [11.0, 12.0, 13.0],
            "最低": [9.5, 10.5, 11.5],
            "成交量": [100000, 110000, 120000],
        }
    )


def get_mock_hist_data_with_infinity():
    """Mock historical data with Infinity values"""
    return pd.DataFrame(
        {
            "日期": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "开盘": [10.0, np.inf, 12.0],
            "收盘": [10.5, 11.5, -np.inf],
            "最高": [11.0, 12.0, 13.0],
            "最低": [9.5, 10.5, 11.5],
            "成交量": [100000, 110000, 120000],
        }
    )


def get_mock_hist_data_etf():
    """Mock ETF historical data"""
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "open": [10.0, 11.0, 12.0],
            "close": [10.5, 11.5, 12.5],
            "high": [11.0, 12.0, 13.0],
            "low": [9.5, 10.5, 11.5],
            "volume": [100000, 110000, 120000],
        }
    )


def get_mock_hist_data_extreme_values():
    """Mock historical data with extreme price values"""
    return pd.DataFrame(
        {
            "日期": ["2024-01-01"],
            "开盘": [1e10],
            "收盘": [1e-10],
            "最高": [999999.99],
            "最低": [0.01],
            "成交量": [1e15],
        }
    )


def get_mock_sina_daily_data():
    """Mock Sina daily data format"""
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "open": [10.0, 11.0, 12.0],
            "close": [10.5, 11.5, 12.5],
            "high": [11.0, 12.0, 13.0],
            "low": [9.5, 10.5, 11.5],
            "volume": [100000, 110000, 120000],
        }
    )


def get_mock_sina_minute_data():
    """Mock Sina minute data format"""
    return pd.DataFrame(
        {
            "date": [
                "2024-01-01 09:30:00",
                "2024-01-01 09:31:00",
                "2024-01-01 09:32:00",
            ],
            "open": [10.0, 10.1, 10.2],
            "close": [10.5, 10.6, 10.7],
            "high": [11.0, 11.1, 11.2],
            "low": [9.5, 9.6, 9.7],
            "volume": [10000, 11000, 12000],
        }
    )


def get_mock_b_share_data():
    """Mock B-share historical data"""
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "open": [5.0, 5.5],
            "close": [5.2, 5.7],
            "high": [5.5, 6.0],
            "low": [4.8, 5.3],
            "volume": [50000, 55000],
        }
    )
