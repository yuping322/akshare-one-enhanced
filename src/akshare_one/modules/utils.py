import warnings

warnings.warn(
    "Import from 'modules.utils' is deprecated. Use 'modules.core.symbols' instead.", DeprecationWarning, stacklevel=2
)
from .core.symbols import *
