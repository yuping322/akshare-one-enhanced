import warnings
warnings.warn(
    "Import from 'modules.realtime' is deprecated. Use 'modules.providers.equities.quotes.realtime' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.quotes.realtime import *
