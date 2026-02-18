"""
Unit tests for market data exception classes.

Tests the exception hierarchy and error handling utilities.
"""

from unittest.mock import Mock

import pytest
import requests

from akshare_one.modules.exceptions import (
    DataSourceUnavailableError,
    DataValidationError,
    InvalidParameterError,
    MarketDataError,
    NoDataError,
    RateLimitError,
    UpstreamChangedError,
    handle_upstream_error,
)


class TestExceptionHierarchy:
    """Test the exception class hierarchy."""
    
    def test_market_data_error_is_base_exception(self):
        """Test that MarketDataError is the base exception."""
        error = MarketDataError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    def test_invalid_parameter_error_inherits_from_market_data_error(self):
        """Test InvalidParameterError inheritance."""
        error = InvalidParameterError("Invalid symbol")
        assert isinstance(error, MarketDataError)
        assert isinstance(error, Exception)
    
    def test_data_source_unavailable_error_inherits_from_market_data_error(self):
        """Test DataSourceUnavailableError inheritance."""
        error = DataSourceUnavailableError("Source down")
        assert isinstance(error, MarketDataError)
        assert isinstance(error, Exception)
    
    def test_no_data_error_inherits_from_market_data_error(self):
        """Test NoDataError inheritance."""
        error = NoDataError("No data available")
        assert isinstance(error, MarketDataError)
        assert isinstance(error, Exception)
    
    def test_upstream_changed_error_inherits_from_market_data_error(self):
        """Test UpstreamChangedError inheritance."""
        error = UpstreamChangedError("API changed")
        assert isinstance(error, MarketDataError)
        assert isinstance(error, Exception)
    
    def test_rate_limit_error_inherits_from_market_data_error(self):
        """Test RateLimitError inheritance."""
        error = RateLimitError("Rate limit exceeded")
        assert isinstance(error, MarketDataError)
        assert isinstance(error, Exception)
    
    def test_data_validation_error_inherits_from_market_data_error(self):
        """Test DataValidationError inheritance."""
        error = DataValidationError("Invalid data")
        assert isinstance(error, MarketDataError)
        assert isinstance(error, Exception)


class TestExceptionCatching:
    """Test that exceptions can be caught properly."""
    
    def test_catch_specific_exception(self):
        """Test catching a specific exception type."""
        with pytest.raises(InvalidParameterError) as exc_info:
            raise InvalidParameterError("Invalid symbol format")
        
        assert "Invalid symbol format" in str(exc_info.value)
    
    def test_catch_base_exception(self):
        """Test catching any MarketDataError."""
        with pytest.raises(MarketDataError):
            raise InvalidParameterError("Invalid parameter")
        
        with pytest.raises(MarketDataError):
            raise DataSourceUnavailableError("Source unavailable")
        
        with pytest.raises(MarketDataError):
            raise NoDataError("No data")
    
    def test_catch_multiple_exception_types(self):
        """Test catching multiple exception types."""
        def raise_error(error_type):
            if error_type == "invalid":
                raise InvalidParameterError("Invalid")
            elif error_type == "unavailable":
                raise DataSourceUnavailableError("Unavailable")
            else:
                raise NoDataError("No data")
        
        # All should be catchable as MarketDataError
        for error_type in ["invalid", "unavailable", "nodata"]:
            with pytest.raises(MarketDataError):
                raise_error(error_type)


class TestHandleUpstreamError:
    """Test the handle_upstream_error utility function."""
    
    def test_handle_timeout_error(self):
        """Test handling timeout errors."""
        timeout_error = requests.Timeout("Connection timeout")
        result = handle_upstream_error(timeout_error, "eastmoney")
        
        assert isinstance(result, DataSourceUnavailableError)
        assert "Timeout" in str(result)
        assert "eastmoney" in str(result)
    
    def test_handle_connection_error(self):
        """Test handling connection errors."""
        conn_error = requests.ConnectionError("Connection refused")
        result = handle_upstream_error(conn_error, "eastmoney")
        
        assert isinstance(result, DataSourceUnavailableError)
        assert "Connection error" in str(result)
        assert "eastmoney" in str(result)
    
    def test_handle_rate_limit_error(self):
        """Test handling rate limit errors (HTTP 429)."""
        # Create a mock response with 429 status
        response = Mock()
        response.status_code = 429
        http_error = requests.HTTPError("Too many requests")
        http_error.response = response
        
        result = handle_upstream_error(http_error, "eastmoney")
        
        assert isinstance(result, RateLimitError)
        assert "Rate limit" in str(result)
        assert "eastmoney" in str(result)
    
    def test_handle_client_error(self):
        """Test handling client errors (HTTP 4xx)."""
        # Create a mock response with 400 status
        response = Mock()
        response.status_code = 400
        http_error = requests.HTTPError("Bad request")
        http_error.response = response
        
        result = handle_upstream_error(http_error, "eastmoney")
        
        assert isinstance(result, InvalidParameterError)
        assert "Client error" in str(result)
        assert "eastmoney" in str(result)
    
    def test_handle_server_error(self):
        """Test handling server errors (HTTP 5xx)."""
        # Create a mock response with 500 status
        response = Mock()
        response.status_code = 500
        http_error = requests.HTTPError("Internal server error")
        http_error.response = response
        
        result = handle_upstream_error(http_error, "eastmoney")
        
        assert isinstance(result, DataSourceUnavailableError)
        assert "Server error" in str(result)
        assert "eastmoney" in str(result)
    
    def test_handle_key_error(self):
        """Test handling KeyError (missing fields)."""
        key_error = KeyError("missing_field")
        result = handle_upstream_error(key_error, "eastmoney")
        
        assert isinstance(result, UpstreamChangedError)
        assert "Unexpected data structure" in str(result)
        assert "eastmoney" in str(result)
    
    def test_handle_attribute_error(self):
        """Test handling AttributeError (changed structure)."""
        attr_error = AttributeError("'dict' object has no attribute 'data'")
        result = handle_upstream_error(attr_error, "eastmoney")
        
        assert isinstance(result, UpstreamChangedError)
        assert "Unexpected data structure" in str(result)
        assert "eastmoney" in str(result)
    
    def test_handle_generic_error(self):
        """Test handling generic errors."""
        generic_error = ValueError("Some unexpected error")
        result = handle_upstream_error(generic_error, "eastmoney")
        
        assert isinstance(result, MarketDataError)
        assert "Unexpected error" in str(result)
        assert "eastmoney" in str(result)


