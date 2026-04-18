"""
Deprecated: This module has been moved.
"""
import warnings
warnings.warn(
    "Import from 'akshare_one.modules.fund_manager' is deprecated. Use 'akshare_one.modules.providers.funds.entities' instead.",
    DeprecationWarning,
    stacklevel=2
)
from akshare_one.modules.providers.funds.entities import *
