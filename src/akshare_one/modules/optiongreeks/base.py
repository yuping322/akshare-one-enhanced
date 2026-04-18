from ..base import BaseProvider
from ..factory_base import BaseFactory
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict


class OptionGreeksProvider(BaseProvider):
    def get_data_type(self) -> str:
        return "optiongreeks"

    def get_update_frequency(self) -> str:
        return "realtime"

    def get_option_greeks(
        self,
        option_code: str,
        underlying_price: float,
        strike: float,
        days_to_expiry: int,
        option_price: float,
        option_type: str = "call",
        risk_free_rate: float = 0.03,
    ) -> Dict:
        """计算期权Greeks"""
        return self._execute_api_mapped(
            "get_option_greeks",
            option_code=option_code,
            underlying_price=underlying_price,
            strike=strike,
            days_to_expiry=days_to_expiry,
            option_price=option_price,
            option_type=option_type,
            risk_free_rate=risk_free_rate,
        )

    def calculate_implied_vol(
        self,
        option_code: str,
        option_price: float,
        underlying_price: float,
        strike: float,
        days_to_expiry: int,
        option_type: str = "call",
        risk_free_rate: float = 0.03,
    ) -> float:
        """计算隐含波动率"""
        return self._execute_api_mapped(
            "calculate_implied_vol",
            option_code=option_code,
            option_price=option_price,
            underlying_price=underlying_price,
            strike=strike,
            days_to_expiry=days_to_expiry,
            option_type=option_type,
            risk_free_rate=risk_free_rate,
        )


class OptionGreeksFactory(BaseFactory[OptionGreeksProvider]):
    _providers: dict[str, type[OptionGreeksProvider]] = {}
