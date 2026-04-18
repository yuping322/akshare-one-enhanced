import warnings
warnings.warn(
    "Import from 'modules.blockdeal' is deprecated. Use 'modules.providers.equities.trading_events.block_deal' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.trading_events.block_deal import *
