import warnings
warnings.warn(
    "Import from 'modules.margin' is deprecated. Use 'modules.providers.equities.capital.margin' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.capital.margin import *
