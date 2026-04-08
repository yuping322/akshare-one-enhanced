# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-04-04

### Added

#### Core Features

- **Multi-source data routing system** - Automatic failover between data sources with intelligent routing
  - New `MultiSourceRouter` class for managing multiple providers
  - Auto-switching when data source fails or times out
  - Configurable source priority and retry strategies
  - Multi-source API endpoints: `get_*_multi_source()` for all major data types

- **Unified filtering API** - Consistent data filtering across all modules
  - `columns` parameter: Select specific columns to return
  - `row_filter` parameter: Advanced row filtering with sorting, sampling, query expressions, and top_n
  - `apply_data_filter()` utility function for custom filtering

- **Comprehensive exception hierarchy** - Structured error handling system
  - New exception module with specialized exception types:
    - `InvalidParameterError` - Parameter validation failures
    - `DataSourceUnavailableError` - Network/data source issues
    - `NoDataError` - Empty data responses
    - `UpstreamChangedError` - API contract violations
    - `RateLimitError` - Rate limiting scenarios
    - `DataValidationError` - Data integrity issues
  - Exception mapping utilities for public API compatibility

- **Monitoring and observability features**
  - Structured JSON logging system across all providers
  - Data source health check mechanism
  - Performance metrics collection
  - Cache hit rate tracking
  - Execution result tracking with `ExecutionResult` class

#### Market Data Extension Modules

Complete implementation of 14 new market data modules with standardized APIs:

- **Northbound Capital** (`northbound`)
  - `get_northbound_flow()` - Northbound capital flow tracking
  - `get_northbound_holdings()` - Holdings detail by stock
  - `get_northbound_top_stocks()` - Top held stocks ranking

- **Fund Flow** (`fundflow`)
  - `get_stock_fund_flow()` - Individual stock fund flow
  - `get_sector_fund_flow()` - Sector/concept fund flow
  - `get_main_fund_flow_rank()` - Main force fund flow ranking

- **Dragon Tiger List** (`lhb`)
  - `get_dragon_tiger_list()` - Daily dragon tiger list
  - `get_dragon_tiger_summary()` - Statistical summary
  - `get_dragon_tiger_broker_stats()` - Broker analysis

- **Limit Up/Down Pool** (`limitup`)
  - `get_limit_up_pool()` - Daily limit up stocks
  - `get_limit_down_pool()` - Daily limit down stocks
  - `get_limit_up_stats()` - Limit up statistics

- **Block Deal** (`blockdeal`)
  - `get_block_deal()` - Block trade details
  - `get_block_deal_summary()` - Block trade summary

- **Disclosure News** (`disclosure`)
  - `get_disclosure_news()` - Company announcements
  - `get_dividend_data()` - Dividend distribution data
  - `get_repurchase_data()` - Stock repurchase data
  - `get_st_delist_data()` - ST/delisting risk stocks

- **Macro Data** (`macro`)
  - `get_lpr_rate()` - Loan Prime Rate
  - `get_pmi_index()` - PMI index (manufacturing/non-manufacturing)
  - `get_cpi_data()` - Consumer Price Index
  - `get_ppi_data()` - Producer Price Index
  - `get_m2_supply()` - M2 money supply
  - `get_shibor_rate()` - SHIBOR interest rates
  - `get_social_financing()` - Social financing data

- **Margin Trading** (`margin`)
  - `get_margin_data()` - Margin trading data
  - `get_margin_summary()` - Market-wide margin summary

- **Equity Pledge** (`pledge`)
  - `get_equity_pledge()` - Equity pledge details
  - `get_equity_pledge_ratio_rank()` - Pledge ratio ranking

- **Restricted Release** (`restricted`)
  - `get_restricted_release()` - Restricted share release data
  - `get_restricted_release_calendar()` - Release calendar

- **Goodwill** (`goodwill`)
  - `get_goodwill_data()` - Goodwill data
  - `get_goodwill_impairment()` - Impairment expectations
  - `get_goodwill_by_industry()` - Industry-level statistics

- **ESG Rating** (`esg`)
  - `get_esg_rating()` - ESG rating by stock
  - `get_esg_rating_rank()` - ESG rating ranking

