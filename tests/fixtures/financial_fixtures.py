"""
Mock fixtures for financial data testing.

This module provides mock data for financial metrics tests,
allowing tests to run offline without requiring network access.
"""

import pandas as pd
import numpy as np
from datetime import datetime


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


def get_mock_sina_balance_sheet_data():
    """Mock Sina balance sheet raw data with all required columns for mapping"""
    return pd.DataFrame(
        {
            "报告日": ["20231231", "20230930", "20230630"],
            "货币资金": [12000000000, 10000000000, 9000000000],
            "应收账款": [500000000, 450000000, 400000000],
            "存货": [2000000000, 1800000000, 1500000000],
            "流动资产合计": [30000000000, 28000000000, 25000000000],
            "非流动资产合计": [50000000000, 47000000000, 45000000000],
            "资产总计": [80000000000, 75000000000, 70000000000],
            "应付账款": [3000000000, 2800000000, 2500000000],
            "流动负债合计": [20000000000, 19000000000, 18000000000],
            "非流动负债合计": [40000000000, 36000000000, 32000000000],
            "负债合计": [60000000000, 55000000000, 50000000000],
            "股东权益合计": [20000000000, 20000000000, 20000000000],
            "短期借款": [5000000000, 4500000000, 4000000000],
            "长期借款": [30000000000, 28000000000, 25000000000],
        }
    )


def get_mock_sina_income_statement_data():
    """Mock Sina income statement raw data with all required columns for mapping"""
    return pd.DataFrame(
        {
            "报告日": ["20231231", "20230930", "20230630"],
            "营业总收入": [5000000000, 4500000000, 4000000000],
            "营业收入": [4800000000, 4300000000, 3800000000],
            "营业总成本": [4000000000, 3600000000, 3200000000],
            "营业成本": [3500000000, 3100000000, 2800000000],
            "营业利润": [1000000000, 900000000, 800000000],
            "销售费用": [100000000, 90000000, 80000000],
            "管理费用": [200000000, 180000000, 160000000],
            "财务费用": [50000000, 45000000, 40000000],
            "净利润": [500000000, 450000000, 400000000],
            "基本每股收益": [0.5, 0.45, 0.4],
            "稀释每股收益": [0.5, 0.45, 0.4],
        }
    )


def get_mock_sina_cash_flow_data():
    """Mock Sina cash flow raw data with all required columns for mapping"""
    return pd.DataFrame(
        {
            "报告日": ["20231231", "20230930", "20230630"],
            "经营活动产生的现金流量净额": [300000000, 250000000, 200000000],
            "投资活动产生的现金流量净额": [-100000000, -80000000, -60000000],
            "筹资活动产生的现金流量净额": [-50000000, -30000000, -20000000],
            "现金及现金等价物净增加额": [150000000, 140000000, 120000000],
            "期末现金及现金等价物余额": [12000000000, 10000000000, 9000000000],
            "销售商品、提供劳务收到的现金": [5500000000, 5000000000, 4500000000],
            "收到的税费返还": [50000000, 45000000, 40000000],
            "支付给职工以及为职工支付的现金": [300000000, 280000000, 250000000],
            "支付的各项税费": [200000000, 180000000, 160000000],
        }
    )


def get_mock_eastmoney_balance_sheet_data():
    """Mock Eastmoney balance sheet raw data"""
    return pd.DataFrame(
        {
            "REPORT_DATE": ["2023-12-31", "2023-09-30", "2023-06-30"],
            "TOTAL_ASSETS": [80000000000, 75000000000, 70000000000],
            "FIXED_ASSET": [5000000000, 4800000000, 4500000000],
            "MONETARYFUNDS": [12000000000, 10000000000, 9000000000],
            "ACCOUNTS_RECE": [500000000, 450000000, 400000000],
            "INVENTORY": [2000000000, 1800000000, 1500000000],
            "TOTAL_LIABILITIES": [60000000000, 55000000000, 50000000000],
            "ACCOUNTS_PAYABLE": [3000000000, 2800000000, 2500000000],
            "ADVANCE_RECEIVABLES": [1000000000, 900000000, 800000000],
            "TOTAL_EQUITY": [20000000000, 20000000000, 20000000000],
        }
    )


def get_mock_eastmoney_income_statement_data():
    """Mock Eastmoney income statement raw data"""
    return pd.DataFrame(
        {
            "REPORT_DATE": ["2023-12-31", "2023-09-30", "2023-06-30"],
            "TOTAL_OPERATE_INCOME": [5000000000, 4500000000, 4000000000],
            "TOTAL_OPERATE_COST": [4000000000, 3600000000, 3200000000],
            "OPERATE_PROFIT": [1000000000, 900000000, 800000000],
            "PARENT_NETPROFIT": [500000000, 450000000, 400000000],
        }
    )


def get_mock_eastmoney_cash_flow_data():
    """Mock Eastmoney cash flow raw data"""
    return pd.DataFrame(
        {
            "REPORT_DATE": ["2023-12-31", "2023-09-30", "2023-06-30"],
            "NETCASH_OPERATE": [300000000, 250000000, 200000000],
            "NETCASH_INVEST": [-100000000, -80000000, -60000000],
            "NETCASH_FINANCE": [-50000000, -30000000, -20000000],
            "CCE_ADD": [150000000, 140000000, 120000000],
        }
    )


