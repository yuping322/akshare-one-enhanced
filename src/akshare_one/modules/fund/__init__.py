"""
Deprecated: This module has been moved.
"""
import warnings
warnings.warn(
    "Import from 'akshare_one.modules.fund' is deprecated. Use 'akshare_one.modules.providers.funds.mutual' instead.",
    DeprecationWarning,
    stacklevel=2
)
from akshare_one.modules.providers.funds.mutual import *
