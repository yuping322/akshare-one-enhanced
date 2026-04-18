import warnings
warnings.warn(
    "Import from 'modules.fundflow' is deprecated. Use 'modules.providers.equities.capital.fundflow' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.capital.fundflow import *
