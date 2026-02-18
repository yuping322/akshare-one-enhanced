"""Tests for P0 MCP tools (fund flow, northbound, dragon tiger, limit up).

Tests both the underlying module functions and MCP tool wrappers.
"""

import json
from datetime import datetime, timedelta

import pandas as pd
import pytest

# Skip all MCP tests if fastmcp is not installed
try:
    from fastmcp import FastMCP  # noqa: F401

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

pytestmark = pytest.mark.skipif(not MCP_AVAILABLE, reason="fastmcp not installed")


# ==================== Helper Functions ====================


def get_recent_30_days():
    """Get date range for last 30 days."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    return start_date, end_date


# ==================== Direct Module Function Imports ====================
# These are the actual data retrieval functions we'll test directly

from akshare_one.modules.fundflow import (
    get_main_fund_flow_rank as fundflow_get_main_fund_flow_rank,
)
from akshare_one.modules.fundflow import (
    get_sector_fund_flow as fundflow_get_sector_fund_flow,
)
from akshare_one.modules.fundflow import (  # noqa: E402
    get_stock_fund_flow as fundflow_get_stock_fund_flow,
)
from akshare_one.modules.lhb import (
    get_dragon_tiger_broker_stats as lhb_get_dragon_tiger_broker_stats,
)
from akshare_one.modules.lhb import (  # noqa: E402
    get_dragon_tiger_list as lhb_get_dragon_tiger_list,
)
from akshare_one.modules.lhb import (
    get_dragon_tiger_summary as lhb_get_dragon_tiger_summary,
)
from akshare_one.modules.limitup import (
    get_limit_down_pool as limitup_get_limit_down_pool,
)
from akshare_one.modules.limitup import (  # noqa: E402
    get_limit_up_pool as limitup_get_limit_up_pool,
)
from akshare_one.modules.limitup import (
    get_limit_up_stats as limitup_get_limit_up_stats,
)
from akshare_one.modules.northbound import (  # noqa: E402
    get_northbound_flow as northbound_get_northbound_flow,
)
from akshare_one.modules.northbound import (
    get_northbound_holdings as northbound_get_northbound_holdings,
)
from akshare_one.modules.northbound import (
    get_northbound_top_stocks as northbound_get_northbound_top_stocks,
)

# MCP tool wrappers (only import if MCP is available, but allow TYPE_CHECKING)
if MCP_AVAILABLE:
    from akshare_one_mcp.server import (
        get_dragon_tiger_broker_stats as mcp_get_dragon_tiger_broker_stats,
    )
    from akshare_one_mcp.server import (
        get_dragon_tiger_list as mcp_get_dragon_tiger_list,
    )
    from akshare_one_mcp.server import (
        get_dragon_tiger_summary as mcp_get_dragon_tiger_summary,
    )
    from akshare_one_mcp.server import (
        get_limit_down_pool as mcp_get_limit_down_pool,
    )
    from akshare_one_mcp.server import (
        get_limit_up_pool as mcp_get_limit_up_pool,
    )
    from akshare_one_mcp.server import (
        get_limit_up_stats as mcp_get_limit_up_stats,
    )
    from akshare_one_mcp.server import (
        get_main_fund_flow_rank as mcp_get_main_fund_flow_rank,
    )
    from akshare_one_mcp.server import (
        get_northbound_flow as mcp_get_northbound_flow,
    )
    from akshare_one_mcp.server import (
        get_northbound_holdings as mcp_get_northbound_holdings,
    )
    from akshare_one_mcp.server import (
        get_northbound_top_stocks as mcp_get_northbound_top_stocks,
    )
    from akshare_one_mcp.server import (
        get_sector_fund_flow as mcp_get_sector_fund_flow,
    )
    from akshare_one_mcp.server import (  # noqa: F401
        get_stock_fund_flow as mcp_get_stock_fund_flow,
    )


# ==================== Fund Flow Tests ====================


class TestFundFlowMCP:
    """Test fund flow data retrieval."""

    def test_get_stock_fund_flow_basic(self):
        """Test basic stock fund flow retrieval."""
        df = fundflow_get_stock_fund_flow(symbol="600000")
        assert isinstance(df, pd.DataFrame)

    def test_get_stock_fund_flow_with_date_range(self):
        """Test stock fund flow with date range."""
        start_date, end_date = get_recent_30_days()
        df = fundflow_get_stock_fund_flow(symbol="600000", start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)

    def test_get_sector_fund_flow_industry(self):
        """Test industry sector fund flow."""
        df = fundflow_get_sector_fund_flow(sector_type="industry")
        assert isinstance(df, pd.DataFrame)

    def test_get_sector_fund_flow_concept(self):
        """Test concept sector fund flow."""
        df = fundflow_get_sector_fund_flow(sector_type="concept")
        assert isinstance(df, pd.DataFrame)

    def test_get_main_fund_flow_rank(self):
        """Test main fund flow ranking."""
        today = datetime.now().strftime("%Y-%m-%d")
        df = fundflow_get_main_fund_flow_rank(date=today)
        assert isinstance(df, pd.DataFrame)

    def test_get_main_fund_flow_rank_with_indicator(self):
        """Test main fund flow ranking with different indicator."""
        today = datetime.now().strftime("%Y-%m-%d")
        df = fundflow_get_main_fund_flow_rank(date=today, indicator="net_inflow_rate")
        assert isinstance(df, pd.DataFrame)


# ==================== Northbound Tests ====================


class TestNorthboundMCP:
    """Test northbound capital data retrieval."""

    def test_get_northbound_flow_all_market(self):
        """Test northbound flow for all markets."""
        df = northbound_get_northbound_flow(market="all")
        assert isinstance(df, pd.DataFrame)

    def test_get_northbound_flow_sh_market(self):
        """Test northbound flow for Shanghai market."""
        df = northbound_get_northbound_flow(market="sh")
        assert isinstance(df, pd.DataFrame)

    def test_get_northbound_flow_sz_market(self):
        """Test northbound flow for Shenzhen market."""
        df = northbound_get_northbound_flow(market="sz")
        assert isinstance(df, pd.DataFrame)

    def test_get_northbound_flow_with_date_range(self):
        """Test northbound flow with date range."""
        start_date, end_date = get_recent_30_days()
        df = northbound_get_northbound_flow(start_date=start_date, end_date=end_date, market="all")
        assert isinstance(df, pd.DataFrame)

    def test_get_northbound_holdings_basic(self):
        """Test northbound holdings retrieval."""
        df = northbound_get_northbound_holdings(symbol="600000")
        assert isinstance(df, pd.DataFrame)

    def test_get_northbound_holdings_with_date_range(self):
        """Test northbound holdings with date range."""
        start_date, end_date = get_recent_30_days()
        df = northbound_get_northbound_holdings(
            symbol="600000", start_date=start_date, end_date=end_date
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_northbound_top_stocks(self):
        """Test northbound top stocks ranking."""
        today = datetime.now().strftime("%Y-%m-%d")
        df = northbound_get_northbound_top_stocks(date=today)
        assert isinstance(df, pd.DataFrame)

    def test_get_northbound_top_stocks_custom_params(self):
        """Test northbound top stocks with custom parameters."""
        today = datetime.now().strftime("%Y-%m-%d")
        df = northbound_get_northbound_top_stocks(date=today, market="sh", top_n=50)
        assert isinstance(df, pd.DataFrame)


# ==================== Dragon Tiger (LHB) Tests ====================


class TestDragonTigerMCP:
    """Test dragon tiger list data retrieval."""

    def test_get_dragon_tiger_list_basic(self):
        """Test dragon tiger list retrieval."""
        # Use a date range that's likely to have data (last 30 days)
        date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        try:
            df = lhb_get_dragon_tiger_list(date=date)
            assert isinstance(df, pd.DataFrame)
        except RuntimeError as e:
            # If no data available for that date, skip test
            if "NoneType" in str(e) or "Failed" in str(e):
                pytest.skip(f"No dragon tiger data available for {date}")
            else:
                raise

    def test_get_dragon_tiger_list_with_symbol(self):
        """Test dragon tiger list for specific stock."""
        date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        try:
            df = lhb_get_dragon_tiger_list(date=date, symbol="600000")
            assert isinstance(df, pd.DataFrame)
        except RuntimeError as e:
            if "NoneType" in str(e) or "Failed" in str(e):
                pytest.skip(f"No dragon tiger data available for {date}")
            else:
                raise

    def test_get_dragon_tiger_list_with_symbol(self):
        """Test dragon tiger list for specific stock."""
        date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        try:
            df = lhb_get_dragon_tiger_list(date=date, symbol="600000")
            assert isinstance(df, pd.DataFrame)
        except RuntimeError as e:
            if "NoneType" in str(e) or "Failed" in str(e):
                pytest.skip(f"No dragon tiger data available for {date}")
            else:
                raise

    def test_get_dragon_tiger_summary_stock_group(self):
        """Test dragon tiger summary grouped by stock."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        df = lhb_get_dragon_tiger_summary(
            start_date=start_date, end_date=end_date, group_by="stock"
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_dragon_tiger_summary_broker_group(self):
        """Test dragon tiger summary grouped by broker."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        df = lhb_get_dragon_tiger_summary(
            start_date=start_date, end_date=end_date, group_by="broker"
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_dragon_tiger_summary_reason_group(self):
        """Test dragon tiger summary grouped by reason."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        df = lhb_get_dragon_tiger_summary(
            start_date=start_date, end_date=end_date, group_by="reason"
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_dragon_tiger_broker_stats(self):
        """Test dragon tiger broker statistics."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        df = lhb_get_dragon_tiger_broker_stats(start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)

    def test_get_dragon_tiger_broker_stats_custom_top_n(self):
        """Test dragon tiger broker statistics with custom top_n."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        df = lhb_get_dragon_tiger_broker_stats(start_date=start_date, end_date=end_date, top_n=20)
        assert isinstance(df, pd.DataFrame)


