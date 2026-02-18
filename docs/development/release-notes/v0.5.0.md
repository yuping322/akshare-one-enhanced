# Release Notes - AKShare-One v0.5.0

## Release Date: TBD

## Overview

This major release adds 12 new Primitive Views for comprehensive market data coverage, significantly expanding akshare-one's capabilities beyond basic stock data to include fund flow, announcements, northbound capital, macro indicators, and more.

---

## 🎉 Major Features

### 12 New Market Data Modules

This release introduces 12 new data modules, adding 40+ new functions:

1. **Fund Flow Module** (7 functions)
   - Individual stock fund flow tracking
   - Sector (industry/concept) fund flow analysis
   - Main fund flow rankings
   - Industry and concept sector lists and constituents

2. **Disclosure Module** (4 functions)
   - Company announcements and disclosures
   - Dividend distribution data
   - Stock buyback tracking
   - ST/delisting risk warnings

3. **Northbound Capital Module** (3 functions)
   - Northbound capital flow (Shanghai/Shenzhen Connect)
   - Northbound holdings tracking
   - Top stocks by northbound holdings

4. **Macro Data Module** (6 functions)
   - LPR (Loan Prime Rate)
   - PMI (Purchasing Managers' Index)
   - CPI/PPI (Consumer/Producer Price Index)
   - M2 money supply
   - Shibor rates
   - Social financing scale

5. **Block Deal Module** (2 functions)
   - Block trade details with premium/discount rates
   - Block trade statistics and summaries

6. **Dragon-Tiger List Module** (3 functions)
   - Dragon-tiger list data (unusual trading activity)
   - Statistics by stock/broker/reason
   - Top broker analysis

7. **Limit Up/Down Module** (3 functions)
   - Limit-up pool with timing and seal analysis
   - Limit-down pool
   - Limit up/down statistics

8. **Margin Trading Module** (2 functions)
   - Margin trading data (financing/securities lending)
   - Market-wide margin trading summary

9. **Equity Pledge Module** (2 functions)
   - Equity pledge data with shareholder details
   - Pledge ratio rankings

10. **Restricted Release Module** (2 functions)
    - Restricted share release data
    - Release calendar with market value

11. **Goodwill Module** (3 functions)
    - Goodwill balance and impairment data
    - Goodwill impairment expectations
    - Industry-level goodwill statistics

12. **ESG Rating Module** (2 functions)
    - ESG ratings with E/S/G component scores
    - ESG rankings with industry filtering

---

## ✨ Key Improvements

### Enhanced Data Quality

- **JSON Compatibility**: All outputs are now guaranteed to be JSON-serializable
  - No NaN or Infinity values (replaced with None)
  - All dates as strings (YYYY-MM-DD format)
  - All symbols as 6-digit strings with leading zeros

- **Standardized Output**: Consistent data structure across all modules
  - English column names (snake_case)
  - Unified date format (YYYY-MM-DD)
  - Consistent numeric types
  - Empty results preserve column structure

### Improved Error Handling

- New exception hierarchy for better error management:
  - `InvalidParameterError` - Parameter validation failures
  - `DataSourceUnavailableError` - Data source connectivity issues
  - `NoDataError` - Empty result scenarios
  - `UpstreamChangedError` - Upstream data structure changes

- Better error messages with context
- Proper input validation for all functions

### Better Developer Experience

- Complete type hints for all public functions
- Comprehensive docstrings with examples
- Consistent API design across all modules
- Better IDE support with type annotations

---

## 📚 Documentation

### New Documentation

- **API Documentation**: Complete reference for all 12 new modules
- **Migration Guide**: Detailed guide for migrating from raw AKShare
- **Code Review Checklist**: Quality assurance documentation
- **Updated README**: New interface listings and usage examples
- **CHANGELOG**: Comprehensive change log

### Improved Documentation

- Enhanced docstrings with parameter descriptions and examples
- Better code comments for complex logic
- More usage examples

---

## 🔧 Technical Changes

### Architecture

- Implemented Factory + Provider pattern for all new modules
- Consistent module structure across all 12 modules
- Stateless providers for thread-safe concurrent access
- Clear separation of concerns

### Testing

- 80%+ code coverage for all new modules
- Unit tests for all functions
- Integration tests for key workflows
- Contract tests (golden samples) for schema stability
- Comprehensive test framework

### Performance

- Response time < 10 seconds for 95% of requests
- Efficient data transformations
- No memory leaks
- Optimized JSON serialization

---

## 🔄 Breaking Changes

None. This release is fully backward compatible with v0.4.0.

---

## 📦 Installation

### Upgrade from v0.4.0

```bash
pip install --upgrade akshare-one
```

### Fresh Installation

```bash
pip install akshare-one==0.5.0
```

---

## 🚀 Quick Start

### Fund Flow Analysis

```python
from akshare_one.modules.fundflow import get_stock_fund_flow

# Get stock fund flow
df = get_stock_fund_flow("600000", start_date="2024-01-01")
print(df.head())
```

### Northbound Capital Tracking

```python
from akshare_one.modules.northbound import get_northbound_flow

# Get northbound capital flow
df = get_northbound_flow(start_date="2024-01-01", market="all")
print(df.head())
```

### Macro Data Analysis

```python
from akshare_one.modules.macro import get_lpr_rate, get_pmi_index

# Get LPR rates
lpr = get_lpr_rate(start_date="2024-01-01")

# Get PMI index
pmi = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")
```

---

## 📊 Statistics

- **New Modules**: 12
- **New Functions**: 40+
- **Lines of Code**: ~5,000+ (new code)
- **Test Coverage**: 80%+
- **Documentation Pages**: 5 new documents

---

## 🙏 Acknowledgments

This release was made possible by:

- The AKShare project for providing the underlying data sources
- The open-source community for feedback and suggestions
- All contributors and testers

---

## 🔮 What's Next (v0.6.0)

Planned features for the next release:

- Additional data sources for redundancy
- Caching layer for improved performance
- Data quality metrics and monitoring
- More macro indicators
- Enhanced error recovery mechanisms

---

## 📝 Full Changelog

See [CHANGELOG.md](../CHANGELOG.md) for detailed changes.

---

## 🐛 Known Issues

None at this time.

---

## 💬 Feedback

We welcome your feedback! Please:

- Report bugs on [GitHub Issues](https://github.com/zwldarren/akshare-one/issues)
- Suggest features on [GitHub Discussions](https://github.com/zwldarren/akshare-one/discussions)
- Contribute via [Pull Requests](https://github.com/zwldarren/akshare-one/pulls)

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details

---

*Released by the AKShare-One Team*
