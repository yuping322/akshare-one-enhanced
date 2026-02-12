# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Market Data Extension - 12 New Primitive Views

**Fund Flow Module** (`modules.fundflow`)
- `get_stock_fund_flow()` - Get individual stock fund flow data with main/super-large/large/medium/small order tracking
- `get_sector_fund_flow()` - Get industry/concept sector fund flow data
- `get_main_fund_flow_rank()` - Get main fund flow rankings by net inflow or rate
- `get_industry_list()` - Get list of industry sectors
- `get_industry_constituents()` - Get constituent stocks of an industry
- `get_concept_list()` - Get list of concept sectors
- `get_concept_constituents()` - Get constituent stocks of a concept

**Disclosure Module** (`modules.disclosure`)
- `get_disclosure_news()` - Get company announcements with category filtering (dividend, repurchase, ST, major events)
- `get_dividend_data()` - Get dividend distribution data with record/ex-dividend/payment dates
- `get_repurchase_data()` - Get stock buyback progress and details
- `get_st_delist_data()` - Get ST/delisting risk warnings

**Northbound Capital Module** (`modules.northbound`)
- `get_northbound_flow()` - Get northbound capital flow data (Shanghai/Shenzhen/All markets)
- `get_northbound_holdings()` - Get northbound holdings details with historical tracking
- `get_northbound_top_stocks()` - Get top stocks by northbound capital holdings

**Macro Data Module** (`modules.macro`)
- `get_lpr_rate()` - Get LPR (Loan Prime Rate) data for 1Y and 5Y terms
- `get_pmi_index()` - Get PMI index (manufacturing/non-manufacturing/Caixin)
- `get_cpi_data()` - Get CPI (Consumer Price Index) data
- `get_ppi_data()` - Get PPI (Producer Price Index) data
- `get_m2_supply()` - Get M2 money supply data
- `get_shibor_rate()` - Get Shibor rates for multiple terms
- `get_social_financing()` - Get social financing scale data

**Block Deal Module** (`modules.blockdeal`)
- `get_block_deal()` - Get block trade details with premium/discount rates
- `get_block_deal_summary()` - Get block trade statistics grouped by stock/date/broker

**Dragon-Tiger List Module** (`modules.lhb`)
- `get_dragon_tiger_list()` - Get dragon-tiger list data with broker details
- `get_dragon_tiger_summary()` - Get dragon-tiger statistics by stock/broker/reason
- `get_dragon_tiger_broker_stats()` - Get top broker statistics

**Limit Up/Down Module** (`modules.limitup`)
- `get_limit_up_pool()` - Get limit-up pool with timing and seal analysis
- `get_limit_down_pool()` - Get limit-down pool data
- `get_limit_up_stats()` - Get limit up/down statistics and broken board rates

**Margin Trading Module** (`modules.margin`)
- `get_margin_data()` - Get margin trading data (financing/securities lending)
- `get_margin_summary()` - Get market-wide margin trading summary

**Equity Pledge Module** (`modules.pledge`)
- `get_equity_pledge()` - Get equity pledge data with shareholder details
- `get_equity_pledge_ratio_rank()` - Get stocks ranked by pledge ratio

**Restricted Release Module** (`modules.restricted`)
- `get_restricted_release()` - Get restricted share release data
- `get_restricted_release_calendar()` - Get release calendar with market value

**Goodwill Module** (`modules.goodwill`)
- `get_goodwill_data()` - Get goodwill balance and impairment data
- `get_goodwill_impairment()` - Get goodwill impairment expectations
- `get_goodwill_by_industry()` - Get industry-level goodwill statistics

**ESG Rating Module** (`modules.esg`)
- `get_esg_rating()` - Get ESG ratings with E/S/G component scores
- `get_esg_rating_rank()` - Get ESG rankings with industry filtering

### Changed

- Enhanced exception handling system with new exception types:
  - `InvalidParameterError` - For parameter validation failures
  - `DataSourceUnavailableError` - For data source connectivity issues
  - `NoDataError` - For empty result scenarios
  - `UpstreamChangedError` - For upstream data structure changes

- Improved data standardization:
  - All interfaces return JSON-compatible DataFrames (no NaN/Infinity)
  - Unified date format (YYYY-MM-DD)
  - Consistent field naming conventions
  - Proper handling of empty results with preserved column structure

### Technical Improvements

- Implemented Factory + Provider pattern for all new modules
- Added comprehensive unit tests with 80%+ code coverage
- Added contract tests (golden samples) for schema stability
- Added integration tests for end-to-end validation
- Improved documentation with complete docstrings and examples
- Enhanced error handling and retry mechanisms
- Optimized JSON serialization for all data outputs

### Documentation

- Updated README.md with new interface listings and usage examples
- Added comprehensive API documentation for all 12 new modules
- Created migration guide from akshare to akshare-one
- Added interface comparison table

## [Previous Versions]

See git history for previous version changes.
