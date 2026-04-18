import warnings

warnings.warn(
    "Import from 'modules.exceptions' is deprecated. Use 'modules.core.exceptions' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from .core.exceptions import *
