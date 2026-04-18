"""
Shareholder depth data module.

This module provides extended shareholder APIs including shareholder structure,
shareholder concentration, and top float shareholders.
"""

import warnings

warnings.warn(
    "Import from 'modules.shareholderdepth' is deprecated. Use 'modules.providers.equities.corporate_events.shareholder.depth' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.equities.corporate_events.shareholder.depth import *
