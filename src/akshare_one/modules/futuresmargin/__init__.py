"""
Futures margin data module.
"""

import warnings

warnings.warn(
    "Import from 'modules.futuresmargin' is deprecated. Use 'modules.providers.derivatives.futures.margin' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.derivatives.futures.margin import *
