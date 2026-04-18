"""
Northbound depth data module.
"""

import warnings

warnings.warn(
    "Import from 'modules.northbounddepth' is deprecated. Use 'modules.providers.equities.capital.northbound.depth' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.equities.capital.northbound.depth import *
