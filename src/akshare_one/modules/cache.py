import warnings

warnings.warn(
    "Import from 'modules.cache' is deprecated. Use 'modules.core.cache' instead.", DeprecationWarning, stacklevel=2
)
from .core.cache import *
