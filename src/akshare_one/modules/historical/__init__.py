import warnings
warnings.warn(
    "Import from 'modules.historical' is deprecated. Use 'modules.providers.equities.quotes.historical' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.quotes.historical import *
