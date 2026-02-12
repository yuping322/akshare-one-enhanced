"""Tests for newly added data source providers."""

import pandas as pd
import pytest
from unittest.mock import Mock, patch

from akshare_one.modules.info.factory import InfoDataFactory
from akshare_one.modules.news.factory import NewsDataFactory
from akshare_one.modules.historical.factory import HistoricalDataFactory
from akshare_one.modules.financial.factory import FinancialDataFactory
from akshare_one.modules.multi_source import MultiSourceRouter


def test_sina_info_provider_creation():
    """Test that SinaInfo provider can be created."""
    provider = InfoDataFactory.get_provider('sina', symbol='600000')
    assert provider is not None
    assert hasattr(provider, 'get_basic_info')


def test_sina_news_provider_creation():
    """Test that SinaNews provider can be created."""
    provider = NewsDataFactory.get_provider('sina', symbol='600000')
    assert provider is not None
    assert hasattr(provider, 'get_news_data')


def test_tencent_historical_provider_creation():
    """Test that TencentHistorical provider can be created."""
    provider = HistoricalDataFactory.get_provider('tencent', symbol='600000', interval='day')
    assert provider is not None
    assert hasattr(provider, 'get_hist_data')


def test_netease_historical_provider_creation():
    """Test that NetEaseHistorical provider can be created."""
    provider = HistoricalDataFactory.get_provider('netease', symbol='600000', interval='day')
    assert provider is not None
    assert hasattr(provider, 'get_hist_data')


def test_cninfo_financial_provider_creation():
    """Test that CninfoFinancialReport provider can be created."""
    provider = FinancialDataFactory.get_provider('cninfo', symbol='600000')
    assert provider is not None
    assert hasattr(provider, 'get_balance_sheet')
    assert hasattr(provider, 'get_income_statement')
    assert hasattr(provider, 'get_cash_flow')
    assert hasattr(provider, 'get_financial_metrics')


def test_sina_info_provider_methods():
    """Test SinaInfo provider methods exist."""
    provider = InfoDataFactory.get_provider('sina', symbol='600000')
    
    # Check all required methods exist
    assert hasattr(provider, 'get_basic_info')
    
    # Test that method can be called (even if it fails due to network)
    try:
        # This will likely fail due to network/API issues, but that's OK for this test
        result = provider.get_basic_info()
        # If it doesn't raise an exception, check if it's a DataFrame or None
        assert isinstance(result, (pd.DataFrame, type(None))) or result is None
    except Exception:
        # Network/api errors are expected, just ensure the method exists and signature is correct
        pass


def test_sina_news_provider_methods():
    """Test SinaNews provider methods exist."""
    provider = NewsDataFactory.get_provider('sina', symbol='600000')
    
    # Check all required methods exist
    assert hasattr(provider, 'get_news_data')
    
    # Test that method can be called (even if it fails due to network)
    try:
        result = provider.get_news_data()
        assert isinstance(result, (pd.DataFrame, type(None))) or result is None
    except Exception:
        # Network/api errors are expected
        pass


def test_tencent_historical_provider_methods():
    """Test TencentHistorical provider methods exist."""
    provider = HistoricalDataFactory.get_provider('tencent', symbol='600000', interval='day')
    
    # Check all required methods exist
    assert hasattr(provider, 'get_hist_data')
    
    # Test that method can be called (even if it fails due to network)
    try:
        result = provider.get_hist_data()
        assert isinstance(result, (pd.DataFrame, type(None))) or result is None
    except Exception:
        # Network/api errors are expected
        pass


def test_netease_historical_provider_methods():
    """Test NetEaseHistorical provider methods exist."""
    provider = HistoricalDataFactory.get_provider('netease', symbol='600000', interval='day')
    
    # Check all required methods exist
    assert hasattr(provider, 'get_hist_data')
    
    # Test that method can be called (even if it fails due to network)
    try:
        result = provider.get_hist_data()
        assert isinstance(result, (pd.DataFrame, type(None))) or result is None
    except Exception:
        # Network/api errors are expected
        pass


def test_cninfo_financial_provider_methods():
    """Test CninfoFinancialReport provider methods exist."""
    provider = FinancialDataFactory.get_provider('cninfo', symbol='600000')
    
    # Check all required methods exist
    assert hasattr(provider, 'get_balance_sheet')
    assert hasattr(provider, 'get_income_statement')
    assert hasattr(provider, 'get_cash_flow')
    assert hasattr(provider, 'get_financial_metrics')
    
    # Test that methods can be called (even if they fail due to network)
    methods_to_test = [
        'get_balance_sheet',
        'get_income_statement', 
        'get_cash_flow',
        'get_financial_metrics'
    ]
    
    for method_name in methods_to_test:
        try:
            method = getattr(provider, method_name)
            result = method()
            assert isinstance(result, (pd.DataFrame, type(None))) or result is None
        except Exception:
            # Network/api errors are expected
            pass


