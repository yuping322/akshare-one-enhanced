"""
Integration tests for FundFlow module - Task 2.11.

This test suite focuses on:
1. Testing complete workflows (end-to-end)
2. Testing real data fetching with actual API calls
3. Validating data quality and consistency across multiple API calls

These tests are marked with @pytest.mark.integration and require network access.
Run with: pytest tests/test_fundflow_integration.py --run-integration
"""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from akshare_one.modules.fundflow import (
    get_concept_constituents,
    get_concept_list,
    get_industry_constituents,
    get_industry_list,
    get_main_fund_flow_rank,
    get_sector_fund_flow,
    get_stock_fund_flow,
)
from tests.utils.integration_helpers import (
    DataFrameValidator,
    integration_rate_limiter,
    skip_if_no_network,
)

# ============================================================================
# Integration Tests - Complete Flow Testing
# ============================================================================

class TestCompleteFlowIndustry:
    """Test complete workflow for industry sector analysis."""
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_complete_industry_flow(self):
        """
        Test complete flow: Industry list -> Constituents -> Fund flow data.
        
        This test validates:
        1. Can fetch industry list
        2. Can fetch constituents for an industry
        3. Can fetch fund flow for constituent stocks
        4. Data consistency across all steps
        """
        validator = DataFrameValidator()
        
        # Step 1: Get industry list
        integration_rate_limiter.wait()
        industries = get_industry_list()
        
        assert not industries.empty, "Industry list should not be empty"
        validator.validate_required_columns(
            industries,
            ['sector_code', 'sector_name', 'constituent_count']
        )
        validator.validate_json_compatible(industries)
        
        # Verify we have multiple industries
        assert len(industries) >= 10, "Should have at least 10 industries"
        
        # Step 2: Get constituents for first industry
        industry_code = industries['sector_code'].iloc[0]
        industry_name = industries['sector_name'].iloc[0]
        
        integration_rate_limiter.wait()
        constituents = get_industry_constituents(industry_code)
        
        assert not constituents.empty, f"Constituents for {industry_name} should not be empty"
        validator.validate_required_columns(constituents, ['symbol', 'name'])
        validator.validate_json_compatible(constituents)
        
        # Verify symbol format
        for symbol in constituents['symbol']:
            assert len(symbol) == 6, f"Symbol {symbol} should be 6 digits"
            assert symbol.isdigit(), f"Symbol {symbol} should be numeric"
        
        # Step 3: Get fund flow for first 3 constituents
        date_end = datetime.now().strftime('%Y-%m-%d')
        date_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        fund_flow_results = []
        for symbol in constituents['symbol'].head(3):
            integration_rate_limiter.wait()
            fund_flow = get_stock_fund_flow(symbol, start_date=date_start, end_date=date_end)
            
            # Validate fund flow data
            validator.validate_json_compatible(fund_flow)
            
            if not fund_flow.empty:
                validator.validate_required_columns(
                    fund_flow,
                    ['date', 'symbol', 'close_price', 'fundflow_main_net_inflow']
                )
                
                # Verify symbol matches
                assert all(fund_flow['symbol'] == symbol), \
                    f"All rows should have symbol {symbol}"
                
                # Verify date range
                validator.validate_date_range(fund_flow, 'date', date_start, date_end)
                
                fund_flow_results.append(fund_flow)
        
        # Verify we got data for at least one stock
        assert len(fund_flow_results) > 0, "Should get fund flow data for at least one stock"
        
        print("\n✓ Complete industry flow test passed:")
        print(f"  - Industries: {len(industries)}")
        print(f"  - Constituents in {industry_name}: {len(constituents)}")
        print(f"  - Fund flow data fetched for {len(fund_flow_results)} stocks")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_industry_sector_fund_flow(self):
        """
        Test industry sector fund flow data fetching.
        
        This test validates:
        1. Can fetch sector-level fund flow for industries
        2. Data contains expected fields
        3. Data is JSON compatible
        """
        validator = DataFrameValidator()
        
        # Get today's date
        datetime.now().strftime('%Y-%m-%d')
        
        integration_rate_limiter.wait()
        sector_flow = get_sector_fund_flow('industry')
        
        assert not sector_flow.empty, "Industry sector fund flow should not be empty"
        
        validator.validate_required_columns(
            sector_flow,
            ['date', 'sector_code', 'sector_name', 'sector_type', 'main_net_inflow']
        )
        validator.validate_json_compatible(sector_flow)
        
        # Verify sector_type is 'industry'
        assert all(sector_flow['sector_type'] == 'industry'), \
            "All rows should have sector_type='industry'"
        
        # Verify we have multiple sectors
        assert len(sector_flow) >= 10, "Should have at least 10 industry sectors"
        
        print("\n✓ Industry sector fund flow test passed:")
        print(f"  - Sectors: {len(sector_flow)}")
        print(f"  - Date: {sector_flow['date'].iloc[0] if not sector_flow.empty else 'N/A'}")


