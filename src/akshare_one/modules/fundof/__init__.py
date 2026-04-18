"""
FOF (Fund of Funds) data module.
"""

import warnings

warnings.warn(
    "Import from 'modules.fundof' is deprecated. Use 'modules.providers.funds.fund_of' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.funds.fund_of import *
