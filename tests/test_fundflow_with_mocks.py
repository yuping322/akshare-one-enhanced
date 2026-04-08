"""
Test fund flow module using mock fixtures - no network required.

This demonstrates offline testing for fund flow data.
"""

import pandas as pd
import pytest

from akshare_one.modules.fundflow import get_stock_fund_flow


class TestFundFlowWithMocks:
    """Test fund flow data with mocked API responses."""

    def test_get_stock_fund_flow_mocked(self, mock_stock_fund_flow_api):
        """
        Test getting stock fund flow data using mock data.
        """
        df = get_stock_fund_flow(symbol="600000", start_date="2024-01-15", end_date="2024-01-17")

        # Verify structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "date" in df.columns
        assert "symbol" in df.columns

        # Verify data types
        assert (
            df["date"].dtype == "object"
            or str(df["date"].dtype) in ("str", "string")
            or str(df["date"].dtype).startswith("StringDtype")
        )

    def test_fund_flow_json_serializable_mocked(self, mock_stock_fund_flow_api):
        """
        Test that fund flow data can be serialized to JSON.
        """
        df = get_stock_fund_flow(symbol="600000", start_date="2024-01-15", end_date="2024-01-17")

        # Should not raise
        json_str = df.to_json(orient="records")
        assert json_str is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
