"""
Macro AkShare data module.
"""

import warnings

warnings.warn(
    "Import from 'modules.macroakshare' is deprecated. Use 'modules.providers.macro.akshare_source' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.macro.akshare_source import *
