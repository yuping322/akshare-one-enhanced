import warnings
warnings.warn(
    "Import from 'modules.restricted' is deprecated. Use 'modules.providers.equities.corporate_events.restricted' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.corporate_events.restricted import *
