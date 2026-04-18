"""
LOF (Listed Open-Ended Fund) data module.
"""

import warnings

warnings.warn(
    "Import from 'modules.lof' is deprecated. Use 'modules.providers.funds.lof' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.funds.lof import *
