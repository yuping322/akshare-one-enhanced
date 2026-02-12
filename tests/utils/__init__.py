"""
Test utilities for akshare-one testing framework.

This package provides utilities for:
- Contract testing (golden samples)
- Integration testing helpers
- Test data fixtures
- Mock data generators
"""

from .contract_test import (
    GoldenSampleValidator,
    create_golden_sample_if_missing,
)

__all__ = [
    'GoldenSampleValidator',
    'create_golden_sample_if_missing',
]
