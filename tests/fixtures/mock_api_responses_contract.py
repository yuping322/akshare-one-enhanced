"""
Mock API response fixtures for contract tests.

This module provides pytest fixtures that mock provider classes directly,
allowing contract tests to run completely offline.
"""

import pandas as pd
import pytest


def get_mock_hist_data_contract():
    """Mock historical data for contract tests."""
    return pd.DataFrame(
        {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "symbol": ["600000", "600000", "600000"],
            "open": [10.0, 11.0, 12.0],
            "high": [11.0, 12.0, 13.0],
            "low": [9.5, 10.5, 11.5],
            "close": [10.5, 11.5, 12.5],
            "volume": [100000, 110000, 120000],
        }
    )


def get_mock_realtime_data_contract():
    """Mock realtime data for contract tests."""
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


def get_mock_etf_hist_data_contract():
    """Mock ETF historical data for contract tests."""
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "symbol": ["510050", "510050", "510050"],
            "open": [3.0, 3.1, 3.2],
            "high": [3.1, 3.2, 3.3],
            "low": [2.9, 3.0, 3.1],
            "close": [3.05, 3.15, 3.25],
            "volume": [500000, 550000, 600000],
        }
    )


def get_mock_fund_flow_contract():
    """Mock fund flow data for contract tests."""
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "symbol": ["600000", "600000", "600000"],
            "fundflow_main_net_inflow": [1000000, -500000, 2000000],
            "fundflow_main_net_inflow_rate": [0.5, -0.25, 1.0],
        }
    )


def get_mock_dragon_tiger_contract():
    """Mock dragon tiger data for contract tests."""
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01"],
            "symbol": ["600000", "300001"],
            "name": ["浦发银行", "特锐德"],
            "close": [10.50, 8.30],
            "pct_change": [5.23, 3.45],
            "turnover": [12.5, 8.6],
            "reason": ["涨停", "连续涨停"],
        }
    )


def get_mock_financial_metrics_contract():
    """Mock financial metrics data for contract tests."""
    return pd.DataFrame(
        {
            "report_date": ["2024-01-01", "2023-12-01", "2023-09-01"],
            "symbol": ["600000", "600000", "600000"],
            "total_assets": [80000000000, 75000000000, 70000000000],
            "revenue": [5000000000, 4500000000, 4000000000],
            "net_income_common_stock": [500000000, 450000000, 400000000],
        }
    )


@pytest.fixture
def mock_hist_data_contract(mocker):
    """Mock historical data provider."""
    # Mock EastMoneyDirectHistorical provider directly
    return mocker.patch(
        "akshare_one.modules.historical.eastmoney_direct.EastMoneyDirectHistorical.get_hist_data",
        return_value=get_mock_hist_data_contract(),
    )


@pytest.fixture
def mock_realtime_data_contract(mocker):
    """Mock realtime data provider."""
    # Mock EastMoneyDirectRealtime provider directly
    return mocker.patch(
        "akshare_one.modules.realtime.eastmoney_direct.EastMoneyDirectRealtime.get_current_data",
        return_value=get_mock_realtime_data_contract(),
    )


@pytest.fixture
def mock_etf_hist_data_contract(mocker):
    """Mock ETF historical data provider."""
    # Mock ETF historical provider
    from tests.fixtures.historical_fixtures import get_mock_hist_data_etf

    # Need to mock at the akshare_compat level for ETF
    return mocker.patch("akshare_one.akshare_compat.call_akshare", return_value=get_mock_hist_data_etf())


@pytest.fixture
def mock_fund_flow_contract(mocker):
    """Mock fund flow provider."""
    # Mock fund flow provider directly
    return mocker.patch(
        "akshare_one.modules.fundflow.eastmoney.EastmoneyFundFlowProvider.get_stock_fund_flow",
        return_value=get_mock_fund_flow_contract(),
    )


@pytest.fixture
def mock_dragon_tiger_contract(mocker):
    """Mock dragon tiger provider."""
    # Mock dragon tiger provider directly
    return mocker.patch(
        "akshare_one.modules.lhb.eastmoney.EastmoneyDragonTigerProvider.get_dragon_tiger_list",
        return_value=get_mock_dragon_tiger_contract(),
    )


@pytest.fixture
def mock_financial_metrics_contract(mocker):
    """Mock financial metrics provider."""
    # Mock financial metrics provider directly
    return mocker.patch(
        "akshare_one.modules.financial.eastmoney_direct.EastmoneyDirectFinancialProvider.get_financial_metrics",
        return_value=get_mock_financial_metrics_contract(),
    )
