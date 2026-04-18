import warnings
warnings.warn(
    "Import from 'modules.performance' is deprecated. Use 'modules.providers.equities.fundamentals.performance' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.fundamentals.performance import *
