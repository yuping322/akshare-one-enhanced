import warnings
warnings.warn(
    "Import from 'modules.dividend' is deprecated. Use 'modules.providers.equities.fundamentals.dividend' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.fundamentals.dividend import *
