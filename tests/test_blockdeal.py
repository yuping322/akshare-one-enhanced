"""
Unit tests for block deal data module.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from akshare_one.modules.blockdeal import (
    get_block_deal,
)
from akshare_one.modules.blockdeal.eastmoney import EastmoneyBlockDealProvider
from akshare_one.modules.blockdeal import BlockDealFactory


class TestBlockDealFactory:
    """Test BlockDealFactory class."""

    def test_get_provider_eastmoney(self):
        """Test getting eastmoney provider."""
        provider = BlockDealFactory.get_provider('eastmoney')
        assert isinstance(provider, EastmoneyBlockDealProvider)

    def test_get_provider_invalid_source(self):
        """Test getting provider with invalid source.

        Note: Exception is mapped from internal InvalidParameterError to standard ValueError
        for public API contract.
        """
        with pytest.raises(ValueError, match="Unsupported data source"):
            BlockDealFactory.get_provider('invalid')


class TestEastmoneyBlockDealProvider:
    """Test EastmoneyBlockDealProvider class."""