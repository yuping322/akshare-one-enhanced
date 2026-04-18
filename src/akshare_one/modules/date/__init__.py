import warnings

warnings.warn(
    "Import from 'modules.date' is deprecated. Use 'modules.core.calendar' instead.", DeprecationWarning, stacklevel=2
)
from ..core.calendar import *
