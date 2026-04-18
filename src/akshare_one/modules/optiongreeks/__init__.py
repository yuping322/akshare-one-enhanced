"""
Option Greeks calculator module.
"""

import warnings

warnings.warn(
    "Import from 'modules.optiongreeks' is deprecated. Use 'modules.providers.derivatives.options.greeks' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.derivatives.options.greeks import *
