"""
Futures margin data provider - contract margin rates and calculations.
"""

import pandas as pd

from ....core.base import BaseProvider
from .base import FuturesHistoricalFactory


CONTRACT_MULTIPLIERS = {
    "AG": 15,
    "AU": 1000,
    "CU": 5,
    "AL": 5,
    "ZN": 5,
    "PB": 5,
    "NI": 1,
    "SN": 1,
    "RB": 10,
    "HC": 10,
    "I": 100,
    "J": 100,
    "JM": 60,
    "MA": 10,
    "TA": 5,
    "SA": 20,
    "FG": 20,
    "SR": 10,
    "CF": 5,
    "RM": 10,
    "OI": 10,
    "AP": 10,
    "CJ": 5,
    "IF": 300,
    "IC": 200,
    "IH": 300,
    "IM": 200,
}

DEFAULT_MARGIN_RATE = 0.10


def get_contract_multiplier(contract_code: str) -> float:
    """Get contract multiplier."""
    product = "".join(c for c in contract_code.upper() if c.isalpha())
    return CONTRACT_MULTIPLIERS.get(product, 1)


def get_margin_rate_for_contract(contract_code: str) -> float:
    """Get margin rate for contract."""
    product = "".join(c for c in contract_code.upper() if c.isalpha())
    margin_rates = {
        "IF": 0.12,
        "IC": 0.14,
        "IH": 0.12,
        "IM": 0.14,
        "AU": 0.08,
        "AG": 0.10,
        "CU": 0.10,
        "AL": 0.10,
        "ZN": 0.10,
        "NI": 0.12,
        "RB": 0.09,
        "HC": 0.09,
        "I": 0.12,
        "MA": 0.09,
        "TA": 0.09,
        "SA": 0.12,
    }
    return margin_rates.get(product, DEFAULT_MARGIN_RATE)


def calculate_position_value(price: float, quantity: int, contract_code: str) -> float:
    """Calculate position value."""
    multiplier = get_contract_multiplier(contract_code)
    return price * multiplier * quantity


def calculate_required_margin(price: float, quantity: int, contract_code: str) -> float:
    """Calculate required margin."""
    position_value = calculate_position_value(price, quantity, contract_code)
    margin_rate = get_margin_rate_for_contract(contract_code)
    return position_value * margin_rate


class FuturesMarginProvider(BaseProvider):
    """Provider for futures margin data."""

    def get_data_type(self) -> str:
        return "futuresmargin"

    def get_contract_info(self, contract_code: str) -> pd.DataFrame:
        """Get contract information."""
        return self._execute_api_mapped("get_contract_info", contract_code=contract_code)

    def get_margin_rate(self, contract_code: str) -> pd.DataFrame:
        """Get margin rate."""
        return self._execute_api_mapped("get_margin_rate", contract_code=contract_code)


class FuturesMarginFactory(FuturesHistoricalFactory):
    """Factory for futures margin data providers."""

    pass
