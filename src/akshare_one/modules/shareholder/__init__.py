import warnings
warnings.warn(
    "Import from 'modules.shareholder' is deprecated. Use 'modules.providers.equities.corporate_events.shareholder' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.corporate_events.shareholder import *