class TestCompleteFlowConcept:
    """Test complete workflow for concept sector analysis."""
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_complete_concept_flow(self):
        """
        Test complete flow: Concept list -> Constituents -> Fund flow data.
        
        This test validates:
        1. Can fetch concept list
        2. Can fetch constituents for a concept
        3. Can fetch fund flow for constituent stocks
        4. Data consistency across all steps
        """
        validator = DataFrameValidator()
        
        # Step 1: Get concept list
        integration_rate_limiter.wait()
        concepts = get_concept_list()
        
        assert not concepts.empty, "Concept list should not be empty"
        validator.validate_required_columns(
            concepts,
            ['sector_code', 'sector_name', 'constituent_count']
        )
        validator.validate_json_compatible(concepts)
        
        # Verify we have multiple concepts
        assert len(concepts) >= 10, "Should have at least 10 concepts"
        
        # Step 2: Get constituents for first concept
        concept_code = concepts['sector_code'].iloc[0]
        concept_name = concepts['sector_name'].iloc[0]
        
        integration_rate_limiter.wait()
        constituents = get_concept_constituents(concept_code)
        
        assert not constituents.empty, f"Constituents for {concept_name} should not be empty"
        validator.validate_required_columns(constituents, ['symbol', 'name'])
        validator.validate_json_compatible(constituents)
        
        # Verify symbol format
        for symbol in constituents['symbol']:
            assert len(symbol) == 6, f"Symbol {symbol} should be 6 digits"
            assert symbol.isdigit(), f"Symbol {symbol} should be numeric"
        
        # Step 3: Get fund flow for first 2 constituents
        date_end = datetime.now().strftime('%Y-%m-%d')
        date_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        fund_flow_results = []
        for symbol in constituents['symbol'].head(2):
            integration_rate_limiter.wait()
            fund_flow = get_stock_fund_flow(symbol, start_date=date_start, end_date=date_end)
            
            # Validate fund flow data
            validator.validate_json_compatible(fund_flow)
            
            if not fund_flow.empty:
                validator.validate_required_columns(
                    fund_flow,
                    ['date', 'symbol', 'close_price', 'fundflow_main_net_inflow']
                )
                
                # Verify symbol matches
                assert all(fund_flow['symbol'] == symbol), \
                    f"All rows should have symbol {symbol}"
                
                fund_flow_results.append(fund_flow)
        
        # Verify we got data for at least one stock
        assert len(fund_flow_results) > 0, "Should get fund flow data for at least one stock"
        
        print("\n✓ Complete concept flow test passed:")
        print(f"  - Concepts: {len(concepts)}")
        print(f"  - Constituents in {concept_name}: {len(constituents)}")
        print(f"  - Fund flow data fetched for {len(fund_flow_results)} stocks")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_concept_sector_fund_flow(self):
        """
        Test concept sector fund flow data fetching.
        
        This test validates:
        1. Can fetch sector-level fund flow for concepts
        2. Data contains expected fields
        3. Data is JSON compatible
        """
        validator = DataFrameValidator()
        
        integration_rate_limiter.wait()
        sector_flow = get_sector_fund_flow('concept')
        
        assert not sector_flow.empty, "Concept sector fund flow should not be empty"
        
        validator.validate_required_columns(
            sector_flow,
            ['date', 'sector_code', 'sector_name', 'sector_type', 'main_net_inflow']
        )
        validator.validate_json_compatible(sector_flow)
        
        # Verify sector_type is 'concept'
        assert all(sector_flow['sector_type'] == 'concept'), \
            "All rows should have sector_type='concept'"
        
        # Verify we have multiple sectors
        assert len(sector_flow) >= 10, "Should have at least 10 concept sectors"
        
        print("\n✓ Concept sector fund flow test passed:")
        print(f"  - Sectors: {len(sector_flow)}")
        print(f"  - Date: {sector_flow['date'].iloc[0] if not sector_flow.empty else 'N/A'}")


# ============================================================================
# Integration Tests - Real Data Fetching & Quality
# ============================================================================

