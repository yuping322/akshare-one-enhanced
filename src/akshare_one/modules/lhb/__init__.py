import warnings
warnings.warn(
    "Import from 'modules.lhb' is deprecated. Use 'modules.providers.equities.trading_events.dragon_tiger' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.trading_events.dragon_tiger import *