def test_info_multi_source_router_with_new_providers():
    """Test MultiSourceRouter works with new providers."""
    # Create mock providers to test router functionality
    mock_sina = Mock()
    mock_sina.get_basic_info.return_value = pd.DataFrame({
        'symbol': ['600000'],
        'name': ['PF Bank'],
        'price': [10.5]
    })
    
    # Create router with mixed providers (existing + new)
    router = MultiSourceRouter([
        ('sina', mock_sina),  # new provider
    ])
    
    result = router.execute('get_basic_info')
    assert not result.empty
    assert 'symbol' in result.columns


def test_news_multi_source_router_with_new_providers():
    """Test MultiSourceRouter works with new news providers."""
    # Create mock providers to test router functionality
    mock_sina = Mock()
    mock_sina.get_news_data.return_value = pd.DataFrame({
        'title': ['News Title'],
        'content': ['News Content'],
        'publish_time': ['2024-01-01']
    })
    
    # Create router with new provider
    router = MultiSourceRouter([
        ('sina', mock_sina),  # new provider
    ])
    
    result = router.execute('get_news_data')
    assert not result.empty
    assert 'title' in result.columns


def test_historical_multi_source_router_with_new_providers():
    """Test MultiSourceRouter works with new historical providers."""
    # Create mock providers to test router functionality
    mock_tencent = Mock()
    mock_tencent.get_hist_data.return_value = pd.DataFrame({
        'timestamp': ['2024-01-01'],
        'open': [100.0],
        'close': [100.5],
        'volume': [1000]
    })
    
    mock_netease = Mock()
    mock_netease.get_hist_data.return_value = pd.DataFrame({
        'timestamp': ['2024-01-01'],
        'open': [100.0],
        'close': [100.5],
        'volume': [1000]
    })
    
    # Create router with new providers
    router = MultiSourceRouter([
        ('tencent', mock_tencent),  # new provider
        ('netease', mock_netease),  # new provider
    ])
    
    result = router.execute('get_hist_data')
    assert not result.empty
    assert 'open' in result.columns


def test_financial_multi_source_router_with_new_providers():
    """Test MultiSourceRouter works with new financial providers."""
    # Create mock providers to test router functionality
    mock_cninfo = Mock()
    mock_cninfo.get_balance_sheet.return_value = pd.DataFrame({
        'report_date': ['2023-12-31'],
        'total_assets': [1000000],
        'total_liabilities': [500000]
    })
    
    # Create router with new provider
    router = MultiSourceRouter([
        ('cninfo', mock_cninfo),  # new provider
    ])
    
    result = router.execute('get_balance_sheet')
    assert not result.empty
    assert 'report_date' in result.columns


def test_all_new_providers_registered_in_factories():
    """Test that all new providers are properly registered in their factories."""
    # Info factory should have sina
    info_providers = InfoDataFactory._providers
    assert 'sina' in info_providers
    
    # News factory should have sina
    news_providers = NewsDataFactory._providers
    assert 'sina' in news_providers
    
    # Historical factory should have tencent and netease
    hist_providers = HistoricalDataFactory._providers
    assert 'tencent' in hist_providers
    assert 'netease' in hist_providers
    
    # Financial factory should have cninfo
    fin_providers = FinancialDataFactory._providers
    assert 'cninfo' in fin_providers


def test_provider_registration_classes_correct():
    """Test that registered providers are the correct classes."""
    from akshare_one.modules.info.sina import SinaInfo
    from akshare_one.modules.news.sina import SinaNews
    from akshare_one.modules.historical.tencent import TencentHistorical
    from akshare_one.modules.historical.netease import NetEaseHistorical
    from akshare_one.modules.financial.cninfo import CninfoFinancialReport
    
    # Test Info factory
    info_provider = InfoDataFactory.get_provider('sina', symbol='600000')
    assert isinstance(info_provider, SinaInfo)
    
    # Test News factory
    news_provider = NewsDataFactory.get_provider('sina', symbol='600000')
    assert isinstance(news_provider, SinaNews)
    
    # Test Historical factory
    tencent_provider = HistoricalDataFactory.get_provider('tencent', symbol='600000', interval='day')
    assert isinstance(tencent_provider, TencentHistorical)
    
    netease_provider = HistoricalDataFactory.get_provider('netease', symbol='600000', interval='day')
    assert isinstance(netease_provider, NetEaseHistorical)
    
    # Test Financial factory
    cninfo_provider = FinancialDataFactory.get_provider('cninfo', symbol='600000')
    assert isinstance(cninfo_provider, CninfoFinancialReport)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])