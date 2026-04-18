import warnings

warnings.warn(
    "Import from 'modules.base' is deprecated. Use 'modules.core.base' instead.", DeprecationWarning, stacklevel=2
)
from .core.base import *
