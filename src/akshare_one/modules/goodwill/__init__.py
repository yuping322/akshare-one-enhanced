import warnings
warnings.warn(
    "Import from 'modules.goodwill' is deprecated. Use 'modules.providers.equities.corporate_events.goodwill' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.corporate_events.goodwill import *
