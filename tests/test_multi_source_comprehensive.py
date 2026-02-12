"""Comprehensive tests for multi-source functionality and failover mechanisms."""

import unittest.mock as mock
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from akshare_one import (
    get_basic_info_multi_source,
    get_financial_data_multi_source,
    get_financial_metrics_multi_source,
    get_hist_data_multi_source,
    get_news_data_multi_source,
)
from akshare_one.modules.multi_source import ExecutionResult, MultiSourceRouter


def test_multi_source_router_basic_functionality():
    """Test basic functionality of MultiSourceRouter."""
    # Create mock providers
    provider1 = Mock()
    provider1.get_hist_data.return_value = pd.DataFrame({
        "timestamp": ["2024-01-01"],
        "open": [100.0],
        "close": [100.5],
        "volume": [1000],
    })

    # Create router with providers
    router = MultiSourceRouter([
        ("provider1", provider1),
    ])

    result = router.execute("get_hist_data")
    assert not result.empty
    assert "open" in result.columns
    assert provider1.get_hist_data.called


def test_multi_source_router_failover():
    """Test failover mechanism when first provider fails."""
    # First provider fails
    provider1 = Mock()
    provider1.get_hist_data.side_effect = Exception("Rate limited")

    # Second provider succeeds
    provider2 = Mock()
    provider2.get_hist_data.return_value = pd.DataFrame({
        "timestamp": ["2024-01-01"],
        "open": [100.0],
        "close": [100.5],
        "volume": [1000],
    })

    router = MultiSourceRouter([
        ("provider1", provider1),
        ("provider2", provider2),
    ])

    result = router.execute("get_hist_data")
    assert not result.empty
    assert provider1.get_hist_data.called
    assert provider2.get_hist_data.called


def test_multi_source_router_execute_with_result():
    """Test execute_with_result for detailed execution information."""
    # First provider fails
    provider1 = Mock()
    provider1.get_hist_data.side_effect = Exception("Rate limited")

    # Second provider succeeds
    provider2 = Mock()
    provider2.get_hist_data.return_value = pd.DataFrame({
        "timestamp": ["2024-01-01"],
        "open": [100.0],
        "close": [100.5],
        "volume": [1000],
    })

    router = MultiSourceRouter([
        ("provider1", provider1),
        ("provider2", provider2),
    ])

    result = router.execute_with_result("get_hist_data")

    assert result.success is True
    assert result.source == "provider2"
    assert result.attempts == 2
    assert len(result.error_details) == 1  # One error from provider1


def test_multi_source_router_all_sources_fail():
    """Test when all sources fail."""
    # Both providers fail
    provider1 = Mock()
    provider1.get_hist_data.side_effect = Exception("Rate limited")

    provider2 = Mock()
    provider2.get_hist_data.side_effect = Exception("Service unavailable")

    router = MultiSourceRouter([
        ("provider1", provider1),
        ("provider2", provider2),
    ])

    result = router.execute_with_result("get_hist_data")

    assert result.success is False
    assert result.source is None
    assert result.attempts == 2
    assert len(result.error_details) == 2


def test_multi_source_router_validation():
    """Test result validation with required columns."""
    # Provider returns data without required columns
    provider1 = Mock()
    provider1.get_hist_data.return_value = pd.DataFrame({
        "timestamp": ["2024-01-01"],
        "open": [100.0],
        # Missing required 'volume' column
    })

    provider2 = Mock()
    provider2.get_hist_data.return_value = pd.DataFrame({
        "timestamp": ["2024-01-01"],
        "open": [100.0],
        "close": [100.5],
        "volume": [1000],
    })

    router = MultiSourceRouter(
        [
            ("provider1", provider1),
            ("provider2", provider2),
        ],
        required_columns=["timestamp", "open", "close", "volume"],
    )

    result = router.execute_with_result("get_hist_data")

    assert result.success is True
    assert result.source == "provider2"  # Should use provider2 as provider1 fails validation
    assert result.attempts == 2


def test_multi_source_router_stats():
    """Test execution statistics tracking."""
    provider1 = Mock()
    provider1.get_hist_data.side_effect = Exception("Rate limited")

    provider2 = Mock()
    provider2.get_hist_data.return_value = pd.DataFrame({
        "timestamp": ["2024-01-01"],
        "open": [100.0],
        "close": [100.5],
        "volume": [1000],
    })

    router = MultiSourceRouter([
        ("provider1", provider1),
        ("provider2", provider2),
    ])

    # Execute multiple times
    router.execute("get_hist_data")
    router.execute("get_hist_data")

    stats = router.get_stats()
    assert stats["provider1"]["failure"] == 2
    assert stats["provider2"]["success"] == 2


def test_get_hist_data_multi_source_integration():
    """Integration test for get_hist_data_multi_source with multiple sources."""
    with patch('akshare_one.modules.historical.factory.HistoricalDataFactory.get_provider') as mock_factory:
        # Mock providers to simulate different behaviors
        mock_provider1 = Mock()
        mock_provider1.get_hist_data.side_effect = Exception("Provider 1 failed")
        
        mock_provider2 = Mock()
        mock_provider2.get_hist_data.return_value = pd.DataFrame({
            "timestamp": ["2024-01-01"],
            "open": [100.0],
            "high": [101.0],
            "low": [99.0],
            "close": [100.5],
            "volume": [1000],
        })
        
        # Configure factory to return different mocks based on source name
        def get_mock_provider(source, **kwargs):
            if source == "eastmoney_direct":
                return mock_provider1
            elif source == "eastmoney":
                return mock_provider1
            elif source == "sina":
                return mock_provider2
            else:
                raise ValueError(f"Unknown provider: {source}")
        
        mock_factory.side_effect = get_mock_provider
        
        # Test multi-source call
        result = get_hist_data_multi_source(
            symbol="600000",
            sources=["eastmoney_direct", "eastmoney", "sina"]
        )
        
        # Verify result
        assert not result.empty
        assert "open" in result.columns
        assert "close" in result.columns
        # Verify that all providers were tried until one succeeded
        assert mock_provider1.get_hist_data.call_count == 2
        assert mock_provider2.get_hist_data.call_count == 1