- **Analyst Data** (`analyst`)
  - Enhanced analyst ranking with standardized fields
  - Fixed eastmoney analyst rank filtering

- **Market Sentiment** (`sentiment`)
  - Hot stock ranking
  - Sentiment indicators

#### Infrastructure Improvements

- **Dynamic field mapping system** - Automatic field name standardization
  - Complete field naming standards documentation
  - Dynamic mapping between upstream fields and standardized output
  - Field naming models for consistent data contracts

- **AkShare compatibility adapter** - Handle upstream API drift
  - `AkShareAdapter` for managing function signature changes
  - `call_akshare()` with fallback handling
  - Function existence checking utilities

- **Module factory automation** - Simplified provider creation
  - `@api_endpoint` decorator for automatic routing
  - Unified factory pattern across all modules
  - Removed individual factory.py files (19 files deleted)

- **Data source implementations**
  - Added backup data sources for 14 single-source modules
  - Enhanced Sina provider for futures/options/historical
  - Improved Eastmoney providers with better error handling

#### Developer Experience

- **Comprehensive documentation**
  - Field standardization report
  - Compatibility contract documentation
  - API map completion report
  - Coverage strategy documentation
  - Product readiness plan

- **Enhanced test infrastructure**
  - Test timeout configuration (60s default)
  - Contract tests for API stability
  - Backup provider tests
  - Edge case testing improvements
  - Multi-source comprehensive tests

- **CI/CD workflows**
  - Automated testing workflow
  - Standardization checks workflow
  - Coverage reporting integration

### Changed

#### API Changes

- **BREAKING: Factory pattern refactoring** - All modules now use unified routing
  - Removed individual `factory.py` files from all modules (19 modules affected)
  - New `@api_endpoint` decorator replaces explicit factory calls
  - All public APIs now support `source`, `columns`, `row_filter` parameters

- **Standardized parameter names**
  - All data fetching functions now use consistent parameter naming
  - Date parameters: `start_date`, `end_date` (YYYY-MM-DD format)
  - Symbol parameter: always `symbol` (6-digit format)
  - Source parameter: `source` for single-source, `sources` for multi-source

- **Enhanced return structures**
  - All DataFrame outputs now follow standardized field naming
  - Timestamp fields: `timestamp` (datetime type)
  - Price fields: `open`, `high`, `low`, `close`
  - Volume fields: `volume`, `amount`

- **Multi-source API naming convention**
  - Multi-source endpoints: `get_*_multi_source()` pattern
  - Router creation: `create_*_router()` pattern
  - Execution method: `router.execute(method_name, *args)`

#### Module Architecture

- **BaseProvider enhancements**
  - Added structured logging integration
  - Performance metrics collection hooks
  - Health check capabilities
  - Cache statistics tracking

- **Factory base class improvements**
  - Generic type support with TypeVar
  - Automatic method routing via decorators
  - Exception mapping for public API
  - Standard parameter handling

- **Cache system updates**
  - Tiered cache durations (hourly for intraday, daily for historical)
  - Cache statistics and hit rate tracking
  - Enhanced cache key generation

#### Configuration

- **pyproject.toml updates**
  - Coverage tiered thresholds strategy (30% baseline)
  - Ruff linting configuration improvements
  - Test timeout settings
  - Optional dependency groups (talib, mcp)

### Deprecated

- **Direct factory instantiation** - Use `@api_endpoint` decorator instead
- **Manual data source switching** - Use multi-source routers instead
- **Implicit field naming** - All fields should follow standardized naming

### Removed

#### Files Deleted

- Individual factory files from 19 modules:
  - `analyst/factory.py`, `blockdeal/factory.py`, `board/factory.py`
  - `bond/factory.py`, `concept/factory.py`, `disclosure/factory.py`
  - `esg/factory.py`, `etf/factory.py`, `financial/factory.py`
  - `fundflow/factory.py`, `futures/factory.py`, `goodwill/factory.py`
  - `historical/factory.py`, `hkus/factory.py`, `index/factory.py`
  - `industry/factory.py`, `info/factory.py`, `insider/factory.py`
  - `ipo/factory.py`, `lhb/factory.py`, `limitup/factory.py`
  - `macro/factory.py`, `margin/factory.py`, `news/factory.py`
  - `northbound/factory.py`, `options/factory.py`, `performance/factory.py`
  - `pledge/factory.py`, `restricted/factory.py`, `sentiment/factory.py`
  - `shareholder/factory.py`, `st/factory.py`, `suspended/factory.py`
  - `valuation/factory.py`

