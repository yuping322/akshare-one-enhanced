"""
Company depth data module.

This module provides extended company information APIs including security status,
name history, management info, employee info, listing info, and industry info.
"""

import warnings

warnings.warn(
    "Import from 'modules.companydepth' is deprecated. Use 'modules.providers.equities.fundamentals.info.depth' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.equities.fundamentals.info.depth import *
