import warnings

warnings.warn(
    "Import from 'modules.factory_base' is deprecated. Use 'modules.core.factory' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from .core.factory import *
