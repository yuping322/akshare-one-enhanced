import warnings
warnings.warn(
    "Import from 'modules.limitup' is deprecated. Use 'modules.providers.equities.trading_events.limit_up' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.trading_events.limit_up import *