- Compiled Python cache files removed from tracking
  - All `__pycache__` directories
  - `.pyc` files

#### APIs Removed

- **Old-style factory methods** - Direct provider instantiation without routing
- **Undocumented data source parameters** - Non-standard source configurations

### Fixed

#### Bug Fixes

- **Upstream API drift handling**
  - Fixed test failures due to upstream API changes
  - Enhanced error handling for changed field names
  - Improved timeout handling for slow APIs

- **Data validation issues**
  - Fixed floating-point underflow in test cases
  - Corrected missing test decorators (skip markers)
  - Resolved data type mismatches

- **Module initialization**
  - Added missing `__init__.py` files for proper module exports
  - Fixed import errors in extended modules
  - Resolved circular dependency issues

- **Analyst data standardization**
  - Fixed eastmoney analyst rank filtering logic
  - Corrected field naming inconsistencies
  - Improved data type handling

- **Test reliability improvements**
  - Fixed flaky tests with proper timeout handling
  - Enhanced API error handling in tests
  - Improved test isolation and cleanup

#### Performance Improvements

- **Cache optimization**
  - Reduced redundant API calls through better caching
  - Improved cache hit rates with smarter key generation
  - Added cache statistics for monitoring

- **Module compression**
  - Reduced code duplication through factory consolidation
  - Simplified module structure (204 files changed, 2154 insertions, 2712 deletions)
  - Improved import efficiency

- **Error handling efficiency**
  - Faster failure detection with timeout improvements
  - Reduced retry overhead with intelligent backoff
  - Better exception propagation

### Security

- **SSL verification configuration**
  - Added `configure_ssl_verification()` for custom SSL handling
  - Improved HTTPS connection security
  - Enhanced certificate validation options

- **Input validation**
  - Enhanced parameter validation across all APIs
  - Improved symbol format checking (6-digit requirement)
  - Better date range validation

---

## [0.4.0] - 2026-02-15

### Added

- Initial market data extension interface design
- Codebase summary documentation
- Basic multi-source support for historical/realtime data

### Changed

- Improved test reliability and API error handling
- Enhanced error messages for debugging

### Fixed

- Fixed test timeout issues
- Resolved API contract violations

---

## [0.3.0] - 2026-01-20

### Added

- ETF, Bond, Index modules with basic providers
- Valuation, Shareholder, Performance modules
- Analyst and Sentiment data support
- Concept and Industry sector modules

### Changed

- Standardized field naming conventions
- Improved cache system

### Fixed

- Fixed upstream field naming inconsistencies
- Resolved import errors

---

## [0.2.0] - 2025-12-15

### Added

- Financial data module (balance sheet, income statement, cash flow)
- Insider trading data support
- HK and US stock data modules
- IPO and new stock data

### Changed

- Enhanced base provider architecture
- Improved error handling

### Fixed

- Fixed date parsing issues
- Corrected symbol validation

---

## [0.1.0] - 2025-11-10

### Added

- Initial release with core modules
- Historical data fetching (`get_hist_data`)
- Realtime data support (`get_realtime_data`)
- News data module (`get_news_data`)
- Basic info module (`get_basic_info`)
- Futures and Options modules
- Technical indicators support
- AkShare adapter for upstream compatibility

### Infrastructure

- Basic provider pattern implementation
- Simple cache system
- Error handling framework
- Test infrastructure setup
- CI/CD pipeline initialization

---

[0.5.0]: https://github.com/zwldarren/akshare-one/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/zwldarren/akshare-one/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/zwldarren/akshare-one/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/zwldarren/akshare-one/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/zwldarren/akshare-one/releases/tag/v0.1.0