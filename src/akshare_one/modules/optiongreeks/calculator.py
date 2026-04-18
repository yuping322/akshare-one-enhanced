from ..base import BaseProvider


class CalculatorProvider(BaseProvider):
    def get_source_name(self) -> str:
        return "calculator"

    def get_data_type(self) -> str:
        return "optiongreeks"

    def get_option_greeks(
        self,
        option_code: str,
        underlying_price: float,
        strike: float,
        days_to_expiry: int,
        option_price: float,
        option_type: str = "call",
        risk_free_rate: float = 0.03,
    ) -> dict:
        from . import calculate_greeks

        return calculate_greeks(underlying_price, strike, days_to_expiry, option_price, option_type, risk_free_rate)

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
        from . import calculate_implied_vol

        return calculate_implied_vol(
            option_price, underlying_price, strike, days_to_expiry, option_type, risk_free_rate
        )


# Register
from .base import OptionGreeksFactory

OptionGreeksFactory._providers["calculator"] = CalculatorProvider
