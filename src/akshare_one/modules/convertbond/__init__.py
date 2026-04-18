"""
Convertible Bond (可转债) data module.

This module provides interfaces to fetch convertible bond data including:
- Convertible bond list
- Convertible bond details
- Historical quotes
- Realtime quotes
- Premium rates
- Stock-to-bond mapping
"""

import warnings

warnings.warn(
    "Import from 'modules.convertbond' is deprecated. Use 'modules.providers.fixed_income.convertible_bonds' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.fixed_income.convertible_bonds import *
