import warnings
warnings.warn(
    "Import from 'modules.info' is deprecated. Use 'modules.providers.equities.fundamentals.info' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.fundamentals.info import *
