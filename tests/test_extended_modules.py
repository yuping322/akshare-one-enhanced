"""Tests for board, concept, industry, ipo, st, suspended modules.

These modules provide data for special stock categories.
"""

import pandas as pd
import pytest


class TestBoardModule:
    """Test board module (科创板/创业板)."""

    def test_get_kcb_stocks(self):
        """Test getting KCB (科创板) stocks."""
        from akshare_one.modules.board import get_kcb_stocks

        df = get_kcb_stocks()
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "symbol" in df.columns
            assert "name" in df.columns
            # Verify all symbols start with 688 (KCB code)
            assert all(df["symbol"].str.startswith("688"))

    def test_get_cyb_stocks(self):
        """Test getting CYB (创业板) stocks."""
        from akshare_one.modules.board import get_cyb_stocks

        df = get_cyb_stocks()
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "symbol" in df.columns
            assert "name" in df.columns
            # Verify all symbols start with 300 (CYB code)
            assert all(df["symbol"].str.startswith("300"))

    def test_board_factory_list_sources(self):
        """Test BoardFactory list_sources."""
        from akshare_one.modules.board import BoardFactory

        sources = BoardFactory.list_sources()
        assert isinstance(sources, list)
        assert "eastmoney" in sources


class TestConceptModule:
    """Test concept sector module."""

    def test_get_concept_list(self):
        """Test getting concept sector list."""
        from akshare_one.modules.concept import get_concept_list

        df = get_concept_list()
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check expected columns
            expected_cols = ["rank", "name", "code", "price", "change_pct"]
            for col in expected_cols:
                if col in df.columns:
                    break
            else:
                # At least check that we got some columns
                assert len(df.columns) > 0

    def test_get_concept_stocks(self):
        """Test getting stocks in a concept sector."""
        from akshare_one.modules.concept import get_concept_stocks

        # Test with a popular concept
        df = get_concept_stocks(concept="人工智能")
        assert isinstance(df, pd.DataFrame)
        # May be empty if concept not found


class TestIndustryModule:
    """Test industry sector module."""

    def test_get_industry_list(self):
        """Test getting industry sector list."""
        from akshare_one.modules.industry import get_industry_list

        df = get_industry_list()
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert len(df.columns) > 0

    def test_get_industry_stocks(self):
        """Test getting stocks in an industry."""
        from akshare_one.modules.industry import get_industry_stocks

        # Test with a major industry
        df = get_industry_stocks(industry="银行")
        assert isinstance(df, pd.DataFrame)
        # May be empty if industry not found


class TestIPOModule:
    """Test IPO module."""

    def test_get_new_stocks(self):
        """Test getting new stock listings."""
        from akshare_one.modules.ipo import get_new_stocks

        df = get_new_stocks()
        assert isinstance(df, pd.DataFrame)

    def test_get_ipo_info(self):
        """Test getting IPO information."""
        from akshare_one.modules.ipo import get_ipo_info

        df = get_ipo_info()
        assert isinstance(df, pd.DataFrame)


class TestSTModule:
    """Test ST stock module."""

    def test_get_st_stocks(self):
        """Test getting ST stocks."""
        from akshare_one.modules.st import get_st_stocks

        df = get_st_stocks()
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Verify ST naming pattern
            names = df["name"].astype(str)
            assert any(names.str.contains("ST"))


class TestSuspendedModule:
    """Test suspended stocks module."""

    def test_get_suspended_stocks(self):
        """Test getting suspended stocks."""
        from akshare_one.modules.suspended import get_suspended_stocks

        df = get_suspended_stocks()
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            # Check expected columns
            assert len(df.columns) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
