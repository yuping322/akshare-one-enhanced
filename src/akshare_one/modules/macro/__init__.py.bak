"""
Macro economic data module for PV.MacroCN.

This module provides interfaces to fetch Chinese macro economic data including:
- GDP data
- LPR interest rates
- PMI indices (manufacturing, non-manufacturing, Caixin)
- CPI/PPI data
- M2 money supply
- Shibor interest rates
- Social financing scale
- Foreign trade
- Currency exchange rate
- Gold/Silver/Platinum prices
- Crude oil/Natural gas prices
- Central bank balance sheet
- Credit securities account
- Domestic debt securities
- Foreign assets
- Investment in fixed assets
- National debt yields
- Population data
- RMB deposits/loans
- RMB index/USD index
- Traffic transportation
- Non-ferrous metals prices
- Official reserve assets
- Real estate data
- Required reserves ratio
- Stamp duty
- Leverage ratio
- Investor data
- Balance of payments
- Energy data
- Petroleum data
- Industrialization data
- Domestic trade
"""

from typing import Literal

import pandas as pd

from ..base import ColumnsType, FilterType, SourceType
from ..factory_base import api_endpoint
from . import baostock, lixinger, official, sina, tushare
from .base import MacroFactory


@api_endpoint(MacroFactory)
def get_lpr_rate(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get LPR (Loan Prime Rate) interest rate data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_pmi_index(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    pmi_type: Literal["manufacturing", "non_manufacturing", "caixin"] = "manufacturing",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get PMI (Purchasing Managers' Index) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        pmi_type: PMI type ('manufacturing', 'non_manufacturing', or 'caixin')
    """
    pass


@api_endpoint(MacroFactory)
def get_cpi_data(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get CPI (Consumer Price Index) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_ppi_data(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get PPI (Producer Price Index) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_m2_supply(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get M2 money supply data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_shibor_rate(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get Shibor (Shanghai Interbank Offered Rate) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_social_financing(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "official",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get social financing scale data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_gdp(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get GDP data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_foreign_trade(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get foreign trade data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_currency_exchange_rate(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    from_currency: str = "USD",
    to_currency: str = "CNY",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get currency exchange rate data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        from_currency: Source currency
        to_currency: Target currency
    """
    pass


@api_endpoint(MacroFactory)
def get_gold_price(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get gold price data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_crude_oil(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get crude oil price data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_natural_gas(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get natural gas price data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_central_bank_balance_sheet(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get central bank balance sheet data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_credit_securities_account(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get credit securities account data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_domestic_debt_securities(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get domestic debt securities data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_foreign_assets(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get foreign assets data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_investment_in_fixed_assets(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get investment in fixed assets data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_national_debt(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get national debt yield data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_population(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get population data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_rmb_deposits(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get RMB deposits data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_rmb_loans(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get RMB loans data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_rmbidx(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get RMB index data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_usdx(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get USD index data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_silver_price(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get silver price data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_platinum_price(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get platinum price data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_traffic_transportation(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get traffic transportation data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_non_ferrous_metals(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get non-ferrous metals price data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_official_reserve_assets(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get official reserve assets data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_real_estate(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get real estate data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_required_reserves(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get required reserves ratio data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_stamp_duty(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get stamp duty data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_leverage_ratio(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get leverage ratio data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_investor(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    granularity: str = "m",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get investor data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        granularity: Data granularity ('m' for monthly, 'w' for weekly)
    """
    pass


@api_endpoint(MacroFactory)
def get_balance_of_payments(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get balance of payments data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_energy(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get energy data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_petroleum(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get petroleum data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_industrialization(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get industrialization data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_domestic_trade(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get domestic trade (social consumer goods retail) data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_macro_data(
    api_type: str,
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "lixinger",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Generic method to query any macro API endpoint.

    Args:
        api_type: API endpoint type (e.g., 'gdp', 'price-index', 'interest-rates')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_deposit_rate_data(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "baostock",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get deposit rate data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_loan_rate_data(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "baostock",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get loan rate data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_required_reserve_ratio_data(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "baostock",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get required reserve ratio data.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_money_supply_data_month(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "baostock",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get monthly money supply data (M0, M1, M2).

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


@api_endpoint(MacroFactory)
def get_money_supply_data_year(
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
    source: SourceType = "baostock",
    columns: ColumnsType = None,
    row_filter: FilterType = None,
) -> pd.DataFrame:
    """
    Get yearly money supply data (M0, M1, M2).

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    pass


__all__ = [
    "get_lpr_rate",
    "get_pmi_index",
    "get_cpi_data",
    "get_ppi_data",
    "get_m2_supply",
    "get_shibor_rate",
    "get_social_financing",
    "get_gdp",
    "get_foreign_trade",
    "get_currency_exchange_rate",
    "get_gold_price",
    "get_crude_oil",
    "get_natural_gas",
    "get_central_bank_balance_sheet",
    "get_credit_securities_account",
    "get_domestic_debt_securities",
    "get_foreign_assets",
    "get_investment_in_fixed_assets",
    "get_national_debt",
    "get_population",
    "get_rmb_deposits",
    "get_rmb_loans",
    "get_rmbidx",
    "get_usdx",
    "get_silver_price",
    "get_platinum_price",
    "get_traffic_transportation",
    "get_non_ferrous_metals",
    "get_official_reserve_assets",
    "get_real_estate",
    "get_required_reserves",
    "get_stamp_duty",
    "get_leverage_ratio",
    "get_investor",
    "get_balance_of_payments",
    "get_energy",
    "get_petroleum",
    "get_industrialization",
    "get_domestic_trade",
    "get_macro_data",
    "get_deposit_rate_data",
    "get_loan_rate_data",
    "get_required_reserve_ratio_data",
    "get_money_supply_data_month",
    "get_money_supply_data_year",
    "MacroFactory",
]