class TestExceptionUsageScenarios:
    """Test realistic usage scenarios for exceptions."""
    
    def test_invalid_symbol_scenario(self):
        """Test InvalidParameterError for invalid symbol."""
        def validate_symbol(symbol):
            import re
            if not re.match(r'^\d{6}$', symbol):
                raise InvalidParameterError(
                    f"Invalid symbol format: {symbol}. Expected 6-digit code."
                )
        
        # Valid symbol should not raise
        validate_symbol("600000")
        
        # Invalid symbols should raise
        with pytest.raises(InvalidParameterError) as exc_info:
            validate_symbol("60000")  # Too short
        assert "Invalid symbol format" in str(exc_info.value)
        
        with pytest.raises(InvalidParameterError):
            validate_symbol("ABC123")  # Not digits
    
    def test_date_range_validation_scenario(self):
        """Test InvalidParameterError for invalid date range."""
        from datetime import datetime
        
        def validate_date_range(start_date, end_date):
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start > end:
                raise InvalidParameterError(
                    f"start_date ({start_date}) must be <= end_date ({end_date})"
                )
        
        # Valid range should not raise
        validate_date_range("2024-01-01", "2024-12-31")
        
        # Invalid range should raise
        with pytest.raises(InvalidParameterError) as exc_info:
            validate_date_range("2024-12-31", "2024-01-01")
        assert "must be <=" in str(exc_info.value)
    
    def test_upstream_field_change_scenario(self):
        """Test UpstreamChangedError for missing fields."""
        def validate_response_structure(data):
            expected_fields = ['date', 'symbol', 'close']
            missing = set(expected_fields) - set(data.keys())
            
            if missing:
                raise UpstreamChangedError(
                    f"Missing expected fields: {missing}. Upstream API may have changed."
                )
        
        # Valid structure should not raise
        validate_response_structure({'date': '2024-01-01', 'symbol': '600000', 'close': 10.0})
        
        # Missing fields should raise
        with pytest.raises(UpstreamChangedError) as exc_info:
            validate_response_structure({'date': '2024-01-01', 'symbol': '600000'})
        assert "Missing expected fields" in str(exc_info.value)
        assert "close" in str(exc_info.value)
    
    def test_no_data_scenario(self):
        """Test NoDataError for explicit no data response."""
        def check_data_availability(response):
            if response.get('error') == 'NO_DATA':
                raise NoDataError(
                    "No data available for the requested period"
                )
        
        # Normal response should not raise
        check_data_availability({'data': []})
        
        # No data error should raise
        with pytest.raises(NoDataError) as exc_info:
            check_data_availability({'error': 'NO_DATA'})
        assert "No data available" in str(exc_info.value)
    
    def test_data_validation_scenario(self):
        """Test DataValidationError for invalid data values."""
        import pandas as pd
        
        def validate_price_data(df):
            if (df['close'] < 0).any():
                raise DataValidationError("Close price cannot be negative")
            
            if (df['volume'] < 0).any():
                raise DataValidationError("Volume cannot be negative")
        
        # Valid data should not raise
        valid_df = pd.DataFrame({
            'close': [10.0, 11.0, 12.0],
            'volume': [1000, 2000, 3000]
        })
        validate_price_data(valid_df)
        
        # Invalid close price should raise
        invalid_df = pd.DataFrame({
            'close': [10.0, -1.0, 12.0],
            'volume': [1000, 2000, 3000]
        })
        with pytest.raises(DataValidationError) as exc_info:
            validate_price_data(invalid_df)
        assert "Close price cannot be negative" in str(exc_info.value)


class TestExceptionMessages:
    """Test that exception messages are informative."""
    
    def test_exception_messages_contain_context(self):
        """Test that exceptions include helpful context."""
        # InvalidParameterError should include the invalid value
        error = InvalidParameterError("Invalid symbol: ABC")
        assert "ABC" in str(error)
        
        # DataSourceUnavailableError should include the source
        error = DataSourceUnavailableError("Failed to connect to eastmoney")
        assert "eastmoney" in str(error)
        
        # UpstreamChangedError should indicate what changed
        error = UpstreamChangedError("Missing field: close_price")
        assert "close_price" in str(error)
    
    def test_exception_can_be_raised_with_custom_message(self):
        """Test that all exceptions accept custom messages."""
        custom_message = "This is a custom error message"
        
        exceptions = [
            MarketDataError,
            InvalidParameterError,
            DataSourceUnavailableError,
            NoDataError,
            UpstreamChangedError,
            RateLimitError,
            DataValidationError,
        ]
        
        for exc_class in exceptions:
            error = exc_class(custom_message)
            assert str(error) == custom_message