class TestRealDataFetching:
    """Test real data fetching with quality validation."""
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_stock_fund_flow_real_data_quality(self):
        """
        Test stock fund flow with real data and validate quality.
        
        This test validates:
        1. Data can be fetched for well-known stocks
        2. Data contains reasonable values
        3. Data is consistent over time
        """
        validator = DataFrameValidator()
        
        # Test with well-known stocks
        test_symbols = ['600000', '000001', '600519']  # 浦发银行, 平安银行, 贵州茅台
        
        date_end = datetime.now().strftime('%Y-%m-%d')
        date_start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        for symbol in test_symbols:
            integration_rate_limiter.wait()
            df = get_stock_fund_flow(symbol, start_date=date_start, end_date=date_end)
            
            # Basic validation
            validator.validate_json_compatible(df)
            
            if not df.empty:
                # Validate required columns
                validator.validate_required_columns(
                    df,
                    ['date', 'symbol', 'close_price', 'pct_change', 'fundflow_main_net_inflow']
                )
                
                # Validate data quality
                # 1. Closing price should be positive
                validator.validate_numeric_range(df, 'close_price', min_value=0.01)
                
                # 2. Price change should be reasonable (-20% to +20%)
                validator.validate_numeric_range(df, 'pct_change', min_value=-20, max_value=20)
                
                # 3. Dates should be in order
                dates = pd.to_datetime(df['date'])
                assert dates.is_monotonic_increasing, "Dates should be in ascending order"
                
                # 4. No duplicate dates
                assert not dates.duplicated().any(), "Should not have duplicate dates"
                
                print(f"\n✓ Stock {symbol} fund flow data quality validated:")
                print(f"  - Records: {len(df)}")
                print(f"  - Date range: {df['date'].min()} to {df['date'].max()}")
                print(f"  - Price range: {df['close_price'].min():.2f} to {df['close_price'].max():.2f}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_main_fund_flow_rank_real_data(self):
        """
        Test main fund flow ranking with real data.
        
        This test validates:
        1. Can fetch ranking data
        2. Rankings are properly ordered
        3. Data contains reasonable values
        """
        validator = DataFrameValidator()
        
        # Get today's ranking
        date_today = datetime.now().strftime('%Y-%m-%d')
        
        integration_rate_limiter.wait()
        df = get_main_fund_flow_rank(date_today, indicator='net_inflow')
        
        assert not df.empty, "Main fund flow rank should not be empty"
        
        # Validate structure
        validator.validate_required_columns(
            df,
            ['rank', 'symbol', 'name', 'main_net_inflow', 'pct_change']
        )
        validator.validate_json_compatible(df)
        
        # Validate ranking
        assert df['rank'].iloc[0] == 1, "First row should have rank 1"
        assert df['rank'].is_monotonic_increasing, "Ranks should be in ascending order"
        
        # Validate we have enough data
        assert len(df) >= 50, "Should have at least 50 ranked stocks"
        
        # Validate symbol format
        for symbol in df['symbol'].head(10):
            assert len(symbol) == 6, f"Symbol {symbol} should be 6 digits"
            assert symbol.isdigit(), f"Symbol {symbol} should be numeric"
        
        print("\n✓ Main fund flow rank data validated:")
        print(f"  - Total ranked stocks: {len(df)}")
        print(f"  - Top stock: {df['name'].iloc[0]} ({df['symbol'].iloc[0]})")
        print(f"  - Top inflow: {df['main_net_inflow'].iloc[0]:,.0f}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_sector_lists_completeness(self):
        """
        Test that sector lists are complete and consistent.
        
        This test validates:
        1. Industry and concept lists are not empty
        2. Lists contain expected number of sectors
        3. Sector codes are unique
        """
        validator = DataFrameValidator()
        
        # Test industry list
        integration_rate_limiter.wait()
        industries = get_industry_list()
        
        assert not industries.empty, "Industry list should not be empty"
        assert len(industries) >= 20, "Should have at least 20 industries"
        
        # Check for duplicates
        assert not industries['sector_code'].duplicated().any(), \
            "Industry codes should be unique"
        
        validator.validate_json_compatible(industries)
        
        # Test concept list
        integration_rate_limiter.wait()
        concepts = get_concept_list()
        
        assert not concepts.empty, "Concept list should not be empty"
        assert len(concepts) >= 50, "Should have at least 50 concepts"
        
        # Check for duplicates
        assert not concepts['sector_code'].duplicated().any(), \
            "Concept codes should be unique"
        
        validator.validate_json_compatible(concepts)
        
        print("\n✓ Sector lists completeness validated:")
        print(f"  - Industries: {len(industries)}")
        print(f"  - Concepts: {len(concepts)}")


# ============================================================================
# Integration Tests - Cross-Validation
# ============================================================================

class TestCrossValidation:
    """Test data consistency across different API calls."""
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_constituent_count_consistency(self):
        """
        Test that constituent counts match actual constituent lists.
        
        This test validates:
        1. Constituent count in sector list matches actual constituents
        2. Data is consistent across different API calls
        """
        # Test with industries
        integration_rate_limiter.wait()
        industries = get_industry_list()
        
        if not industries.empty:
            # Pick first industry
            industry = industries.iloc[0]
            industry_code = industry['sector_code']
            reported_count = industry['constituent_count']
            
            integration_rate_limiter.wait()
            constituents = get_industry_constituents(industry_code)
            actual_count = len(constituents)
            
            # Allow some tolerance (±10%) as data might be slightly stale
            tolerance = max(5, int(reported_count * 0.1))
            assert abs(actual_count - reported_count) <= tolerance, \
                f"Constituent count mismatch for {industry['sector_name']}: " \
                f"reported {reported_count}, actual {actual_count}"
            
            print("\n✓ Constituent count consistency validated:")
            print(f"  - Industry: {industry['sector_name']}")
            print(f"  - Reported count: {reported_count}")
            print(f"  - Actual count: {actual_count}")
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_fund_flow_data_consistency(self):
        """
        Test that fund flow data is internally consistent.
        
        This test validates:
        1. Main net inflow equals sum of components
        2. Data relationships are mathematically correct
        """
        DataFrameValidator()
        
        # Get fund flow for a well-known stock
        symbol = '600000'
        date_end = datetime.now().strftime('%Y-%m-%d')
        date_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        integration_rate_limiter.wait()
        df = get_stock_fund_flow(symbol, start_date=date_start, end_date=date_end)
        
        if not df.empty and len(df) > 0:
            # Check if main_net_inflow approximately equals sum of components
            # (allowing for rounding errors)
            for _idx, row in df.iterrows():
                if pd.notna(row['fundflow_main_net_inflow']) and \
                   pd.notna(row['fundflow_super_large_net_inflow']) and \
                   pd.notna(row['fundflow_large_net_inflow']):
                    
                    calculated_main = row['fundflow_super_large_net_inflow'] + row['fundflow_large_net_inflow']
                    reported_main = row['fundflow_main_net_inflow']
                    
                    # Allow 1% tolerance for rounding
                    if abs(reported_main) > 1000:  # Only check if value is significant
                        relative_diff = abs(calculated_main - reported_main) / abs(reported_main)
                        assert relative_diff < 0.01, \
                            f"Main net inflow inconsistency on {row['date']}: " \
                            f"calculated {calculated_main:,.0f}, reported {reported_main:,.0f}"
            
            print("\n✓ Fund flow data consistency validated:")
            print(f"  - Symbol: {symbol}")
            print(f"  - Records checked: {len(df)}")


# ============================================================================
# Integration Tests - Error Handling with Real API
# ============================================================================

class TestRealAPIErrorHandling:
    """Test error handling with real API calls."""
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_invalid_symbol_real_api(self):
        """Test handling of invalid symbol with real API."""
        # Invalid symbol should raise ValueError before API call
        with pytest.raises(ValueError, match="Invalid symbol format"):
            get_stock_fund_flow('INVALID')
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_future_date_real_api(self):
        """Test handling of future dates with real API."""
        DataFrameValidator()
        
        # Future date should return empty result
        future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        integration_rate_limiter.wait()
        df = get_stock_fund_flow('600000', start_date=future_date, end_date=future_date)
        
        # Should return empty DataFrame with correct structure
        assert isinstance(df, pd.DataFrame)
        assert df.empty or len(df) == 0
        
        # Should still have correct columns
        expected_columns = [
            'date', 'symbol', 'close_price', 'pct_change',
            'fundflow_main_net_inflow', 'fundflow_main_net_inflow_rate',
            'fundflow_super_large_net_inflow', 'fundflow_large_net_inflow',
            'fundflow_medium_net_inflow', 'fundflow_small_net_inflow'
        ]
        assert list(df.columns) == expected_columns
    
    @pytest.mark.integration
    @skip_if_no_network()
    def test_invalid_sector_type_real_api(self):
        """Test handling of invalid sector type with real API."""
        # Invalid sector type should raise ValueError before API call
        with pytest.raises(ValueError, match="Invalid sector_type"):
            get_sector_fund_flow('invalid_type')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--run-integration'])
