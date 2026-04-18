import warnings
warnings.warn(
    "Import from 'modules.insider' is deprecated. Use 'modules.providers.equities.corporate_events.insider' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.corporate_events.insider import *
