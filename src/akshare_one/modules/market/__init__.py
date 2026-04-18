import warnings
warnings.warn(
    "Import from 'modules.market' is deprecated. Use 'modules.providers.equities.market_infra' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.market_infra import *
