"""
src/akshare_one/jq_compat/order.py
JQ-compatible order and portfolio management APIs.
Note: These require a running strategy context for actual execution.
"""

import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class LimitOrderStyle:
    """Limit order style."""
    def __init__(self, limit_price: float):
        self.limit_price = limit_price


class MarketOrderStyle:
    """Market order style."""
    def __init__(self):
        pass


def order_shares(security: str, amount: int,
                 style: Optional[Union[LimitOrderStyle, MarketOrderStyle]] = None):
    """Place order by shares. Requires running strategy context. JQ-compatible."""
    logger.warning("order_shares requires a running strategy context.")
    return None


def order_target_percent(security: str, percent: float,
                         style: Optional[Union[LimitOrderStyle, MarketOrderStyle]] = None):
    """Place order to target percent. Requires running strategy context. JQ-compatible."""
    logger.warning("order_target_percent requires a running strategy context.")
    return None


def rebalance_portfolio(target_weights: Dict[str, float], stock_list: Optional[List[str]] = None):
    """Rebalance portfolio to target weights. JQ-compatible."""
    for security, weight in target_weights.items():
        order_target_percent(security, weight)


def get_portfolio_weights() -> Dict[str, float]:
    """Get current portfolio weights. Requires running strategy context. JQ-compatible."""
    logger.warning("get_portfolio_weights requires a running strategy context.")
    return {}


def calculate_position_value(security: str, amount: Optional[int] = None) -> float:
    """Calculate position market value. JQ-compatible."""
    from .market import get_close_price
    from ..modules.utils import normalize_symbol
    sym = normalize_symbol(security)
    price = get_close_price(sym)
    if amount is None:
        return 0.0
    return float(amount) * float(price)


def get_position_ratio(security: str) -> float:
    """Get current position ratio. Requires running strategy context. JQ-compatible."""
    logger.warning("get_position_ratio requires a running strategy context.")
    return 0.0


def will_sell_on_limit_up(security: str) -> bool:
    """Check if security is at limit up. JQ-compatible."""
    from ..modules.utils import normalize_symbol
    from .cache import get_current_data_cached
    try:
        sym = normalize_symbol(security)
        data = get_current_data_cached(sym)
        last_price = data.get("last_price") or data.get("price", 0)
        high_limit = data.get("high_limit", float("inf"))
        return float(last_price) >= float(high_limit) * 0.999
    except Exception as e:
        logger.debug(f"will_sell_on_limit_up failed for '{security}': {e}")
        return False


def will_buy_on_limit_down(security: str) -> bool:
    """Check if security is at limit down. JQ-compatible."""
    from ..modules.utils import normalize_symbol
    from .cache import get_current_data_cached
    try:
        sym = normalize_symbol(security)
        data = get_current_data_cached(sym)
        last_price = data.get("last_price") or data.get("price", 0)
        low_limit = data.get("low_limit", 0)
        return float(last_price) <= float(low_limit) * 1.001
    except Exception as e:
        logger.debug(f"will_buy_on_limit_down failed for '{security}': {e}")
        return False


__all__ = [
    "order_shares", "order_target_percent", "LimitOrderStyle", "MarketOrderStyle",
    "rebalance_portfolio", "calculate_position_value", "get_position_ratio",
    "will_sell_on_limit_up", "will_buy_on_limit_down", "get_portfolio_weights",
]
