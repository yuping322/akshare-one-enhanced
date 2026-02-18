# Migration Guide: From AKShare to AKShare-One

This guide helps you migrate from raw AKShare to akshare-one, focusing on the 12 new market data extension interfaces.

## Table of Contents

1. [Why Migrate?](#why-migrate)
2. [Key Differences](#key-differences)
3. [Interface Mapping](#interface-mapping)
4. [Migration Examples](#migration-examples)
5. [Common Pitfalls](#common-pitfalls)
6. [Best Practices](#best-practices)

---

## Why Migrate?

AKShare-One provides several advantages over raw AKShare:

### 1. Unified Interface Design
- Consistent parameter naming across all functions
- Standardized date format (YYYY-MM-DD)
- Unified stock symbol format (6-digit string)

### 2. Better Data Quality
- JSON-compatible outputs (no NaN/Infinity)
- Standardized column names (English)
- Consistent data types across all rows
- Empty results preserve column structure

### 3. Improved Error Handling
- Clear exception types instead of silent failures
- Detailed error messages
- Proper validation of input parameters

### 4. Enhanced Developer Experience
- Complete type hints for IDE support
- Comprehensive docstrings
- Better documentation
- Easier testing and debugging

---

## Key Differences

### Parameter Naming

| Aspect | AKShare | AKShare-One |
|--------|---------|-------------|
| Stock symbol | `stock`, `symbol`, `code` (inconsistent) | Always `symbol` |
| Date format | Various formats | Always `YYYY-MM-DD` |
| Market | `market` parameter | Embedded in symbol or separate `market` param |
| Date range | `start`, `end` or single date | `start_date`, `end_date` |

### Output Format

| Aspect | AKShare | AKShare-One |
|--------|---------|-------------|
| Column names | Chinese | English |
| Date format | Various | YYYY-MM-DD string |
| Missing values | NaN, empty string | None (JSON null) |
| Symbol format | May have prefix/suffix | Clean 6-digit string |

---


## Interface Mapping

### 1. Fund Flow Data

#### Individual Stock Fund Flow

**AKShare:**
```python
import akshare as ak
df = ak.stock_individual_fund_flow(stock="600000", market="sh")
# Returns: Chinese column names, mixed date formats
```

**AKShare-One:**
```python
from akshare_one.modules.fundflow import get_stock_fund_flow
df = get_stock_fund_flow("600000", start_date="2024-01-01", end_date="2024-12-31")
# Returns: English columns, standardized YYYY-MM-DD dates
```

#### Sector Fund Flow

**AKShare:**
```python
df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
```

**AKShare-One:**
```python
from akshare_one.modules.fundflow import get_sector_fund_flow
df = get_sector_fund_flow("industry", start_date="2024-01-01", end_date="2024-12-31")
```

---

### 2. Disclosure and Announcements

#### Company Announcements

**AKShare:**
```python
df = ak.stock_notice_report(symbol="600000")
```

**AKShare-One:**
```python
from akshare_one.modules.disclosure import get_disclosure_news
df = get_disclosure_news("600000", start_date="2024-01-01", category="all")
```

#### Dividend Data

**AKShare:**
```python
df = ak.stock_dividend_cninfo(symbol="600000")
```

**AKShare-One:**
```python
from akshare_one.modules.disclosure import get_dividend_data
df = get_dividend_data("600000", start_date="2024-01-01")
```

---

### 3. Northbound Capital (HSGT)

#### Capital Flow

**AKShare:**
```python
df = ak.stock_hsgt_fund_flow_summary_em()
```

**AKShare-One:**
```python
from akshare_one.modules.northbound import get_northbound_flow
df = get_northbound_flow(start_date="2024-01-01", market="all")
```

#### Holdings

**AKShare:**
```python
df = ak.stock_hsgt_hold_stock_em(symbol="600000")
```

**AKShare-One:**
```python
from akshare_one.modules.northbound import get_northbound_holdings
df = get_northbound_holdings("600000", start_date="2024-01-01")
```

---

### 4. Macro Data

#### LPR Rates

**AKShare:**
```python
df = ak.rate_interbank_lpr()
```

**AKShare-One:**
```python
from akshare_one.modules.macro import get_lpr_rate
df = get_lpr_rate(start_date="2024-01-01")
```

#### PMI Index

**AKShare:**
```python
df = ak.macro_china_pmi()
```

**AKShare-One:**
```python
from akshare_one.modules.macro import get_pmi_index
df = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")
```

---

### 5. Block Deals

**AKShare:**
```python
df = ak.stock_dzjy_mrmx(start_date="20240101", end_date="20241231")
```

**AKShare-One:**
```python
from akshare_one.modules.blockdeal import get_block_deal
df = get_block_deal(symbol=None, start_date="2024-01-01", end_date="2024-12-31")
```

---

### 6. Dragon-Tiger List

**AKShare:**
```python
df = ak.stock_lhb_detail_em(start_date="20240101", end_date="20241231")
```

**AKShare-One:**
```python
from akshare_one.modules.lhb import get_dragon_tiger_list
df = get_dragon_tiger_list("2024-12-31")
```

---

### 7. Limit Up/Down Pool

**AKShare:**
```python
df = ak.stock_zt_pool_em(date="20241231")
```

**AKShare-One:**
```python
from akshare_one.modules.limitup import get_limit_up_pool
df = get_limit_up_pool("2024-12-31")
```

---

### 8. Margin Trading

**AKShare:**
```python
df = ak.stock_margin_detail_em(symbol="600000")
```

**AKShare-One:**
```python
from akshare_one.modules.margin import get_margin_data
df = get_margin_data("600000", start_date="2024-01-01")
```

---

### 9. Equity Pledge

**AKShare:**
```python
df = ak.stock_gpzy_pledge_ratio_em()
```

**AKShare-One:**
```python
from akshare_one.modules.pledge import get_equity_pledge
df = get_equity_pledge(symbol=None, start_date="2024-01-01")
```

---

### 10. Restricted Share Release

**AKShare:**
```python
df = ak.stock_restricted_release_queue_em(symbol="600000")
```

**AKShare-One:**
```python
from akshare_one.modules.restricted import get_restricted_release
df = get_restricted_release("600000", start_date="2024-01-01")
```

---

### 11. Goodwill

**AKShare:**
```python
df = ak.stock_sy_profile_em()
```

**AKShare-One:**
```python
from akshare_one.modules.goodwill import get_goodwill_data
df = get_goodwill_data(symbol=None, start_date="2024-01-01")
```

---

### 12. ESG Ratings

**AKShare:**
```python
df = ak.stock_esg_rate_sina()
```

**AKShare-One:**
```python
from akshare_one.modules.esg import get_esg_rating
df = get_esg_rating(symbol=None, start_date="2024-01-01")
```

---


## Migration Examples

### Example 1: Fund Flow Analysis

**Before (AKShare):**
```python
import akshare as ak
import pandas as pd

# Get fund flow - inconsistent interface
df1 = ak.stock_individual_fund_flow(stock="600000", market="sh")
df2 = ak.stock_individual_fund_flow(stock="000001", market="sz")

# Column names in Chinese
print(df1.columns)  # ['日期', '收盘价', '涨跌幅', '主力净流入-净额', ...]

# Date format inconsistent
df1['日期'] = pd.to_datetime(df1['日期'])

# Need manual data cleaning
df1 = df1.fillna(0)
```

**After (AKShare-One):**
```python
from akshare_one.modules.fundflow import get_stock_fund_flow

# Unified interface for all stocks
df1 = get_stock_fund_flow("600000", start_date="2024-01-01")
df2 = get_stock_fund_flow("000001", start_date="2024-01-01")

# English column names
print(df1.columns)  # ['date', 'symbol', 'close', 'pct_change', 'main_net_inflow', ...]

# Date already in YYYY-MM-DD format
# No NaN values - already cleaned
```

---

### Example 2: Multi-Source Data Integration

**Before (AKShare):**
```python
import akshare as ak

# Different interfaces, different formats
fund_flow = ak.stock_individual_fund_flow(stock="600000", market="sh")
northbound = ak.stock_hsgt_hold_stock_em(symbol="600000")
margin = ak.stock_margin_detail_em(symbol="600000")

# Need to manually standardize
fund_flow.rename(columns={'日期': 'date', '股票代码': 'symbol'}, inplace=True)
northbound.rename(columns={'日期': 'date', '代码': 'symbol'}, inplace=True)
margin.rename(columns={'日期': 'date', '代码': 'symbol'}, inplace=True)

# Merge with caution - date formats may differ
```

**After (AKShare-One):**
```python
from akshare_one.modules.fundflow import get_stock_fund_flow
from akshare_one.modules.northbound import get_northbound_holdings
from akshare_one.modules.margin import get_margin_data

# All interfaces return standardized format
fund_flow = get_stock_fund_flow("600000", start_date="2024-01-01")
northbound = get_northbound_holdings("600000", start_date="2024-01-01")
margin = get_margin_data("600000", start_date="2024-01-01")

# Can merge directly - all have 'date' and 'symbol' columns
merged = fund_flow.merge(northbound, on=['date', 'symbol'], how='outer')
merged = merged.merge(margin, on=['date', 'symbol'], how='outer')
```

---

### Example 3: JSON Export for API

**Before (AKShare):**
```python
import akshare as ak
import json

df = ak.stock_individual_fund_flow(stock="600000", market="sh")

# Problem: NaN values cause JSON serialization to fail
try:
    json_str = df.to_json(orient='records')
except ValueError as e:
    print(f"JSON serialization failed: {e}")
    
# Need manual cleaning
df = df.fillna(None)
df = df.replace([float('inf'), float('-inf')], None)
json_str = df.to_json(orient='records')
```

**After (AKShare-One):**
```python
from akshare_one.modules.fundflow import get_stock_fund_flow
import json

df = get_stock_fund_flow("600000", start_date="2024-01-01")

# JSON serialization works out of the box
json_str = df.to_json(orient='records')
data = json.loads(json_str)  # Success!
```

---

## Common Pitfalls

### 1. Date Format Confusion

**Problem:**
```python
# AKShare uses different date formats
df1 = ak.some_function(date="20240101")  # YYYYMMDD
df2 = ak.other_function(start="2024-01-01")  # YYYY-MM-DD
```

**Solution:**
```python
# AKShare-One always uses YYYY-MM-DD
df1 = get_some_data(date="2024-01-01")
df2 = get_other_data(start_date="2024-01-01")
```

---

### 2. Symbol Format Issues

**Problem:**
```python
# AKShare may return symbols with prefixes
df = ak.some_function()
print(df['symbol'])  # ['SH600000', 'SZ000001', ...]
```

**Solution:**
```python
# AKShare-One returns clean 6-digit symbols
df = get_some_data()
print(df['symbol'])  # ['600000', '000001', ...]
```

---

### 3. Missing Value Handling

**Problem:**
```python
# AKShare returns NaN which breaks JSON
df = ak.some_function()
df.to_json()  # May fail or produce invalid JSON
```

**Solution:**
```python
# AKShare-One returns None (JSON null)
df = get_some_data()
df.to_json()  # Always works
```

---

### 4. Column Name Inconsistency

**Problem:**
```python
# Need to remember Chinese column names
df = ak.stock_individual_fund_flow(stock="600000", market="sh")
main_inflow = df['主力净流入-净额']  # Hard to remember
```

**Solution:**
```python
# English column names are consistent
df = get_stock_fund_flow("600000")
main_inflow = df['main_net_inflow']  # Clear and consistent
```

---

## Best Practices

### 1. Use Type Hints

```python
from typing import Optional
import pandas as pd
from akshare_one.modules.fundflow import get_stock_fund_flow

def analyze_fund_flow(symbol: str, days: int = 30) -> pd.DataFrame:
    """Analyze fund flow for the last N days."""
    from datetime import datetime, timedelta
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    return get_stock_fund_flow(symbol, start_date, end_date)
```

### 2. Handle Exceptions Properly

```python
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    DataSourceUnavailableError,
    NoDataError
)

try:
    df = get_stock_fund_flow("600000", start_date="2024-01-01")
except InvalidParameterError as e:
    print(f"Invalid parameters: {e}")
except DataSourceUnavailableError as e:
    print(f"Data source unavailable: {e}")
except NoDataError as e:
    print(f"No data available: {e}")
```

### 3. Validate Data Before Use

```python
def validate_data(df: pd.DataFrame) -> bool:
    """Validate data quality."""
    # Check if DataFrame is empty
    if df.empty:
        return False
    
    # Check required columns
    required_cols = ['date', 'symbol']
    if not all(col in df.columns for col in required_cols):
        return False
    
    # Check date format
    try:
        pd.to_datetime(df['date'], format='%Y-%m-%d')
    except ValueError:
        return False
    
    return True

df = get_stock_fund_flow("600000")
if validate_data(df):
    # Process data
    pass
```

### 4. Use Batch Queries When Possible

```python
# Instead of multiple single-stock queries
symbols = ['600000', '000001', '000002']
dfs = []
for symbol in symbols:
    df = get_stock_fund_flow(symbol, start_date="2024-01-01")
    dfs.append(df)
result = pd.concat(dfs, ignore_index=True)

# Consider using symbol=None for batch queries (when available)
df = get_stock_fund_flow(symbol=None, start_date="2024-01-01")
result = df[df['symbol'].isin(symbols)]
```

---

## Quick Reference Table

| Task | AKShare Function | AKShare-One Function |
|------|------------------|---------------------|
| Stock fund flow | `stock_individual_fund_flow()` | `get_stock_fund_flow()` |
| Sector fund flow | `stock_sector_fund_flow_rank()` | `get_sector_fund_flow()` |
| Announcements | `stock_notice_report()` | `get_disclosure_news()` |
| Dividends | `stock_dividend_cninfo()` | `get_dividend_data()` |
| Northbound flow | `stock_hsgt_fund_flow_summary_em()` | `get_northbound_flow()` |
| Northbound holdings | `stock_hsgt_hold_stock_em()` | `get_northbound_holdings()` |
| LPR rates | `rate_interbank_lpr()` | `get_lpr_rate()` |
| PMI index | `macro_china_pmi()` | `get_pmi_index()` |
| Block deals | `stock_dzjy_mrmx()` | `get_block_deal()` |
| Dragon-tiger list | `stock_lhb_detail_em()` | `get_dragon_tiger_list()` |
| Limit up pool | `stock_zt_pool_em()` | `get_limit_up_pool()` |
| Margin trading | `stock_margin_detail_em()` | `get_margin_data()` |
| Equity pledge | `stock_gpzy_pledge_ratio_em()` | `get_equity_pledge()` |
| Restricted release | `stock_restricted_release_queue_em()` | `get_restricted_release()` |
| Goodwill | `stock_sy_profile_em()` | `get_goodwill_data()` |
| ESG ratings | `stock_esg_rate_sina()` | `get_esg_rating()` |

---

## Need Help?

- **Documentation**: See [API Documentation](api/market-data-extension.md)
- **Examples**: Check `examples/` directory
- **Issues**: Report on GitHub
- **Community**: Join discussions

---

*Last Updated: 2024*
