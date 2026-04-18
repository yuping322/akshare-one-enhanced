import warnings
warnings.warn(
    "Import from 'modules.northbound' is deprecated. Use 'modules.providers.equities.capital.northbound' instead.",
    DeprecationWarning,
    stacklevel=2
)
from ..providers.equities.capital.northbound import *
