import warnings
warnings.warn(
    "Import from 'modules.disclosure' is deprecated. Use 'modules.providers.equities.fundamentals.disclosure' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.fundamentals.disclosure import *
