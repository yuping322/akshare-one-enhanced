import warnings
warnings.warn(
    "Import from 'modules.financial' is deprecated. Use 'modules.providers.equities.fundamentals.financial' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.fundamentals.financial import *