def test_get_basic_info_multi_source_integration():
    """Integration test for get_basic_info_multi_source with multiple sources."""
    with patch('akshare_one.modules.info.factory.InfoDataFactory.get_provider') as mock_factory:
        # Mock providers to simulate different behaviors
        mock_provider1 = Mock()
        mock_provider1.get_basic_info.side_effect = Exception("Provider 1 failed")
        
        mock_provider2 = Mock()
        mock_provider2.get_basic_info.return_value = pd.DataFrame({
            "symbol": ["600000"],
            "name": ["PF Bank"],
            "price": [10.5],
        })
        
        # Configure factory to return different mocks based on source name
        def get_mock_provider(source, **kwargs):
            if source == "eastmoney":
                return mock_provider1
            elif source == "sina":
                return mock_provider2
            else:
                raise ValueError(f"Unknown provider: {source}")
        
        mock_factory.side_effect = get_mock_provider
        
        # Test multi-source call
        result = get_basic_info_multi_source(
            symbol="600000",
            sources=["eastmoney", "sina"]
        )
        
        # Verify result
        assert not result.empty
        assert "symbol" in result.columns
        assert "name" in result.columns
        # Verify that both providers were tried until one succeeded
        assert mock_provider1.get_basic_info.call_count == 1
        assert mock_provider2.get_basic_info.call_count == 1


def test_get_news_data_multi_source_integration():
    """Integration test for get_news_data_multi_source with multiple sources."""
    with patch('akshare_one.modules.news.factory.NewsDataFactory.get_provider') as mock_factory:
        # Mock providers to simulate different behaviors
        mock_provider1 = Mock()
        mock_provider1.get_news_data.side_effect = Exception("Provider 1 failed")
        
        mock_provider2 = Mock()
        mock_provider2.get_news_data.return_value = pd.DataFrame({
            "title": ["News Title"],
            "content": ["News Content"],
            "publish_time": ["2024-01-01"],
        })
        
        # Configure factory to return different mocks based on source name
        def get_mock_provider(source, **kwargs):
            if source == "eastmoney":
                return mock_provider1
            elif source == "sina":
                return mock_provider2
            else:
                raise ValueError(f"Unknown provider: {source}")
        
        mock_factory.side_effect = get_mock_provider
        
        # Test multi-source call
        result = get_news_data_multi_source(
            symbol="600000",
            sources=["eastmoney", "sina"]
        )
        
        # Verify result
        assert not result.empty
        assert "title" in result.columns
        # Verify that both providers were tried until one succeeded
        assert mock_provider1.get_news_data.call_count == 1
        assert mock_provider2.get_news_data.call_count == 1


def test_get_financial_data_multi_source_integration():
    """Integration test for get_financial_data_multi_source with multiple sources."""
    with patch('akshare_one.modules.financial.factory.FinancialDataFactory.get_provider') as mock_factory:
        # Mock providers to simulate different behaviors
        mock_provider1 = Mock()
        mock_provider1.get_balance_sheet.side_effect = Exception("Provider 1 failed")
        
        mock_provider2 = Mock()
        mock_provider2.get_balance_sheet.return_value = pd.DataFrame({
            "report_date": ["2023-12-31"],
            "total_assets": [1000000],
            "total_liabilities": [500000],
        })
        
        # Configure factory to return different mocks based on source name
        def get_mock_provider(source, **kwargs):
            if source == "eastmoney_direct":
                return mock_provider1
            elif source == "sina":
                return mock_provider2
            else:
                raise ValueError(f"Unknown provider: {source}")
        
        mock_factory.side_effect = get_mock_provider
        
        # Test multi-source call
        result = get_financial_data_multi_source(
            symbol="600000",
            data_type="balance_sheet",
            sources=["eastmoney_direct", "sina"]
        )
        
        # Verify result
        assert not result.empty
        assert "report_date" in result.columns
        # Verify that both providers were tried until one succeeded
        assert mock_provider1.get_balance_sheet.call_count == 1
        assert mock_provider2.get_balance_sheet.call_count == 1


def test_execution_result_properties():
    """Test ExecutionResult properties and methods."""
    # Successful result
    success_result = ExecutionResult(
        success=True,
        data=pd.DataFrame({"col1": [1, 2, 3]}),
        source="provider1",
        error=None,
        attempts=1
    )
    
    assert success_result.success is True
    assert success_result.source == "provider1"
    assert success_result.attempts == 1
    assert success_result.error is None
    
    # Failed result
    failed_result = ExecutionResult(
        success=False,
        data=None,
        source=None,
        error="All providers failed",
        attempts=3,
        error_details=[("provider1", "timeout"), ("provider2", "rate limit")]
    )
    
    assert failed_result.success is False
    assert failed_result.source is None
    assert failed_result.attempts == 3
    assert failed_result.error == "All providers failed"
    assert len(failed_result.error_details) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])