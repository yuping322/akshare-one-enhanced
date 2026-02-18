"""Tests for utility functions."""

import pytest


class TestSymbolConversion:
    """Test symbol conversion utilities."""

    def test_convert_xieqiu_symbol_shanghai(self):
        """Test converting Shanghai A-share symbols."""
        from akshare_one.modules.utils import convert_xieqiu_symbol

        # 主板
        assert convert_xieqiu_symbol("600000") == "SH600000"
        assert convert_xieqiu_symbol("601398") == "SH601398"
        assert convert_xieqiu_symbol("603000") == "SH603000"
        # 科创板
        assert convert_xieqiu_symbol("688001") == "SH688001"

    def test_convert_xieqiu_symbol_shenzhen(self):
        """Test converting Shenzhen A-share symbols."""
        from akshare_one.modules.utils import convert_xieqiu_symbol

        # 主板
        assert convert_xieqiu_symbol("000001") == "SZ000001"
        assert convert_xieqiu_symbol("000002") == "SZ000002"
        # 中小板
        assert convert_xieqiu_symbol("002001") == "SZ002001"
        # 创业板
        assert convert_xieqiu_symbol("300001") == "SZ300001"

    def test_convert_xieqiu_symbol_already_formatted(self):
        """Test symbols already in XueQiu format."""
        from akshare_one.modules.utils import convert_xieqiu_symbol

        assert convert_xieqiu_symbol("SH600000") == "SH600000"
        assert convert_xieqiu_symbol("SZ000001") == "SZ000001"

    def test_convert_xieqiu_symbol_us_stocks(self):
        """Test US stock symbols."""
        from akshare_one.modules.utils import convert_xieqiu_symbol

        assert convert_xieqiu_symbol("AAPL") == "AAPL"
        assert convert_xieqiu_symbol("MSFT") == "MSFT"

    def test_convert_xieqiu_symbol_empty(self):
        """Test empty symbol."""
        from akshare_one.modules.utils import convert_xieqiu_symbol

        assert convert_xieqiu_symbol("") == ""


class TestNormalizeSymbol:
    """Test symbol normalization."""

    def test_normalize_with_prefix(self):
        """Test removing prefix."""
        from akshare_one.modules.utils import normalize_symbol

        assert normalize_symbol("SH600000") == "600000"
        assert normalize_symbol("SZ000001") == "SZ000001"[2:]

    def test_normalize_with_suffix(self):
        """Test removing suffix."""
        from akshare_one.modules.utils import normalize_symbol

        assert normalize_symbol("600000.SH") == "600000"
        assert normalize_symbol("000001.SZ") == "000001"

    def test_normalize_clean(self):
        """Test already clean symbol."""
        from akshare_one.modules.utils import normalize_symbol

        assert normalize_symbol("600000") == "600000"


class TestDetectMarket:
    """Test market detection."""

    def test_detect_shanghai(self):
        """Test detecting Shanghai market."""
        from akshare_one.modules.utils import detect_market

        assert detect_market("600000") == "sh"
        assert detect_market("688001") == "sh"
        assert detect_market("SH600000") == "sh"

    def test_detect_shenzhen(self):
        """Test detecting Shenzhen market."""
        from akshare_one.modules.utils import detect_market

        assert detect_market("000001") == "sz"
        assert detect_market("300001") == "sz"
        assert detect_market("SZ000001") == "sz"

    def test_detect_us(self):
        """Test detecting US market."""
        from akshare_one.modules.utils import detect_market

        assert detect_market("AAPL") == "us"
        assert detect_market("MSFT") == "us"

    def test_detect_empty(self):
        """Test empty symbol."""
        from akshare_one.modules.utils import detect_market

        assert detect_market("") == "unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
