"""
Dividend calculation helpers module.

Provides utilities for dividend and rights calculation:
- Ex-rights price calculation
- Adjusted price calculation
- Stock bonus and rights issue queries
"""

import warnings

warnings.warn(
    "Import from 'modules.dividendcalc' is deprecated. Use 'modules.providers.equities.fundamentals.dividend.calc' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.equities.fundamentals.dividend.calc import *