# ==================== Limit Up/Down Tests ====================


class TestLimitUpMCP:
    """Test limit up pool data retrieval."""

    def test_get_limit_up_pool(self):
        """Test limit up pool retrieval."""
        today = datetime.now().strftime("%Y-%m-%d")
        df = limitup_get_limit_up_pool(date=today)
        assert isinstance(df, pd.DataFrame)

    def test_get_limit_down_pool(self):
        """Test limit down pool retrieval."""
        today = datetime.now().strftime("%Y-%m-%d")
        df = limitup_get_limit_down_pool(date=today)
        assert isinstance(df, pd.DataFrame)

    def test_get_limit_up_stats(self):
        """Test limit up statistics."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        df = limitup_get_limit_up_stats(start_date=start_date, end_date=end_date)
        assert isinstance(df, pd.DataFrame)


# ==================== MCP Tool Wrapper Tests ====================


@pytest.mark.skipif(not MCP_AVAILABLE, reason="fastmcp not installed")
class TestMCPToolWrappers:
    """Test MCP tool wrappers."""

    def test_mcp_tools_have_required_attributes(self):
        """Test that MCP tools have required attributes."""
        mcp_tools = [
            mcp_get_stock_fund_flow,
            mcp_get_sector_fund_flow,
            mcp_get_main_fund_flow_rank,
            mcp_get_northbound_flow,
            mcp_get_northbound_holdings,
            mcp_get_northbound_top_stocks,
            mcp_get_dragon_tiger_list,
            mcp_get_dragon_tiger_summary,
            mcp_get_dragon_tiger_broker_stats,
            mcp_get_limit_up_pool,
            mcp_get_limit_down_pool,
            mcp_get_limit_up_stats,
        ]
        for tool in mcp_tools:
            assert hasattr(tool, "fn"), f"{tool.__name__} should have 'fn' attribute"
            assert callable(tool.fn), f"{tool.__name__}.fn should be callable"
            assert hasattr(tool, "name"), f"{tool.__name__} should have 'name' attribute"
            assert hasattr(tool, "description"), (
                f"{tool.__name__} should have 'description' attribute"
            )

    def test_mcp_tools_json_output(self):
        """Test that MCP tools return valid JSON."""
        today = datetime.now().strftime("%Y-%m-%d")
        start_date, end_date = get_recent_30_days()

        test_cases = [
            (mcp_get_stock_fund_flow, {"symbol": "600000"}),
            (mcp_get_sector_fund_flow, {"sector_type": "industry"}),
            (mcp_get_main_fund_flow_rank, {"date": today}),
            (mcp_get_northbound_flow, {}),
            (mcp_get_northbound_holdings, {"symbol": "600000"}),
            (mcp_get_northbound_top_stocks, {"date": today}),
            (mcp_get_dragon_tiger_list, {"date": today}),
            (mcp_get_dragon_tiger_summary, {"start_date": start_date, "end_date": end_date}),
            (mcp_get_dragon_tiger_broker_stats, {"start_date": start_date, "end_date": end_date}),
            (mcp_get_limit_up_pool, {"date": today}),
            (mcp_get_limit_down_pool, {"date": today}),
            (mcp_get_limit_up_stats, {"start_date": start_date, "end_date": end_date}),
        ]

        for tool, kwargs in test_cases:
            try:
                result = tool.fn(**kwargs) if hasattr(tool, "fn") else tool(**kwargs)
                assert isinstance(result, str), f"{tool.name} should return string"
                if result != "[]":
                    data = json.loads(result)
                    assert isinstance(data, list), f"{tool.name} should return list in JSON"
            except RuntimeError as e:
                # Skip if data source fails (e.g., dragon tiger data not available)
                if "Failed" in str(e) or "NoneType" in str(e):
                    pytest.skip(f"Skipping {tool.name} due to data source issue")
                else:
                    raise

    def test_mcp_wrapper_recent_n_parameter(self):
        """Test recent_n parameter works correctly in MCP wrapper."""
        df = fundflow_get_stock_fund_flow(symbol="600000")
        if not df.empty:
            result = (
                mcp_get_stock_fund_flow.fn(symbol="600000", recent_n=5)
                if hasattr(mcp_get_stock_fund_flow, "fn")
                else mcp_get_stock_fund_flow(symbol="600000", recent_n=5)
            )
            assert isinstance(result, str)
            try:
                data = json.loads(result)
                assert len(data) <= 5, f"Expected <= 5 records, got {len(data)}"
            except json.JSONDecodeError:
                pytest.fail("get_stock_fund_flow with recent_n returned invalid JSON")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
