import warnings
warnings.warn(
    "Import from 'modules.analyst' is deprecated. Use 'modules.providers.equities.corporate_events.analyst' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.corporate_events.analyst import *
