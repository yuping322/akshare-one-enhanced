"""
Call Auction (集合竞价) data module for akshare-one.

This module provides interfaces to fetch call auction data including:
- Single stock call auction data
- Batch call auction data for multiple stocks
"""

import warnings

warnings.warn(
    "Import from 'modules.callauction' is deprecated. Use 'modules.providers.equities.trading_events.call_auction' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.equities.trading_events.call_auction import *
