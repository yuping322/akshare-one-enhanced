"""
Option Greeks calculator provider - Black-Scholes pricing and Greeks calculation.
"""

import numpy as np
from math import log, sqrt
from scipy import stats

import pandas as pd

from ....core.base import BaseProvider
from .base import OptionsDataFactory


def black_scholes_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """Black-Scholes option pricing formula."""
    if T <= 0 or sigma <= 0:
        return max(S - K, 0) if option_type == "call" else max(K - S, 0)

    d1 = (log(S / K) + (r + sigma**2 / 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    if option_type == "call":
        return S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)


def calculate_implied_vol(
    option_price: float,
    underlying_price: float,
    strike: float,
    days_to_expiry: int,
    option_type: str = "call",
    risk_free_rate: float = 0.03,
    max_iter: int = 1000,
    tol: float = 1e-6,
) -> float:
    """Calculate implied volatility using Newton-Raphson method."""
    T = days_to_expiry / 365.0
    if T <= 0:
        return 0.0

    sigma = 0.3
    for _ in range(max_iter):
        price = black_scholes_price(underlying_price, strike, T, risk_free_rate, sigma, option_type)
        diff = option_price - price
        if abs(diff) < tol:
            return sigma
        d1 = (log(underlying_price / strike) + (risk_free_rate + sigma**2 / 2) * T) / (sigma * sqrt(T))
        vega = underlying_price * stats.norm.pdf(d1) * sqrt(T)
        if vega == 0:
            break
        sigma += diff / vega
        sigma = max(0.01, min(sigma, 5.0))

    return sigma


def calculate_greeks(
    underlying_price: float,
    strike: float,
    days_to_expiry: int,
    option_price: float,
    option_type: str = "call",
    risk_free_rate: float = 0.03,
) -> dict:
    """Calculate option Greeks."""
    T = days_to_expiry / 365.0
    sigma = calculate_implied_vol(option_price, underlying_price, strike, days_to_expiry, option_type, risk_free_rate)

    if T <= 0 or sigma <= 0:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0, "implied_volatility": 0}

    d1 = (log(underlying_price / strike) + (risk_free_rate + sigma**2 / 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    if option_type == "call":
        delta = stats.norm.cdf(d1)
        theta = (
            -(underlying_price * stats.norm.pdf(d1) * sigma) / (2 * sqrt(T))
            - risk_free_rate * strike * np.exp(-risk_free_rate * T) * stats.norm.cdf(d2)
        ) / 365
        rho = strike * T * np.exp(-risk_free_rate * T) * stats.norm.cdf(d2) / 100
    else:
        delta = stats.norm.cdf(d1) - 1
        theta = (
            -(underlying_price * stats.norm.pdf(d1) * sigma) / (2 * sqrt(T))
            + risk_free_rate * strike * np.exp(-risk_free_rate * T) * stats.norm.cdf(-d2)
        ) / 365
        rho = -strike * T * np.exp(-risk_free_rate * T) * stats.norm.cdf(-d2) / 100

    gamma = stats.norm.pdf(d1) / (underlying_price * sigma * sqrt(T))
    vega = underlying_price * stats.norm.pdf(d1) * sqrt(T) / 100

    return {
        "delta": round(delta, 6),
        "gamma": round(gamma, 6),
        "theta": round(theta, 6),
        "vega": round(vega, 6),
        "rho": round(rho, 6),
        "implied_volatility": round(sigma, 6),
    }


class OptionGreeksProvider(BaseProvider):
    """Provider for option Greeks calculations."""

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
    ) -> dict:
        """Calculate option Greeks."""
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
        """Calculate implied volatility."""
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


class OptionGreeksFactory(OptionsDataFactory):
    """Factory for option Greeks data providers."""

    pass


@OptionGreeksFactory.register("calculator")
class CalculatorProvider(OptionGreeksProvider):
    """Calculator-based option Greeks provider."""

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
        return calculate_implied_vol(
            option_price, underlying_price, strike, days_to_expiry, option_type, risk_free_rate
        )
