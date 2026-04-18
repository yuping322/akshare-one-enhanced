"""
Share change depth data module.
"""

import warnings

warnings.warn(
    "Import from 'modules.sharechangedepth' is deprecated. Use 'modules.providers.equities.corporate_events.shareholder.changes' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.equities.corporate_events.shareholder.changes import *
