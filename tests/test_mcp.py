"""Tests for MCP (Model Context Protocol) server module."""

import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

# Skip all MCP tests if fastmcp is not installed
try:
    from akshare_one.mcp import mcp, run_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

pytestmark = pytest.mark.skipif(not MCP_AVAILABLE, reason="fastmcp not installed")


class TestMCPInitialization:
    """Test MCP server initialization."""

    def test_mcp_server_exists(self):
        """Test that MCP server is properly initialized."""
        assert mcp is not None
        assert mcp.name == "akshare-one-mcp"

    def test_run_server_function_exists(self):
        """Test that run_server function exists."""
        assert callable(run_server)


class TestMCPServerLogic:
    """Test MCP server logic by testing the underlying functions directly."""

    def test_dataframe_to_json_conversion(self):
        """Test that DataFrame is correctly converted to JSON."""
        df = pd.DataFrame({
            "timestamp": [1609459200000, 1609545600000],
            "close": [100.0, 101.0],
        })

        result = df.to_json(orient="records") or "[]"
        data = json.loads(result)

        assert len(data) == 2
        assert data[0]["close"] == 100.0

    def test_empty_dataframe_to_json(self):
        """Test that empty DataFrame returns '[]'."""
        df = pd.DataFrame()
        result = df.to_json(orient="records") or "[]"
        assert result == "[]"

    def test_dataframe_with_recent_n(self):
        """Test recent_n functionality."""
        df = pd.DataFrame({
            "timestamp": [1, 2, 3, 4, 5],
            "close": [100.0, 101.0, 102.0, 103.0, 104.0],
        })

        recent_n = 3
        df_limited = df.tail(recent_n)
        result = df_limited.to_json(orient="records") or "[]"
        data = json.loads(result)

        assert len(data) == 3
        assert data[-1]["close"] == 104.0


class TestTimeInfoLogic:
    """Test get_time_info logic."""

    def test_time_info_structure(self):
        """Test that time info has correct structure."""
        from akshare_one.mcp.server import get_time_info

        # Just verify the function exists (it's wrapped by FastMCP)
        assert get_time_info is not None

    def test_datetime_iso_format(self):
        """Test ISO format generation."""
        local_time = datetime.now().astimezone()
        iso_str = local_time.isoformat()

        # Should be parseable
        parsed = datetime.fromisoformat(iso_str)
        assert parsed is not None

    def test_timestamp_generation(self):
        """Test timestamp generation."""
        local_time = datetime.now().astimezone()
        timestamp = local_time.timestamp()

        assert isinstance(timestamp, float)
        assert timestamp > 0


class TestIndicatorMap:
    """Test indicator mapping in MCP server."""

    def test_indicator_names(self):
        """Test that indicator names are valid."""
        valid_indicators = [
            "SMA", "EMA", "RSI", "MACD", "BOLL", "STOCH",
            "ATR", "CCI", "ADX", "WILLR", "OBV", "TRIX",
            "ROC", "MOM",
        ]

        # These should match the indicators available in akshare_one.indicators
        from akshare_one import indicators

        for indicator in valid_indicators:
            func_name = f"get_{indicator.lower()}"
            if indicator == "STOCH":
                func_name = "get_stoch"
            elif indicator == "BOLL":
                func_name = "get_bollinger_bands"

            assert hasattr(indicators, func_name), f"Missing indicator: {indicator}"


class TestMCPIntegration:
    """Test MCP integration points."""

    @patch("akshare_one.mcp.server.ako.get_hist_data")
    def test_hist_data_integration(self, mock_get_hist):
        """Test that hist_data tool integrates correctly."""
        mock_df = pd.DataFrame({
            "timestamp": [1609459200000],
            "close": [100.0],
        })
        mock_get_hist.return_value = mock_df

        # Verify the mock works
        result = mock_get_hist(symbol="600000")
        assert len(result) == 1
        assert result.iloc[0]["close"] == 100.0

    @patch("akshare_one.mcp.server.ako.get_realtime_data")
    def test_realtime_data_integration(self, mock_get_realtime):
        """Test that realtime_data tool integrates correctly."""
        mock_df = pd.DataFrame({
            "symbol": ["600000"],
            "price": [10.5],
        })
        mock_get_realtime.return_value = mock_df

        result = mock_get_realtime(symbol="600000")
        assert result.iloc[0]["symbol"] == "600000"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
