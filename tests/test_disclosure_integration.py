"""
Integration tests for disclosure news data.

Tests the actual data fetching and standardization from Eastmoney.
"""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.akshare_one.modules.disclosure import (
    get_disclosure_news,
    get_dividend_data,
    get_repurchase_data,
    get_st_delist_data,
)


class TestDisclosureNewsIntegration:
    """Integration tests for disclosure news data."""
    
    def test_get_disclosure_news_all_categories(self):
        """Test fetching disclosure news for all categories."""
        # Use a recent date range (1 day)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = end_date  # Same day to limit data
        
        df = get_disclosure_news(
            symbol=None,
            start_date=start_date,
            end_date=end_date,
            category='all'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = ['date', 'symbol', 'title', 'category', 'content', 'url']
        assert list(df.columns) == expected_columns
        
        # If data exists, check data types
        if not df.empty:
            # Check that date, symbol, title, category, url are string types
            assert pd.api.types.is_string_dtype(df['date'])
            assert pd.api.types.is_string_dtype(df['symbol'])
            assert pd.api.types.is_string_dtype(df['title'])
            assert pd.api.types.is_string_dtype(df['category'])
            assert pd.api.types.is_string_dtype(df['url'])
            
            # Check symbol format (6 digits)
            assert all(len(s) == 6 for s in df['symbol'])
            assert all(s.isdigit() for s in df['symbol'])
            
            # Check date format (YYYY-MM-DD)
            for date_str in df['date']:
                datetime.strptime(date_str, '%Y-%m-%d')
    
    def test_get_disclosure_news_specific_symbol(self):
        """Test fetching disclosure news for a specific stock."""
        # Use a major stock that likely has announcements
        symbol = '600000'  # 浦发银行
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        df = get_disclosure_news(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            category='all'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = ['date', 'symbol', 'title', 'category', 'content', 'url']
        assert list(df.columns) == expected_columns
        
        # If data exists, all symbols should match
        if not df.empty:
            assert all(df['symbol'] == symbol)
    
    def test_get_disclosure_news_dividend_category(self):
        """Test fetching disclosure news filtered by dividend category."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = get_disclosure_news(
            symbol=None,
            start_date=start_date,
            end_date=end_date,
            category='dividend'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = ['date', 'symbol', 'title', 'category', 'content', 'url']
        assert list(df.columns) == expected_columns
        
        # If data exists, check that titles contain dividend-related keywords
        if not df.empty:
            dividend_keywords = ['分红', '派息', '红利', '股息', '现金分红']
            for title in df['title']:
                assert any(keyword in title for keyword in dividend_keywords)
    
    def test_get_disclosure_news_repurchase_category(self):
        """Test fetching disclosure news filtered by repurchase category."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = get_disclosure_news(
            symbol=None,
            start_date=start_date,
            end_date=end_date,
            category='repurchase'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = ['date', 'symbol', 'title', 'category', 'content', 'url']
        assert list(df.columns) == expected_columns
        
        # If data exists, check that titles contain repurchase-related keywords
        if not df.empty:
            repurchase_keywords = ['回购', '股份回购', '回购股份']
            for title in df['title']:
                assert any(keyword in title for keyword in repurchase_keywords)
    
    def test_get_disclosure_news_st_category(self):
        """Test fetching disclosure news filtered by ST category."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = get_disclosure_news(
            symbol=None,
            start_date=start_date,
            end_date=end_date,
            category='st'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = ['date', 'symbol', 'title', 'category', 'content', 'url']
        assert list(df.columns) == expected_columns
        
        # If data exists, check that titles contain ST-related keywords
        if not df.empty:
            st_keywords = ['ST', '*ST', 'SST', '退市', '风险警示', '风险提示']
            for title in df['title']:
                assert any(keyword in title for keyword in st_keywords)
    
    def test_get_disclosure_news_major_event_category(self):
        """Test fetching disclosure news filtered by major event category."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        df = get_disclosure_news(
            symbol=None,
            start_date=start_date,
            end_date=end_date,
            category='major_event'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = ['date', 'symbol', 'title', 'category', 'content', 'url']
        assert list(df.columns) == expected_columns
        
        # If data exists, check that titles or categories contain major event-related keywords
        # Note: This test may return empty results if no major events in the date range
        if not df.empty:
            major_keywords = ['重大事项', '重大合同', '重大资产', '重组', '收购', '兼并']
            # At least some results should contain the keywords
            has_keyword = any(
                any(keyword in title or keyword in category 
                    for keyword in major_keywords)
                for title, category in zip(df['title'], df['category'], strict=False)
            )
            # If we got results, they should be relevant (but may be empty if no events)
            if len(df) > 0:
                assert has_keyword or len(df) == 0, "Results should contain major event keywords or be empty"
    
    def test_get_disclosure_news_invalid_symbol(self):
        """Test that invalid symbol raises ValueError."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            get_disclosure_news(
                symbol='invalid',
                start_date='2024-01-01',
                end_date='2024-01-31',
                category='all'
            )
    
    def test_get_disclosure_news_invalid_date_range(self):
        """Test that invalid date range raises ValueError."""
        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            get_disclosure_news(
                symbol=None,
                start_date='2024-12-31',
                end_date='2024-01-01',
                category='all'
            )
    
    def test_get_disclosure_news_invalid_category(self):
        """Test that invalid category raises ValueError."""
        with pytest.raises(ValueError, match="Invalid category"):
            get_disclosure_news(
                symbol=None,
                start_date='2024-01-01',
                end_date='2024-01-31',
                category='invalid'
            )
    
    def test_get_disclosure_news_json_compatibility(self):
        """Test that returned data is JSON compatible."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = end_date
        
        df = get_disclosure_news(
            symbol=None,
            start_date=start_date,
            end_date=end_date,
            category='all'
        )
        
        # Test JSON serialization
        json_str = df.to_json(orient='records')
        assert json_str is not None
        
        # Check no NaN values
        assert not df.isnull().any().any()
    
    def test_get_disclosure_news_empty_result(self):
        """Test handling of empty results."""
        # Use a date far in the future
        start_date = '2099-01-01'
        end_date = '2099-01-01'
        
        df = get_disclosure_news(
            symbol=None,
            start_date=start_date,
            end_date=end_date,
            category='all'
        )
        
        # Should return empty DataFrame with correct structure
        assert isinstance(df, pd.DataFrame)
        assert df.empty
        expected_columns = ['date', 'symbol', 'title', 'category', 'content', 'url']
        assert list(df.columns) == expected_columns


class TestDisclosureDividendIntegration:
    """Integration tests for dividend data."""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real API call - run with pytest -m integration")
    def test_get_dividend_data_real_api(self):
        """Test fetching real dividend data from API."""
        # Use a major stock that likely has dividend history
        symbol = '600000'  # 浦发银行
        
        df = get_dividend_data(
            symbol=symbol,
            start_date='2020-01-01',
            end_date='2024-12-31'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = [
            'symbol', 'fiscal_year', 'dividend_per_share',
            'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio'
        ]
        assert list(df.columns) == expected_columns
        
        # If data exists, validate content
        if not df.empty:
            # All symbols should match
            assert all(df['symbol'] == symbol)
            
            # Check data types
            assert pd.api.types.is_string_dtype(df['symbol'])
            assert pd.api.types.is_string_dtype(df['fiscal_year'])
            assert pd.api.types.is_string_dtype(df['record_date'])
            assert pd.api.types.is_string_dtype(df['ex_dividend_date'])
            assert pd.api.types.is_string_dtype(df['payment_date'])
            
            # Check date formats
            for date_col in ['record_date', 'ex_dividend_date', 'payment_date']:
                for date_str in df[date_col].dropna():
                    if date_str:  # Skip empty strings
                        datetime.strptime(date_str, '%Y-%m-%d')
            
            # Check dividend_per_share is numeric or None
            assert df['dividend_per_share'].dtype in [float, 'float64', 'object']
            
            # Test JSON compatibility
            json_str = df.to_json(orient='records')
            assert json_str is not None
    
    def test_get_dividend_data_structure(self):
        """Test that get_dividend_data returns correct structure."""
        df = get_dividend_data(
            symbol='600000',
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = [
            'symbol', 'fiscal_year', 'dividend_per_share',
            'record_date', 'ex_dividend_date', 'payment_date', 'dividend_ratio'
        ]
        assert list(df.columns) == expected_columns
    
    def test_get_dividend_data_invalid_symbol(self):
        """Test that invalid symbol raises ValueError."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            get_dividend_data(
                symbol='invalid',
                start_date='2024-01-01',
                end_date='2024-12-31'
            )
    
    def test_get_dividend_data_invalid_date_range(self):
        """Test that invalid date range raises ValueError."""
        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            get_dividend_data(
                symbol='600000',
                start_date='2024-12-31',
                end_date='2024-01-01'
            )


class TestDisclosureRepurchaseIntegration:
    """Integration tests for repurchase data."""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real API call - run with pytest -m integration")
    def test_get_repurchase_data_real_api(self):
        """Test fetching real repurchase data from API."""
        # Get all repurchase data for recent period
        df = get_repurchase_data(
            symbol=None,
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = [
            'symbol', 'announcement_date', 'progress',
            'amount', 'quantity', 'price_range'
        ]
        assert list(df.columns) == expected_columns
        
        # If data exists, validate content
        if not df.empty:
            # Check data types
            assert pd.api.types.is_string_dtype(df['symbol'])
            assert pd.api.types.is_string_dtype(df['announcement_date'])
            assert pd.api.types.is_string_dtype(df['progress'])
            assert pd.api.types.is_string_dtype(df['price_range'])
            
            # Check symbol format (6 digits)
            assert all(len(s) == 6 for s in df['symbol'])
            assert all(s.isdigit() for s in df['symbol'])
            
            # Check date format
            for date_str in df['announcement_date'].dropna():
                if date_str:
                    datetime.strptime(date_str, '%Y-%m-%d')
            
            # Test JSON compatibility
            json_str = df.to_json(orient='records')
            assert json_str is not None
    
    def test_get_repurchase_data_structure(self):
        """Test that get_repurchase_data returns correct structure."""
        df = get_repurchase_data(
            symbol='600000',
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = [
            'symbol', 'announcement_date', 'progress',
            'amount', 'quantity', 'price_range'
        ]
        assert list(df.columns) == expected_columns
    
    def test_get_repurchase_data_invalid_symbol(self):
        """Test that invalid symbol raises ValueError."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            get_repurchase_data(
                symbol='invalid',
                start_date='2024-01-01',
                end_date='2024-12-31'
            )
    
    def test_get_repurchase_data_invalid_date_range(self):
        """Test that invalid date range raises ValueError."""
        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            get_repurchase_data(
                symbol='600000',
                start_date='2024-12-31',
                end_date='2024-01-01'
            )


class TestDisclosureSTDelistIntegration:
    """Integration tests for ST/delist data."""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires real API call - run with pytest -m integration")
    def test_get_st_delist_data_real_api(self):
        """Test fetching real ST/delist data from API."""
        # Get all ST/delist data
        df = get_st_delist_data(symbol=None)
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = [
            'symbol', 'name', 'st_type', 'risk_level', 'announcement_date'
        ]
        assert list(df.columns) == expected_columns
        
        # Should have some data (there are always delisted stocks)
        assert not df.empty
        
        # Check data types
        assert pd.api.types.is_string_dtype(df['symbol'])
        assert pd.api.types.is_string_dtype(df['name'])
        assert pd.api.types.is_string_dtype(df['st_type'])
        assert pd.api.types.is_string_dtype(df['risk_level'])
        assert pd.api.types.is_string_dtype(df['announcement_date'])
        
        # Check symbol format (6 digits)
        assert all(len(s) == 6 for s in df['symbol'])
        assert all(s.isdigit() for s in df['symbol'])
        
        # Check ST type values
        valid_st_types = {'ST', '*ST', 'SST', 'S*ST', 'normal'}
        assert set(df['st_type'].unique()).issubset(valid_st_types)
        
        # Check risk level values
        valid_risk_levels = {'low', 'medium', 'high', 'critical'}
        assert set(df['risk_level'].unique()).issubset(valid_risk_levels)
        
        # Check date format
        for date_str in df['announcement_date'].dropna():
            if date_str:
                datetime.strptime(date_str, '%Y-%m-%d')
        
        # Test JSON compatibility
        json_str = df.to_json(orient='records')
        assert json_str is not None
    
    def test_get_st_delist_data_structure(self):
        """Test that get_st_delist_data returns correct structure."""
        df = get_st_delist_data(symbol='600000')
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        expected_columns = [
            'symbol', 'name', 'st_type', 'risk_level', 'announcement_date'
        ]
        assert list(df.columns) == expected_columns
    
    def test_get_st_delist_data_invalid_symbol(self):
        """Test that invalid symbol raises ValueError."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            get_st_delist_data(symbol='invalid')
