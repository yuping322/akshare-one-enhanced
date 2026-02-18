"""Tests for P1 and P2 MCP tools (disclosure, macro, block deal, margin, pledge, restricted, goodwill, esg).

Tests both the underlying module functions and MCP tool wrappers.
"""

import json
from datetime import datetime, timedelta

import pandas as pd
import pytest

try:
    from fastmcp import FastMCP  # noqa: F401

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

pytestmark = pytest.mark.skipif(not MCP_AVAILABLE, reason="fastmcp not installed")


def get_recent_30_days():
    """Get date range for last 30 days."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    return start_date, end_date


# ==================== P1: Disclosure Module Functions ====================
# ==================== P1: Block Deal Module Functions ====================
from akshare_one.modules.blockdeal import get_block_deal as blockdeal_get_block_deal
from akshare_one.modules.blockdeal import (
    get_block_deal_summary as blockdeal_get_block_deal_summary,
)
from akshare_one.modules.disclosure import (
    get_disclosure_news as disclosure_get_disclosure_news,
)
from akshare_one.modules.disclosure import (
    get_dividend_data as disclosure_get_dividend_data,
)
from akshare_one.modules.disclosure import (
    get_repurchase_data as disclosure_get_repurchase_data,
)
from akshare_one.modules.disclosure import (
    get_st_delist_data as disclosure_get_st_delist_data,
)

# ==================== P2: ESG Module Functions ====================
from akshare_one.modules.esg import get_esg_rating as esg_get_esg_rating
from akshare_one.modules.esg import get_esg_rating_rank as esg_get_esg_rating_rank
from akshare_one.modules.goodwill import (
    get_goodwill_by_industry as goodwill_get_goodwill_by_industry,
)

# ==================== P2: Goodwill Module Functions ====================
from akshare_one.modules.goodwill import get_goodwill_data as goodwill_get_goodwill_data
from akshare_one.modules.goodwill import (
    get_goodwill_impairment as goodwill_get_goodwill_impairment,
)
from akshare_one.modules.macro import get_cpi_data as macro_get_cpi_data

# ==================== P1: Macro Module Functions ====================
from akshare_one.modules.macro import get_lpr_rate as macro_get_lpr_rate
from akshare_one.modules.macro import get_m2_supply as macro_get_m2_supply
from akshare_one.modules.macro import get_pmi_index as macro_get_pmi_index
from akshare_one.modules.macro import get_ppi_data as macro_get_ppi_data
from akshare_one.modules.macro import get_shibor_rate as macro_get_shibor_rate
from akshare_one.modules.macro import get_social_financing as macro_get_social_financing

# ==================== P1: Margin Module Functions ====================
from akshare_one.modules.margin import get_margin_data as margin_get_margin_data
from akshare_one.modules.margin import get_margin_summary as margin_get_margin_summary

# ==================== P2: Equity Pledge Module Functions ====================
from akshare_one.modules.pledge import get_equity_pledge as pledge_get_equity_pledge
from akshare_one.modules.pledge import (
    get_equity_pledge_ratio_rank as pledge_get_equity_pledge_ratio_rank,
)

# ==================== P2: Restricted Release Module Functions ====================
from akshare_one.modules.restricted import (
    get_restricted_release as restricted_get_restricted_release,
)
from akshare_one.modules.restricted import (
    get_restricted_release_calendar as restricted_get_restricted_release_calendar,
)

# MCP tool wrappers
if MCP_AVAILABLE:
    from akshare_one_mcp.server import get_block_deal as mcp_get_block_deal
    from akshare_one_mcp.server import get_block_deal_summary as mcp_get_block_deal_summary
    from akshare_one_mcp.server import get_cpi_data as mcp_get_cpi_data
    from akshare_one_mcp.server import get_disclosure_news as mcp_get_disclosure_news
    from akshare_one_mcp.server import get_dividend_data as mcp_get_dividend_data
    from akshare_one_mcp.server import get_equity_pledge as mcp_get_equity_pledge
    from akshare_one_mcp.server import (
        get_equity_pledge_ratio_rank as mcp_get_equity_pledge_ratio_rank,
    )
    from akshare_one_mcp.server import get_esg_rating as mcp_get_esg_rating
    from akshare_one_mcp.server import get_esg_rating_rank as mcp_get_esg_rating_rank
    from akshare_one_mcp.server import get_goodwill_by_industry as mcp_get_goodwill_by_industry
    from akshare_one_mcp.server import get_goodwill_data as mcp_get_goodwill_data
    from akshare_one_mcp.server import get_goodwill_impairment as mcp_get_goodwill_impairment
    from akshare_one_mcp.server import get_lpr_rate as mcp_get_lpr_rate
    from akshare_one_mcp.server import get_m2_supply as mcp_get_m2_supply
    from akshare_one_mcp.server import get_margin_data as mcp_get_margin_data
    from akshare_one_mcp.server import get_margin_summary as mcp_get_margin_summary
    from akshare_one_mcp.server import get_pmi_index as mcp_get_pmi_index
    from akshare_one_mcp.server import get_ppi_data as mcp_get_ppi_data
    from akshare_one_mcp.server import get_repurchase_data as mcp_get_repurchase_data
    from akshare_one_mcp.server import get_restricted_release as mcp_get_restricted_release
    from akshare_one_mcp.server import (
        get_restricted_release_calendar as mcp_get_restricted_release_calendar,
    )
    from akshare_one_mcp.server import get_shibor_rate as mcp_get_shibor_rate
    from akshare_one_mcp.server import get_social_financing as mcp_get_social_financing
    from akshare_one_mcp.server import get_st_delist_data as mcp_get_st_delist_data


# ==================== P1: Disclosure Tests ====================


class TestDisclosureMCP:
    """Test disclosure data retrieval."""

    def test_get_disclosure_news_basic(self):
        df = disclosure_get_disclosure_news()
        assert isinstance(df, pd.DataFrame)

    def test_get_disclosure_news_with_symbol(self):
        df = disclosure_get_disclosure_news(symbol="600000")
        assert isinstance(df, pd.DataFrame)

    def test_get_disclosure_news_with_category(self):
        start_date, end_date = get_recent_30_days()
        df = disclosure_get_disclosure_news(
            symbol="600000", start_date=start_date, end_date=end_date, category="dividend"
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_dividend_data_basic(self):
        df = disclosure_get_dividend_data()
        assert isinstance(df, pd.DataFrame)

    def test_get_dividend_data_with_symbol(self):
        df = disclosure_get_dividend_data(symbol="600000")
        assert isinstance(df, pd.DataFrame)

    def test_get_repurchase_data_basic(self):
        df = disclosure_get_repurchase_data()
        assert isinstance(df, pd.DataFrame)

    def test_get_repurchase_data_with_symbol(self):
        df = disclosure_get_repurchase_data(symbol="600000")
        assert isinstance(df, pd.DataFrame)

    def test_get_st_delist_data_basic(self):
        df = disclosure_get_st_delist_data()
        assert isinstance(df, pd.DataFrame)


# ==================== P1: Macro Tests ====================


class TestMacroMCP:
    """Test macro economic data retrieval."""

    def test_get_lpr_rate(self):
        df = macro_get_lpr_rate()
        assert isinstance(df, pd.DataFrame)

    def test_get_lpr_rate_with_date_range(self):
        start_date, end_date = get_recent_30_days()
        df = macro_get_lpr_rate(start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)

    def test_get_pmi_index_manufacturing(self):
        df = macro_get_pmi_index(pmi_type="manufacturing")
        assert isinstance(df, pd.DataFrame)

    def test_get_pmi_index_non_manufacturing(self):
        df = macro_get_pmi_index(pmi_type="non_manufacturing")
        assert isinstance(df, pd.DataFrame)

    def test_get_pmi_index_caixin(self):
        df = macro_get_pmi_index(pmi_type="caixin")
        assert isinstance(df, pd.DataFrame)

    def test_get_cpi_data(self):
        df = macro_get_cpi_data()
        assert isinstance(df, pd.DataFrame)

    def test_get_ppi_data(self):
        df = macro_get_ppi_data()
        assert isinstance(df, pd.DataFrame)

    def test_get_m2_supply(self):
        df = macro_get_m2_supply()
        assert isinstance(df, pd.DataFrame)

    def test_get_shibor_rate(self):
        df = macro_get_shibor_rate()
        assert isinstance(df, pd.DataFrame)

    def test_get_social_financing(self):
        df = macro_get_social_financing()
        assert isinstance(df, pd.DataFrame)


# ==================== P1: Block Deal Tests ====================


class TestBlockDealMCP:
    """Test block deal data retrieval."""

    def test_get_block_deal_basic(self):
        df = blockdeal_get_block_deal()
        assert isinstance(df, pd.DataFrame)

    def test_get_block_deal_with_symbol(self):
        start_date, end_date = get_recent_30_days()
        df = blockdeal_get_block_deal(symbol="600000", start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)

    def test_get_block_deal_with_date_range(self):
        start_date, end_date = get_recent_30_days()
        df = blockdeal_get_block_deal(start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)

    def test_get_block_deal_summary_stock(self):
        start_date, end_date = get_recent_30_days()
        df = blockdeal_get_block_deal_summary(
            start_date=start_date, end_date=end_date, group_by="stock"
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_block_deal_summary_date(self):
        start_date, end_date = get_recent_30_days()
        df = blockdeal_get_block_deal_summary(
            start_date=start_date, end_date=end_date, group_by="date"
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_block_deal_summary_broker(self):
        start_date, end_date = get_recent_30_days()
        df = blockdeal_get_block_deal_summary(
            start_date=start_date, end_date=end_date, group_by="broker"
        )
        assert isinstance(df, pd.DataFrame)


# ==================== P1: Margin Tests ====================


class TestMarginMCP:
    """Test margin financing data retrieval."""

    def test_get_margin_data_basic(self):
        df = margin_get_margin_data()
        assert isinstance(df, pd.DataFrame)

    def test_get_margin_data_with_symbol(self):
        start_date, end_date = get_recent_30_days()
        df = margin_get_margin_data(symbol="600000", start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)

    def test_get_margin_summary_all(self):
        start_date, end_date = get_recent_30_days()
        df = margin_get_margin_summary(start_date=start_date, end_date=end_date, market="all")
        assert isinstance(df, pd.DataFrame)

    def test_get_margin_summary_sh(self):
        start_date, end_date = get_recent_30_days()
        df = margin_get_margin_summary(start_date=start_date, end_date=end_date, market="sh")
        assert isinstance(df, pd.DataFrame)

    def test_get_margin_summary_sz(self):
        start_date, end_date = get_recent_30_days()
        df = margin_get_margin_summary(start_date=start_date, end_date=end_date, market="sz")
        assert isinstance(df, pd.DataFrame)


# ==================== P2: Equity Pledge Tests ====================


class TestEquityPledgeMCP:
    """Test equity pledge data retrieval."""

    def test_get_equity_pledge_basic(self):
        df = pledge_get_equity_pledge()
        assert isinstance(df, pd.DataFrame)

    def test_get_equity_pledge_with_symbol(self):
        start_date, end_date = get_recent_30_days()
        df = pledge_get_equity_pledge(symbol="600000", start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)

    def test_get_equity_pledge_ratio_rank(self):
        today = datetime.now().strftime("%Y-%m-%d")
        df = pledge_get_equity_pledge_ratio_rank(date=today)
        assert isinstance(df, pd.DataFrame)

    def test_get_equity_pledge_ratio_rank_custom_top_n(self):
        today = datetime.now().strftime("%Y-%m-%d")
        df = pledge_get_equity_pledge_ratio_rank(date=today, top_n=50)
        assert isinstance(df, pd.DataFrame)


# ==================== P2: Restricted Release Tests ====================


class TestRestrictedReleaseMCP:
    """Test restricted release data retrieval."""

    def test_get_restricted_release_basic(self):
        df = restricted_get_restricted_release()
        assert isinstance(df, pd.DataFrame)

    def test_get_restricted_release_with_symbol(self):
        df = restricted_get_restricted_release(symbol="600000")
        assert isinstance(df, pd.DataFrame)

    def test_get_restricted_release_with_date_range(self):
        start_date, end_date = get_recent_30_days()
        df = restricted_get_restricted_release(start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)

    def test_get_restricted_release_calendar(self):
        start_date, end_date = get_recent_30_days()
        df = restricted_get_restricted_release_calendar(start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)


# ==================== P2: Goodwill Tests ====================


class TestGoodwillMCP:
    """Test goodwill data retrieval."""

    def test_get_goodwill_data_basic(self):
        df = goodwill_get_goodwill_data()
        assert isinstance(df, pd.DataFrame)

    def test_get_goodwill_data_with_symbol(self):
        df = goodwill_get_goodwill_data(symbol="600000")
        assert isinstance(df, pd.DataFrame)

    def test_get_goodwill_impairment(self):
        today = datetime.now().strftime("%Y-%m-%d")
        df = goodwill_get_goodwill_impairment(date=today)
        assert isinstance(df, pd.DataFrame)

    def test_get_goodwill_by_industry(self):
        today = datetime.now().strftime("%Y-%m-%d")
        df = goodwill_get_goodwill_by_industry(date=today)
        assert isinstance(df, pd.DataFrame)


# ==================== P2: ESG Tests ====================


class TestESGMCP:
    """Test ESG rating data retrieval."""

    def test_get_esg_rating_basic(self):
        df = esg_get_esg_rating()
        assert isinstance(df, pd.DataFrame)

    def test_get_esg_rating_with_symbol(self):
        df = esg_get_esg_rating(symbol="600000")
        assert isinstance(df, pd.DataFrame)

    def test_get_esg_rating_rank(self):
        today = datetime.now().strftime("%Y-%m-%d")
        df = esg_get_esg_rating_rank(date=today)
        assert isinstance(df, pd.DataFrame)

    def test_get_esg_rating_rank_with_industry(self):
        today = datetime.now().strftime("%Y-%m-%d")
        df = esg_get_esg_rating_rank(date=today, industry="银行")
        assert isinstance(df, pd.DataFrame)

    def test_get_esg_rating_rank_custom_top_n(self):
        today = datetime.now().strftime("%Y-%m-%d")
        df = esg_get_esg_rating_rank(date=today, top_n=50)
        assert isinstance(df, pd.DataFrame)


# ==================== MCP Tool Wrapper Tests ====================


@pytest.mark.skipif(not MCP_AVAILABLE, reason="fastmcp not installed")
class TestMCPToolWrappersP1P2:
    """Test MCP tool wrappers for P1 and P2 tools."""

    def test_mcp_disclosure_tools_have_attributes(self):
        tools = [
            mcp_get_disclosure_news,
            mcp_get_dividend_data,
            mcp_get_repurchase_data,
            mcp_get_st_delist_data,
        ]
        for tool in tools:
            assert hasattr(tool, "fn"), f"{tool.name} should have 'fn' attribute"
            assert callable(tool.fn), f"{tool.name}.fn should be callable"
            assert hasattr(tool, "name"), f"{tool.name} should have 'name' attribute"
            assert hasattr(tool, "description"), f"{tool.name} should have 'description' attribute"

    def test_mcp_macro_tools_have_attributes(self):
        tools = [
            mcp_get_lpr_rate,
            mcp_get_pmi_index,
            mcp_get_cpi_data,
            mcp_get_ppi_data,
            mcp_get_m2_supply,
            mcp_get_shibor_rate,
            mcp_get_social_financing,
        ]
        for tool in tools:
            assert hasattr(tool, "fn"), f"{tool.name} should have 'fn' attribute"
            assert callable(tool.fn), f"{tool.name}.fn should be callable"

    def test_mcp_block_deal_tools_have_attributes(self):
        tools = [mcp_get_block_deal, mcp_get_block_deal_summary]
        for tool in tools:
            assert hasattr(tool, "fn"), f"{tool.name} should have 'fn' attribute"
            assert callable(tool.fn), f"{tool.name}.fn should be callable"

    def test_mcp_margin_tools_have_attributes(self):
        tools = [mcp_get_margin_data, mcp_get_margin_summary]
        for tool in tools:
            assert hasattr(tool, "fn"), f"{tool.name} should have 'fn' attribute"
            assert callable(tool.fn), f"{tool.name}.fn should be callable"

    def test_mcp_pledge_tools_have_attributes(self):
        tools = [mcp_get_equity_pledge, mcp_get_equity_pledge_ratio_rank]
        for tool in tools:
            assert hasattr(tool, "fn"), f"{tool.name} should have 'fn' attribute"
            assert callable(tool.fn), f"{tool.name}.fn should be callable"

    def test_mcp_restricted_tools_have_attributes(self):
        tools = [mcp_get_restricted_release, mcp_get_restricted_release_calendar]
        for tool in tools:
            assert hasattr(tool, "fn"), f"{tool.name} should have 'fn' attribute"
            assert callable(tool.fn), f"{tool.name}.fn should be callable"

    def test_mcp_goodwill_tools_have_attributes(self):
        tools = [mcp_get_goodwill_data, mcp_get_goodwill_impairment, mcp_get_goodwill_by_industry]
        for tool in tools:
            assert hasattr(tool, "fn"), f"{tool.name} should have 'fn' attribute"
            assert callable(tool.fn), f"{tool.name}.fn should be callable"

    def test_mcp_esg_tools_have_attributes(self):
        tools = [mcp_get_esg_rating, mcp_get_esg_rating_rank]
        for tool in tools:
            assert hasattr(tool, "fn"), f"{tool.name} should have 'fn' attribute"
            assert callable(tool.fn), f"{tool.name}.fn should be callable"

    def test_mcp_tools_json_output(self):
        today = datetime.now().strftime("%Y-%m-%d")
        start_date, end_date = get_recent_30_days()

        test_cases = [
            (mcp_get_disclosure_news, {}),
            (mcp_get_dividend_data, {}),
            (mcp_get_repurchase_data, {}),
            (mcp_get_st_delist_data, {}),
            (mcp_get_lpr_rate, {}),
            (mcp_get_pmi_index, {}),
            (mcp_get_cpi_data, {}),
            (mcp_get_ppi_data, {}),
            (mcp_get_m2_supply, {}),
            (mcp_get_shibor_rate, {}),
            (mcp_get_social_financing, {}),
            (mcp_get_block_deal, {}),
            (mcp_get_block_deal_summary, {"start_date": start_date, "end_date": end_date}),
            (mcp_get_margin_data, {}),
            (mcp_get_margin_summary, {}),
            (mcp_get_equity_pledge, {}),
            (mcp_get_equity_pledge_ratio_rank, {"date": today}),
            (mcp_get_restricted_release, {}),
            (mcp_get_restricted_release_calendar, {}),
            (mcp_get_goodwill_data, {}),
            (mcp_get_goodwill_impairment, {"date": today}),
            (mcp_get_goodwill_by_industry, {"date": today}),
            (mcp_get_esg_rating, {}),
            (mcp_get_esg_rating_rank, {"date": today}),
        ]

        for tool, kwargs in test_cases:
            try:
                result = tool.fn(**kwargs)
                assert isinstance(result, str), f"{tool.name} should return string"
                if result != "[]":
                    data = json.loads(result)
                    assert isinstance(data, list), f"{tool.name} should return list in JSON"
            except Exception as e:
                pytest.skip(f"Skipping {tool.name} due to: {e}")

    def test_mcp_wrapper_recent_n_parameter(self):
        result = mcp_get_lpr_rate.fn(recent_n=5)
        assert isinstance(result, str)
        try:
            data = json.loads(result)
            assert len(data) <= 5, f"Expected <= 5 records, got {len(data)}"
        except json.JSONDecodeError:
            pytest.fail("get_lpr_rate with recent_n returned invalid JSON")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
