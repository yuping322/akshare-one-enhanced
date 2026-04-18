import warnings
warnings.warn(
    "Import from 'modules.esg' is deprecated. Use 'modules.providers.equities.fundamentals.esg' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.fundamentals.esg import *
