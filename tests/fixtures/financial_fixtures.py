"""
Mock fixtures for financial data testing.

This module provides mock data for financial metrics tests,
allowing tests to run offline without requiring network access.
"""

import pandas as pd
import numpy as np


def get_mock_financial_metrics():
    """Mock financial metrics data"""
    return pd.DataFrame(
        {
            "report_date": ["2024-01-01", "2023-12-01", "2023-09-01"],
            "symbol": ["600000", "600000", "600000"],
            "total_assets": [80000000000, 75000000000, 70000000000],
            "fixed_assets_net": [5000000000, 4800000000, 4500000000],
            "cash_and_equivalents": [12000000000, 10000000000, 9000000000],
            "total_liabilities": [60000000000, 55000000000, 50000000000],
            "shareholders_equity": [20000000000, 20000000000, 20000000000],
            "revenue": [5000000000, 4500000000, 4000000000],
            "net_income_common_stock": [500000000, 450000000, 400000000],
            "net_cash_flow_from_operations": [300000000, 250000000, 200000000],
            "net_cash_flow_from_investing": [-100000000, -80000000, -60000000],
            "net_cash_flow_from_financing": [-50000000, -30000000, -20000000],
        }
    )


def get_mock_balance_sheet():
    """Mock balance sheet data"""
    return pd.DataFrame(
        {
            "report_date": ["2024-01-01", "2023-12-01"],
            "symbol": ["600000", "600000"],
            "total_assets": [80000000000, 75000000000],
            "fixed_assets_net": [5000000000, 4800000000],
            "cash_and_equivalents": [12000000000, 10000000000],
            "inventory": [2000000000, 1800000000],
            "total_liabilities": [60000000000, 55000000000],
            "shareholders_equity": [20000000000, 20000000000],
        }
    )


def get_mock_income_statement():
    """Mock income statement data"""
    return pd.DataFrame(
        {
            "report_date": ["2024-01-01", "2023-12-01"],
            "symbol": ["600000", "600000"],
            "revenue": [5000000000, 4500000000],
            "total_operating_costs": [4000000000, 3600000000],
            "operating_profit": [1000000000, 900000000],
            "net_income_common_stock": [500000000, 450000000],
        }
    )


def get_mock_cash_flow():
    """Mock cash flow data"""
    return pd.DataFrame(
        {
            "report_date": ["2024-01-01", "2023-12-01"],
            "symbol": ["600000", "600000"],
            "net_cash_flow_from_operations": [300000000, 250000000],
            "net_cash_flow_from_investing": [-100000000, -80000000],
            "net_cash_flow_from_financing": [-50000000, -30000000],
            "change_in_cash_and_equivalents": [150000000, 140000000],
        }
    )


def get_mock_financial_metrics_empty():
    """Mock empty financial metrics data"""
    return pd.DataFrame()
