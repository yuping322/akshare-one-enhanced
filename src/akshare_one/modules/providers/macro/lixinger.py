"""
Lixinger provider for macro economic data.

This module implements macro economic data provider using Lixinger OpenAPI.
"""

import pandas as pd

from ....lixinger_client import get_lixinger_client
from .base import MacroFactory, MacroProvider


@MacroFactory.register("lixinger")
class LixingerMacroProvider(MacroProvider):
    """
    Macro economic data provider using Lixinger OpenAPI.

    Provides GDP, CPI, PPI, interest rates, money supply, social financing,
    foreign trade, currency exchange rate, gold price, crude oil, natural gas,
    central bank balance sheet, credit securities account, domestic debt securities,
    foreign assets, investment in fixed assets, national debt, population,
    RMB deposits, RMB loans, RMB index, USD index, silver price, platinum price,
    traffic transportation, non-ferrous metals, official reserve assets,
    real estate, required reserves, stamp duty, leverage ratio, investor,
    balance of payments, energy, petroleum, industrialization, domestic trade.
    """

    def get_source_name(self) -> str:
        return "lixinger"

    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def _query_macro_api(self, api_suffix: str, params: dict, **kwargs) -> pd.DataFrame:
        """
        Generic method to query macro API endpoints.

        Args:
            api_suffix: API endpoint suffix
            params: Query parameters

        Returns:
            pd.DataFrame: Macro data
        """
        client = get_lixinger_client()

        response = client.query_api(api_suffix, params)

        if response.get("code") != 1:
            return pd.DataFrame()

        data = response.get("data", [])
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)

        return self.standardize_and_filter(
            df, source="lixinger", columns=kwargs.get("columns"), row_filter=kwargs.get("row_filter")
        )

    def get_ppi_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get PPI data from Lixinger via macro/price-index (same endpoint as CPI).

        Returns:
            pd.DataFrame: PPI data (subset of price-index response)
        """
        return self.get_cpi_data(start_date, end_date, **kwargs)

    def get_shibor_rate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get Shibor rate data from Lixinger via macro/interest-rates.

        Returns:
            pd.DataFrame: Interest rate data including Shibor fields
        """
        return self.get_lpr_rate(start_date, end_date, **kwargs)

    def get_pmi_index(self, start_date: str, end_date: str, pmi_type: str = "manufacturing", **kwargs) -> pd.DataFrame:
        """
        Get PMI data from Lixinger via macro/price-index endpoint.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            pmi_type: PMI type ('manufacturing', 'non_manufacturing', 'composite')

        Returns:
            pd.DataFrame: PMI data
        """
        area_code = kwargs.get("area_code", "cn")

        metrics_map = {
            "manufacturing": ["m.mi_pmi.t"],
            "non_manufacturing": ["m.n_mi_pmi.t"],
            "composite": ["m.c_pmi.t"],
        }

        metrics_list = metrics_map.get(pmi_type, ["m.mi_pmi.t"])

        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": area_code,
            "metricsList": metrics_list,
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/price-index", params, **kwargs)

    def get_cpi_data(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get CPI data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            area_code: Area code ('cn' for China, 'us' for USA). Default: 'cn'
            metrics_list: List of metrics (e.g., ['m.cpi.t', 'm.ppi.t'])

        Returns:
            pd.DataFrame: CPI data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": kwargs.get("area_code", "cn"),
            "metricsList": kwargs.get("metrics_list", ["m.cpi.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/price-index", params, **kwargs)

    def get_m2_supply(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get M2 money supply data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            area_code: Area code ('cn', 'hk', 'us'). Default: 'cn'
            metrics_list: List of metrics (e.g., ['m.m2.t', 'm.m1.t'])

        Returns:
            pd.DataFrame: M2 data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": kwargs.get("area_code", "cn"),
            "metricsList": kwargs.get("metrics_list", ["m.m2.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/money-supply", params, **kwargs)

    def get_social_financing(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get social financing data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.sf.t', 'm.sf_rmbl.t'])

        Returns:
            pd.DataFrame: Social financing data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.sf.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/social-financing", params, **kwargs)

    def get_lpr_rate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get LPR interest rate data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            area_code: Area code ('cn', 'hk', 'us'). Default: 'cn'
            metrics_list: List of metrics (e.g., ['lpr_y1', 'lpr_y5', 'shibor_on'])

        Returns:
            pd.DataFrame: LPR data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": kwargs.get("area_code", "cn"),
            "metricsList": kwargs.get("metrics_list", ["lpr_y1", "lpr_y5"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/interest-rates", params, **kwargs)

    def get_gdp(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get GDP data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            area_code: Area code ('cn' for China, 'us' for USA). Default: 'cn'
            metrics_list: List of metrics (e.g., ['q.gdp.t', 'q.gdp.t_y2y'])

        Returns:
            pd.DataFrame: GDP data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": kwargs.get("area_code", "cn"),
            "metricsList": kwargs.get("metrics_list", ["q.gdp.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/gdp", params, **kwargs)

    def get_foreign_trade(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get foreign trade data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.tiae_rmb.t', 'm.te_usd.t'])

        Returns:
            pd.DataFrame: Foreign trade data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.tiae_rmb.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/foreign-trade", params, **kwargs)

    def get_currency_exchange_rate(
        self, start_date: str, end_date: str, from_currency: str = "USD", to_currency: str = "CNY", **kwargs
    ) -> pd.DataFrame:
        """
        Get currency exchange rate data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            from_currency: Source currency ('CNY', 'HKD', 'USD')
            to_currency: Target currency

        Returns:
            pd.DataFrame: Exchange rate data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "fromCurrency": from_currency,
            "toCurrency": to_currency,
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/currency-exchange-rate", params, **kwargs)

    def get_gold_price(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get gold price data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            area_code: Area code ('cn' for Shanghai Gold, 'us' for London Gold)
            metrics_list: List of metrics (e.g., ['sge_pm_cny'] or ['lbma_pm_usd'])

        Returns:
            pd.DataFrame: Gold price data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": kwargs.get("area_code", "cn"),
            "metricsList": kwargs.get("metrics_list", ["sge_pm_cny"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/gold-price", params, **kwargs)

    def get_crude_oil(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get crude oil price data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['wti_co_sp', 'brent_co_sp'])

        Returns:
            pd.DataFrame: Crude oil price data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "us",
            "metricsList": kwargs.get("metrics_list", ["wti_co_sp", "brent_co_sp"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/crude-oil", params, **kwargs)

    def get_natural_gas(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get natural gas price data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['hh_ng_sp'])

        Returns:
            pd.DataFrame: Natural gas price data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "us",
            "metricsList": kwargs.get("metrics_list", ["hh_ng_sp"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/natural-gas", params, **kwargs)

    def get_central_bank_balance_sheet(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get central bank balance sheet data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.t_a.t', 'm.f_a.t'])

        Returns:
            pd.DataFrame: Central bank balance sheet data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.t_a.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/central-bank-balance-sheet", params, **kwargs)

    def get_credit_securities_account(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get credit securities account data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['ncsa', 'csa'])

        Returns:
            pd.DataFrame: Credit securities account data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["ncsa"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/credit-securities-account", params, **kwargs)

    def get_domestic_debt_securities(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get domestic debt securities data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.gs_i.t', 'm.fb_i.c'])

        Returns:
            pd.DataFrame: Domestic debt securities data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.gs_i.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/domestic-debt-securities", params, **kwargs)

    def get_foreign_assets(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get foreign assets data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.f_e.t', 'm.m_g.t'])

        Returns:
            pd.DataFrame: Foreign assets data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.f_e.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/foreign-assets", params, **kwargs)

    def get_investment_in_fixed_assets(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get investment in fixed assets data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.fai_ef.t', 'm.cg_o_fai_ef.t'])

        Returns:
            pd.DataFrame: Investment in fixed assets data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.fai_ef.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/investment-in-fixed-assets", params, **kwargs)

    def get_national_debt(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get national debt yield data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            area_code: Area code ('cn', 'us')
            metrics_list: List of metrics (e.g., ['tcm_y10', 'tcm_y5'])

        Returns:
            pd.DataFrame: National debt yield data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": kwargs.get("area_code", "cn"),
            "metricsList": kwargs.get("metrics_list", ["tcm_y10"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/national-debt", params, **kwargs)

    def get_population(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get population data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['y.tp.t', 'y.pb_r.t'])

        Returns:
            pd.DataFrame: Population data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["y.tp.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/population", params, **kwargs)

    def get_rmb_deposits(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get RMB deposits data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.rmb_d.t', 'm.rmb_h_d.t'])

        Returns:
            pd.DataFrame: RMB deposits data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.rmb_d.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/rmb-deposits", params, **kwargs)

    def get_rmb_loans(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get RMB loans data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.rmb_l.t', 'm.rmb_h_l.t'])

        Returns:
            pd.DataFrame: RMB loans data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.rmb_l.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/rmb-loans", params, **kwargs)

    def get_rmbidx(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get RMB index data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: RMB index data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/rmbidx", params, **kwargs)

    def get_usdx(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get USD index data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: USD index data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/usdx", params, **kwargs)

    def get_silver_price(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get silver price data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['si_eur'])

        Returns:
            pd.DataFrame: Silver price data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "us",
            "metricsList": kwargs.get("metrics_list", ["si_eur"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/silver-price", params, **kwargs)

    def get_platinum_price(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get platinum price data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['pl_usd'])

        Returns:
            pd.DataFrame: Platinum price data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "us",
            "metricsList": kwargs.get("metrics_list", ["pl_usd"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/platinum-price", params, **kwargs)

    def get_traffic_transportation(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get traffic transportation data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.rfv.t', 'm.rfv.t_y2y'])

        Returns:
            pd.DataFrame: Traffic transportation data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.rfv.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/traffic-transportation", params, **kwargs)

    def get_non_ferrous_metals(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get non-ferrous metals price data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['l_cu_p', 'l_zn_p', 'l_al_p'])

        Returns:
            pd.DataFrame: Non-ferrous metals price data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "us",
            "metricsList": kwargs.get("metrics_list", ["l_cu_p"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/non-ferrous-metals", params, **kwargs)

    def get_official_reserve_assets(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get official reserve assets data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.ora.t', 'm.ora_fc.t'])

        Returns:
            pd.DataFrame: Official reserve assets data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.ora.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/official-reserve-assets", params, **kwargs)

    def get_real_estate(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get real estate data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.rei.t', 'm.sa_o_ch.t'])

        Returns:
            pd.DataFrame: Real estate data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.rei.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/real-estate", params, **kwargs)

    def get_required_reserves(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get required reserves ratio data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['lfi_drr', 'masfi_drr'])

        Returns:
            pd.DataFrame: Required reserves ratio data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["lfi_drr"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/required-reserves", params, **kwargs)

    def get_stamp_duty(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get stamp duty data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['sdsha', 'sdsza'])

        Returns:
            pd.DataFrame: Stamp duty data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["sdsha"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/stamp-duty", params, **kwargs)

    def get_leverage_ratio(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get leverage ratio data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['lr_h', 'lr_nfc', 'lr_gg'])

        Returns:
            pd.DataFrame: Leverage ratio data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["lr_h"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/leverage-ratio", params, **kwargs)

    def get_investor(self, start_date: str, end_date: str, granularity: str = "m", **kwargs) -> pd.DataFrame:
        """
        Get investor data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            granularity: Data granularity ('m' for monthly, 'w' for weekly)
            metrics_list: List of metrics (e.g., ['ni', 'nni', 'non_ni'])

        Returns:
            pd.DataFrame: Investor data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "granularity": granularity,
            "metricsList": kwargs.get("metrics_list", ["ni"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/investor", params, **kwargs)

    def get_balance_of_payments(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get balance of payments data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['q.bop_cura.t', 'q.bop_ca.t'])

        Returns:
            pd.DataFrame: Balance of payments data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["q.bop_cura.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/bop", params, **kwargs)

    def get_energy(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get energy data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.ep.t', 'm.ep_h.t', 'm.ep_t.t'])

        Returns:
            pd.DataFrame: Energy data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.ep.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/energy", params, **kwargs)

    def get_petroleum(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get petroleum data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['y.w_petaol_sto.t', 'y.w_petaol_pro.t'])

        Returns:
            pd.DataFrame: Petroleum data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "us",
            "metricsList": kwargs.get("metrics_list", ["y.w_petaol_sto.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/petroleum", params, **kwargs)

    def get_industrialization(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get industrialization data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.adsietp.t', 'm.ieop.t'])

        Returns:
            pd.DataFrame: Industrialization data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.adsietp.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/industrialization", params, **kwargs)

    def get_domestic_trade(self, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Get domestic trade (social consumer goods retail) data from Lixinger.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metrics_list: List of metrics (e.g., ['m.src.t', 'm.sr_o.t'])

        Returns:
            pd.DataFrame: Domestic trade data
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "areaCode": "cn",
            "metricsList": kwargs.get("metrics_list", ["m.src.t"]),
        }

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api("macro/domestic-trade", params, **kwargs)

    def get_macro_data(self, api_type: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        Generic method to query any macro API endpoint.

        This is a convenience method that provides a unified interface for all macro data.

        Args:
            api_type: API endpoint type (e.g., 'gdp', 'price-index', 'interest-rates', etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            area_code: Area code (optional, depends on API)
            metrics_list: List of metrics (optional)
            from_currency: Source currency (for currency-exchange-rate)
            to_currency: Target currency (for currency-exchange-rate)
            granularity: Data granularity (for investor)
            limit: Number of recent data points

        Returns:
            pd.DataFrame: Macro data

        Example:
            >>> provider.get_macro_data('gdp', '2020-01-01', '2025-01-01',
            ...                         area_code='cn', metrics_list=['q.gdp.t'])
            >>> provider.get_macro_data('currency-exchange-rate', '2020-01-01', '2025-01-01',
            ...                         from_currency='USD', to_currency='CNY')
        """
        api_suffix = f"macro/{api_type}"

        params = {
            "startDate": start_date,
            "endDate": end_date,
        }

        if api_type in [
            "gdp",
            "price-index",
            "interest-rates",
            "money-supply",
            "social-financing",
            "foreign-trade",
            "gold-price",
            "central-bank-balance-sheet",
            "credit-securities-account",
            "domestic-debt-securities",
            "foreign-assets",
            "investment-in-fixed-assets",
            "national-debt",
            "population",
            "rmb-deposits",
            "rmb-loans",
            "traffic-transportation",
            "official-reserve-assets",
            "real-estate",
            "required-reserves",
            "stamp-duty",
            "leverage-ratio",
            "investor",
            "bop",
            "energy",
            "industrialization",
            "domestic-trade",
        ]:
            params["areaCode"] = kwargs.get("area_code", "cn")

        if api_type in [
            "crude-oil",
            "natural-gas",
            "silver-price",
            "platinum-price",
            "non-ferrous-metals",
            "petroleum",
        ]:
            params["areaCode"] = kwargs.get("area_code", "us")

        if api_type == "currency-exchange-rate":
            params["fromCurrency"] = kwargs.get("from_currency", "USD")
            params["toCurrency"] = kwargs.get("to_currency", "CNY")

        if api_type == "investor":
            params["granularity"] = kwargs.get("granularity", "m")

        if "metrics_list" in kwargs:
            params["metricsList"] = kwargs["metrics_list"]

        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]

        return self._query_macro_api(api_suffix, params, **kwargs)
