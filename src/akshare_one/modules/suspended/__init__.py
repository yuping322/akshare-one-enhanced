import warnings

warnings.warn(
    "Import from 'modules.suspended' is deprecated. Use 'modules.providers.equities.corporate_events.status' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.equities.corporate_events.status import *
