"""
Index weights data module.
"""

import warnings

warnings.warn(
    "Import from 'modules.indexweights' is deprecated. Use 'modules.providers.indices.weights' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.indices.weights import *