def get_mock_cninfo_balance_sheet_data():
    """Mock Cninfo balance sheet raw data"""
    return pd.DataFrame(
        {
            "report_date": ["2023-12-31", "2023-09-30"],
            "total_assets": [80000000000, 75000000000],
            "total_liabilities": [60000000000, 55000000000],
            "total_shareholders_equity": [20000000000, 20000000000],
            "current_assets": [30000000000, 28000000000],
            "non_current_assets": [50000000000, 47000000000],
            "current_liabilities": [20000000000, 19000000000],
            "non_current_liabilities": [40000000000, 36000000000],
        }
    )


def get_mock_cninfo_income_statement_data():
    """Mock Cninfo income statement raw data"""
    return pd.DataFrame(
        {
            "report_date": ["2023-12-31", "2023-09-30"],
            "revenue": [5000000000, 4500000000],
            "operating_cost": [3500000000, 3100000000],
            "gross_profit": [1500000000, 1400000000],
            "operating_profit": [1000000000, 900000000],
        }
    )


def get_mock_cninfo_cash_flow_data():
    """Mock Cninfo cash flow raw data"""
    return pd.DataFrame(
        {
            "report_date": ["2023-12-31", "2023-09-30"],
            "net_cash_operating": [300000000, 250000000],
            "net_cash_investing": [-100000000, -80000000],
            "net_cash_financing": [-50000000, -30000000],
            "net_increase_cash": [150000000, 140000000],
        }
    )


def get_mock_financial_report_with_missing_columns():
    """Mock financial report with some missing columns"""
    return pd.DataFrame(
        {
            "报告日": ["20231231"],
            "货币资金": [12000000000],
        }
    )


def get_mock_financial_report_with_nan_values():
    """Mock financial report with NaN values"""
    return pd.DataFrame(
        {
            "报告日": ["20231231", "20230930"],
            "货币资金": [12000000000, np.nan],
            "应收账款": [500000000, 450000000],
            "存货": [np.nan, 1800000000],
            "资产总计": [80000000000, 75000000000],
            "流动资产合计": [30000000000, 28000000000],
            "非流动资产合计": [50000000000, 47000000000],
            "应付账款": [3000000000, 2800000000],
            "流动负债合计": [20000000000, 19000000000],
            "非流动负债合计": [40000000000, 36000000000],
            "负债合计": [60000000000, 55000000000],
            "股东权益合计": [20000000000, 20000000000],
            "短期借款": [5000000000, 4500000000],
            "长期借款": [30000000000, 28000000000],
        }
    )


def get_mock_financial_report_with_zeros():
    """Mock financial report with zero values"""
    return pd.DataFrame(
        {
            "报告日": ["20231231", "20230930"],
            "货币资金": [0, 10000000000],
            "应收账款": [500000000, 450000000],
            "存货": [0, 1800000000],
            "资产总计": [80000000000, 75000000000],
            "流动资产合计": [30000000000, 28000000000],
            "非流动资产合计": [50000000000, 47000000000],
            "应付账款": [3000000000, 2800000000],
            "流动负债合计": [20000000000, 19000000000],
            "非流动负债合计": [40000000000, 36000000000],
            "负债合计": [60000000000, 55000000000],
            "股东权益合计": [20000000000, 20000000000],
            "短期借款": [5000000000, 4500000000],
            "长期借款": [30000000000, 28000000000],
        }
    )


def get_mock_financial_report_empty():
    """Mock empty financial report"""
    return pd.DataFrame()


def get_mock_financial_report_single_row():
    """Mock financial report with single row"""
    return pd.DataFrame(
        {
            "报告日": ["20231231"],
            "货币资金": [12000000000],
            "应收账款": [500000000],
            "存货": [2000000000],
            "资产总计": [80000000000],
            "流动资产合计": [30000000000],
            "非流动资产合计": [50000000000],
            "应付账款": [3000000000],
            "流动负债合计": [20000000000],
            "非流动负债合计": [40000000000],
            "负债合计": [60000000000],
            "股东权益合计": [20000000000],
            "短期借款": [5000000000],
            "长期借款": [30000000000],
        }
    )


def get_mock_financial_metrics_with_calculations():
    """Mock financial metrics for ratio calculations"""
    return pd.DataFrame(
        {
            "report_date": ["2023-12-31", "2023-09-30"],
            "current_assets": [30000000000, 28000000000],
            "current_liabilities": [20000000000, 19000000000],
            "cash_and_equivalents": [12000000000, 10000000000],
            "total_assets": [80000000000, 75000000000],
            "total_debt": [40000000000, 36000000000],
            "total_liabilities": [60000000000, 55000000000],
            "shareholders_equity": [20000000000, 20000000000],
            "revenue": [5000000000, 4500000000],
            "net_income": [500000000, 450000000],
            "operating_profit": [1000000000, 900000000],
            "ebit": [1200000000, 1100000000],
        }
    )
