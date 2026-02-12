# 🎉 AKShare-One v0.5.0 Released - 12 New Market Data Modules!

We're excited to announce the release of **AKShare-One v0.5.0**, a major update that significantly expands the library's capabilities with 12 new market data modules and 40+ new functions!

## 🚀 What's New

### 12 New Primitive Views

This release adds comprehensive market data coverage beyond basic stock information:

1. **📊 Fund Flow** - Track main fund movements in stocks and sectors
2. **📢 Disclosure** - Monitor company announcements, dividends, and buybacks
3. **🌏 Northbound Capital** - Follow foreign investment through Shanghai/Shenzhen Connect
4. **📈 Macro Data** - Access key economic indicators (LPR, PMI, CPI, M2, Shibor)
5. **💼 Block Deals** - Analyze large block trades with premium/discount rates
6. **🐉 Dragon-Tiger List** - Track unusual trading activity and top brokers
7. **📊 Limit Up/Down** - Monitor limit-up/down pools and statistics
8. **💰 Margin Trading** - Access financing and securities lending data
9. **🔒 Equity Pledge** - Track stock pledge ratios and risks
10. **🔓 Restricted Release** - Monitor restricted share release schedules
11. **💎 Goodwill** - Analyze goodwill and impairment risks
12. **🌱 ESG Ratings** - Access ESG scores and rankings

## ✨ Key Features

### Unified Interface Design
- Consistent API across all 40+ new functions
- Standardized parameter naming (`symbol`, `start_date`, `end_date`)
- Unified date format (YYYY-MM-DD)

### JSON-Ready Data
- All outputs are JSON-serializable (no NaN/Infinity)
- Clean 6-digit stock symbols with leading zeros
- Consistent data types across all modules

### Better Error Handling
- Clear exception types for different error scenarios
- Detailed error messages with context
- Proper input validation

### Complete Documentation
- Comprehensive API documentation
- Migration guide from raw AKShare
- Usage examples for all functions
- Type hints for better IDE support

## 📦 Installation

Upgrade to v0.5.0:

```bash
pip install --upgrade akshare-one
```

## 🎯 Quick Examples

### Track Fund Flow
```python
from akshare_one.modules.fundflow import get_stock_fund_flow

# Get main fund flow for a stock
df = get_stock_fund_flow("600000", start_date="2024-01-01")
print(df[['date', 'main_net_inflow', 'pct_change']].head())
```

### Monitor Northbound Capital
```python
from akshare_one.modules.northbound import get_northbound_flow

# Track foreign investment
df = get_northbound_flow(start_date="2024-01-01", market="all")
print(df[['date', 'net_buy', 'balance']].head())
```

### Analyze Macro Trends
```python
from akshare_one.modules.macro import get_lpr_rate, get_pmi_index

# Get LPR rates
lpr = get_lpr_rate(start_date="2024-01-01")

# Get PMI index
pmi = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")
```

### Check Announcements
```python
from akshare_one.modules.disclosure import get_dividend_data

# Get dividend announcements
df = get_dividend_data("600000", start_date="2024-01-01")
print(df[['symbol', 'fiscal_year', 'dividend_per_share']].head())
```

## 📚 Documentation

- **API Reference**: [docs/api/market-data-extension.md](docs/api/market-data-extension.md)
- **Migration Guide**: [docs/migration-guide.md](docs/migration-guide.md)
- **Release Notes**: [docs/release-notes-v0.5.0.md](docs/release-notes-v0.5.0.md)
- **Full Changelog**: [CHANGELOG.md](CHANGELOG.md)

## 🎓 Why Upgrade?

### For Quantitative Traders
- Access to comprehensive market data in one place
- Consistent data format for easier backtesting
- JSON-ready outputs for API integration

### For Data Analysts
- Standardized column names (no more Chinese characters)
- Clean data with proper null handling
- Easy integration with pandas workflows

### For Developers
- Complete type hints for better IDE support
- Clear error messages for debugging
- Comprehensive documentation and examples

## 🔄 Migration from AKShare

Migrating from raw AKShare is straightforward:

**Before (AKShare):**
```python
import akshare as ak
df = ak.stock_individual_fund_flow(stock="600000", market="sh")
# Chinese columns, inconsistent formats
```

**After (AKShare-One):**
```python
from akshare_one.modules.fundflow import get_stock_fund_flow
df = get_stock_fund_flow("600000", start_date="2024-01-01")
# English columns, standardized format, JSON-ready
```

See our [Migration Guide](docs/migration-guide.md) for detailed examples.

## 🏆 Quality Assurance

- **80%+ Test Coverage** - Comprehensive unit and integration tests
- **Type Safety** - Complete type hints for all functions
- **Performance** - Response time < 10 seconds for 95% of requests
- **Reliability** - Proper error handling and validation

## 🤝 Contributing

We welcome contributions! Whether it's:
- Bug reports
- Feature requests
- Documentation improvements
- Code contributions

Visit our [GitHub repository](https://github.com/zwldarren/akshare-one) to get involved.

## 🙏 Acknowledgments

Special thanks to:
- The AKShare project for providing the underlying data sources
- Our contributors and testers
- The open-source community

## 🔮 What's Next

We're already planning v0.6.0 with:
- Additional data sources for redundancy
- Caching layer for improved performance
- More macro indicators
- Enhanced monitoring and metrics

## 📞 Get in Touch

- **GitHub**: https://github.com/zwldarren/akshare-one
- **Issues**: https://github.com/zwldarren/akshare-one/issues
- **Discussions**: https://github.com/zwldarren/akshare-one/discussions

## 📄 License

AKShare-One is released under the MIT License.

---

**Happy Trading! 📈**

*The AKShare-One Team*

---

## Social Media Posts

### Twitter/X
```
🎉 AKShare-One v0.5.0 is here! 

12 new market data modules
40+ new functions
JSON-ready outputs
Complete documentation

Track fund flow, northbound capital, macro data, and more!

pip install --upgrade akshare-one

#Python #QuantTrading #FinTech #OpenSource
```

### LinkedIn
```
Excited to announce AKShare-One v0.5.0! 🚀

This major release adds 12 new market data modules covering:
📊 Fund Flow Analysis
🌏 Northbound Capital Tracking
📈 Macro Economic Indicators
💼 Block Deals & Dragon-Tiger List
💰 Margin Trading & Equity Pledge
🌱 ESG Ratings

Key improvements:
✅ JSON-ready outputs
✅ Unified API design
✅ Complete type hints
✅ 80%+ test coverage

Perfect for quantitative traders, data analysts, and fintech developers working with Chinese market data.

Check it out: https://github.com/zwldarren/akshare-one

#QuantitativeFinance #Python #DataScience #FinTech
```

### Reddit (r/algotrading, r/Python)
```
[Release] AKShare-One v0.5.0 - Comprehensive Chinese Market Data Library

Hey everyone! Just released v0.5.0 of AKShare-One, a Python library for Chinese financial market data.

**What's New:**
- 12 new data modules (fund flow, northbound capital, macro data, etc.)
- 40+ new functions with consistent API
- JSON-ready outputs (no more NaN issues!)
- Complete documentation and migration guide

**Why it matters:**
- Standardized interface over raw AKShare
- Clean, consistent data format
- Type hints for better IDE support
- Comprehensive test coverage

**Installation:**
```pip install --upgrade akshare-one```

**Quick example:**
```python
from akshare_one.modules.fundflow import get_stock_fund_flow
df = get_stock_fund_flow("600000", start_date="2024-01-01")
```

GitHub: https://github.com/zwldarren/akshare-one

Would love to hear your feedback!
```

---

*Last Updated: 2024*
