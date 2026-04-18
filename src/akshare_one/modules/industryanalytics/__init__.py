"""
Industry analytics data module.
"""

import warnings

warnings.warn(
    "Import from 'modules.industryanalytics' is deprecated. Use 'modules.providers.sectors.industry.analytics' instead.",
    DeprecationWarning,
    stacklevel=2,
)
from ..providers.sectors.industry.analytics import *
