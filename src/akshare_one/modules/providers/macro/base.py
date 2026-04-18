"""
Base provider class for macro economic data.

This module defines the abstract interface for macro economic data providers.
"""

import pandas as pd

from ...core.base import BaseProvider
from ...core.factory import BaseFactory


class MacroProvider(BaseProvider):
    """
    Base class for macro economic data providers.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "macro"

    def get_update_frequency(self) -> str:
        """Macro data is updated monthly or quarterly."""
        return "monthly"

    def get_delay_minutes(self) -> int:
        """Macro data has no real-time delay."""
        return 0

    def get_lpr_rate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get LPR (Loan Prime Rate) interest rate data.
        """
        return self._execute_api_mapped("get_lpr_rate", start_date=start_date, end_date=end_date, **kwargs)

    def get_pmi_index(self, start_date: str, end_date: str, pmi_type: str, **kwargs) -> pd.DataFrame:
        """
        Get PMI (Purchasing Managers' Index) data.
        """
        return self._execute_api_mapped(
            "get_pmi_index", start_date=start_date, end_date=end_date, pmi_type=pmi_type, **kwargs
        )

    def get_cpi_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get CPI (Consumer Price Index) data.
        """
        return self._execute_api_mapped("get_cpi_data", start_date=start_date, end_date=end_date, **kwargs)

    def get_ppi_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get PPI (Producer Price Index) data.
        """
        return self._execute_api_mapped("get_ppi_data", start_date=start_date, end_date=end_date, **kwargs)

    def get_m2_supply(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get M2 money supply data.
        """
        return self._execute_api_mapped("get_m2_supply", start_date=start_date, end_date=end_date, **kwargs)

    def get_shibor_rate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get Shibor (Shanghai Interbank Offered Rate) data.
        """
        return self._execute_api_mapped("get_shibor_rate", start_date=start_date, end_date=end_date, **kwargs)

    def get_social_financing(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get social financing scale data.
        """
        return self._execute_api_mapped("get_social_financing", start_date=start_date, end_date=end_date, **kwargs)

    def get_gdp(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get GDP data.
        """
        return self._execute_api_mapped("get_gdp", start_date=start_date, end_date=end_date, **kwargs)

    def get_foreign_trade(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get foreign trade data.
        """
        return self._execute_api_mapped("get_foreign_trade", start_date=start_date, end_date=end_date, **kwargs)

    def get_currency_exchange_rate(
        self, start_date: str, end_date: str, from_currency: str = "USD", to_currency: str = "CNY", **kwargs
    ) -> pd.DataFrame:
        """
        Get currency exchange rate data.
        """
        return self._execute_api_mapped(
            "get_currency_exchange_rate",
            start_date=start_date,
            end_date=end_date,
            from_currency=from_currency,
            to_currency=to_currency,
            **kwargs,
        )

    def get_gold_price(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get gold price data.
        """
        return self._execute_api_mapped("get_gold_price", start_date=start_date, end_date=end_date, **kwargs)

    def get_crude_oil(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get crude oil price data.
        """
        return self._execute_api_mapped("get_crude_oil", start_date=start_date, end_date=end_date, **kwargs)

    def get_natural_gas(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get natural gas price data.
        """
        return self._execute_api_mapped("get_natural_gas", start_date=start_date, end_date=end_date, **kwargs)

    def get_central_bank_balance_sheet(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get central bank balance sheet data.
        """
        return self._execute_api_mapped(
            "get_central_bank_balance_sheet", start_date=start_date, end_date=end_date, **kwargs
        )

    def get_credit_securities_account(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get credit securities account data.
        """
        return self._execute_api_mapped(
            "get_credit_securities_account", start_date=start_date, end_date=end_date, **kwargs
        )

    def get_domestic_debt_securities(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get domestic debt securities data.
        """
        return self._execute_api_mapped(
            "get_domestic_debt_securities", start_date=start_date, end_date=end_date, **kwargs
        )

    def get_foreign_assets(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get foreign assets data.
        """
        return self._execute_api_mapped("get_foreign_assets", start_date=start_date, end_date=end_date, **kwargs)

    def get_investment_in_fixed_assets(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get investment in fixed assets data.
        """
        return self._execute_api_mapped(
            "get_investment_in_fixed_assets", start_date=start_date, end_date=end_date, **kwargs
        )

    def get_national_debt(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get national debt yield data.
        """
        return self._execute_api_mapped("get_national_debt", start_date=start_date, end_date=end_date, **kwargs)

    def get_population(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get population data.
        """
        return self._execute_api_mapped("get_population", start_date=start_date, end_date=end_date, **kwargs)

    def get_rmb_deposits(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get RMB deposits data.
        """
        return self._execute_api_mapped("get_rmb_deposits", start_date=start_date, end_date=end_date, **kwargs)

    def get_rmb_loans(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get RMB loans data.
        """
        return self._execute_api_mapped("get_rmb_loans", start_date=start_date, end_date=end_date, **kwargs)

    def get_rmbidx(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get RMB index data.
        """
        return self._execute_api_mapped("get_rmbidx", start_date=start_date, end_date=end_date, **kwargs)

    def get_usdx(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get USD index data.
        """
        return self._execute_api_mapped("get_usdx", start_date=start_date, end_date=end_date, **kwargs)

    def get_silver_price(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get silver price data.
        """
        return self._execute_api_mapped("get_silver_price", start_date=start_date, end_date=end_date, **kwargs)

    def get_platinum_price(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get platinum price data.
        """
        return self._execute_api_mapped("get_platinum_price", start_date=start_date, end_date=end_date, **kwargs)

    def get_traffic_transportation(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get traffic transportation data.
        """
        return self._execute_api_mapped(
            "get_traffic_transportation", start_date=start_date, end_date=end_date, **kwargs
        )

    def get_non_ferrous_metals(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get non-ferrous metals price data.
        """
        return self._execute_api_mapped("get_non_ferrous_metals", start_date=start_date, end_date=end_date, **kwargs)

    def get_official_reserve_assets(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get official reserve assets data.
        """
        return self._execute_api_mapped(
            "get_official_reserve_assets", start_date=start_date, end_date=end_date, **kwargs
        )

    def get_real_estate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get real estate data.
        """
        return self._execute_api_mapped("get_real_estate", start_date=start_date, end_date=end_date, **kwargs)

    def get_required_reserves(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get required reserves ratio data.
        """
        return self._execute_api_mapped("get_required_reserves", start_date=start_date, end_date=end_date, **kwargs)

    def get_stamp_duty(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get stamp duty data.
        """
        return self._execute_api_mapped("get_stamp_duty", start_date=start_date, end_date=end_date, **kwargs)

    def get_leverage_ratio(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get leverage ratio data.
        """
        return self._execute_api_mapped("get_leverage_ratio", start_date=start_date, end_date=end_date, **kwargs)

    def get_investor(self, start_date: str, end_date: str, granularity: str = "m", **kwargs) -> pd.DataFrame:
        """
        Get investor data.
        """
        return self._execute_api_mapped(
            "get_investor", start_date=start_date, end_date=end_date, granularity=granularity, **kwargs
        )

    def get_balance_of_payments(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get balance of payments data.
        """
        return self._execute_api_mapped("get_balance_of_payments", start_date=start_date, end_date=end_date, **kwargs)

    def get_energy(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get energy data.
        """
        return self._execute_api_mapped("get_energy", start_date=start_date, end_date=end_date, **kwargs)

    def get_petroleum(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get petroleum data.
        """
        return self._execute_api_mapped("get_petroleum", start_date=start_date, end_date=end_date, **kwargs)

    def get_industrialization(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get industrialization data.
        """
        return self._execute_api_mapped("get_industrialization", start_date=start_date, end_date=end_date, **kwargs)

    def get_domestic_trade(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get domestic trade data.
        """
        return self._execute_api_mapped("get_domestic_trade", start_date=start_date, end_date=end_date, **kwargs)

    def get_macro_data(self, api_type: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Generic method to query any macro API endpoint.
        """
        return self._execute_api_mapped(
            "get_macro_data", api_type=api_type, start_date=start_date, end_date=end_date, **kwargs
        )

    def get_deposit_rate_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get deposit rate data.
        """
        return self._execute_api_mapped("get_deposit_rate_data", start_date=start_date, end_date=end_date, **kwargs)

    def get_loan_rate_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get loan rate data.
        """
        return self._execute_api_mapped("get_loan_rate_data", start_date=start_date, end_date=end_date, **kwargs)

    def get_required_reserve_ratio_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get required reserve ratio data.
        """
        return self._execute_api_mapped(
            "get_required_reserve_ratio_data", start_date=start_date, end_date=end_date, **kwargs
        )

    def get_money_supply_data_month(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get monthly money supply data.
        """
        return self._execute_api_mapped(
            "get_money_supply_data_month", start_date=start_date, end_date=end_date, **kwargs
        )

    def get_money_supply_data_year(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get yearly money supply data.
        """
        return self._execute_api_mapped(
            "get_money_supply_data_year", start_date=start_date, end_date=end_date, **kwargs
        )


class MacroFactory(BaseFactory["MacroProvider"]):
    """
    Factory class for creating macro economic data providers.
    """

    _providers: dict[str, type["MacroProvider"]] = {}
