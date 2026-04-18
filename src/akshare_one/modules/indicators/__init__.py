"""
Technical indicator calculation module.

DEPRECATED: Use modules.calculators.technical instead.
"""

import warnings

warnings.warn(
    "Import from 'modules.indicators' is deprecated. Use 'modules.calculators.technical' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from ..calculators.technical import *
