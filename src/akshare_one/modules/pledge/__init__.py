import warnings
warnings.warn(
    "Import from 'modules.pledge' is deprecated. Use 'modules.providers.equities.corporate_events.pledge' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.corporate_events.pledge import *
