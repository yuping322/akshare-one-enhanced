import warnings
warnings.warn(
    "Import from 'modules.ipo' is deprecated. Use 'modules.providers.equities.corporate_events.ipo' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.corporate_events.ipo import *
