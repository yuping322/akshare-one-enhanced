"""
Deprecated: This module has been moved.
"""
import warnings
warnings.warn(
    "Import from 'akshare_one.modules.hkus' is deprecated. Use 'akshare_one.modules.providers.hk_equities' instead.",
    DeprecationWarning,
    stacklevel=2
)
from akshare_one.modules.providers.hk_equities import *
