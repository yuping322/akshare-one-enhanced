# Market Data Extension API Documentation

This document provides comprehensive API documentation for the 12 new Primitive Views added to akshare-one.

## Table of Contents

1. [Fund Flow Module](#fund-flow-module)
2. [Disclosure Module](#disclosure-module)
3. [Northbound Capital Module](#northbound-capital-module)
4. [Macro Data Module](#macro-data-module)
5. [Block Deal Module](#block-deal-module)
6. [Dragon-Tiger List Module](#dragon-tiger-list-module)
7. [Limit Up/Down Module](#limit-updown-module)
8. [Margin Trading Module](#margin-trading-module)
9. [Equity Pledge Module](#equity-pledge-module)
10. [Restricted Release Module](#restricted-release-module)
11. [Goodwill Module](#goodwill-module)
12. [ESG Rating Module](#esg-rating-module)

## Overview

All interfaces follow these design principles:

- **Unified Date Format**: All dates use `YYYY-MM-DD` format
- **JSON Compatible**: All outputs are JSON-serializable (no NaN/Infinity)
- **Standardized Fields**: Consistent field naming across modules
- **Empty Results**: Return empty DataFrames with preserved column structure
- **Error Handling**: Comprehensive exception handling with clear error messages

## Common Parameters

Most interfaces share these common parameters:

- `symbol`: Stock symbol (e.g., '600000'), 6-digit string
- `start_date`: Start date in YYYY-MM-DD format (default: "1970-01-01")
- `end_date`: End date in YYYY-MM-DD format (default: "2030-12-31")
- `source`: Data source, typically "eastmoney" (default)

---


## 1. Fund Flow Module

**Import**: `from akshare_one.modules.fundflow import *`

### 1.1 get_stock_fund_flow()

Get individual stock fund flow data with detailed order size breakdown.

**Parameters:**
- `symbol` (str): Stock symbol (e.g., '600000')
- `start_date` (str): Start date (default: "1970-01-01")
- `end_date` (str): End date (default: "2030-12-31")
- `source` (str): Data source (default: "eastmoney")

**Returns:** DataFrame with columns:
- `date`: Date (YYYY-MM-DD)
- `symbol`: Stock symbol
- `close`: Closing price
- `pct_change`: Price change percentage
- `main_net_inflow`: Main fund net inflow (元)
- `main_net_inflow_rate`: Main fund net inflow rate (%)
- `super_large_net_inflow`: Super large order net inflow (元)
- `large_net_inflow`: Large order net inflow (元)
- `medium_net_inflow`: Medium order net inflow (元)
- `small_net_inflow`: Small order net inflow (元)

**Example:**
```python
df = get_stock_fund_flow("600000", start_date="2024-01-01", end_date="2024-12-31")
print(df.head())
```

### 1.2 get_sector_fund_flow()

Get sector (industry/concept) fund flow data.

**Parameters:**
- `sector_type` (Literal["industry", "concept"]): Sector type
- `start_date` (str): Start date
- `end_date` (str): End date
- `source` (str): Data source

**Returns:** DataFrame with columns:
- `date`: Date
- `sector_code`: Sector code
- `sector_name`: Sector name
- `sector_type`: 'industry' or 'concept'
- `main_net_inflow`: Main fund net inflow
- `pct_change`: Price change percentage
- `leading_stock`: Leading stock symbol
- `leading_stock_pct`: Leading stock price change

**Example:**
```python
df = get_sector_fund_flow("industry", start_date="2024-01-01")
```

### 1.3 get_main_fund_flow_rank()

Get main fund flow ranking by net inflow or rate.

**Parameters:**
- `date` (str): Date in YYYY-MM-DD format
- `indicator` (Literal["net_inflow", "net_inflow_rate"]): Ranking indicator
- `source` (str): Data source

**Returns:** DataFrame with ranking data

**Example:**
```python
df = get_main_fund_flow_rank("2024-12-31", indicator="net_inflow")
```

### 1.4 get_industry_list() / get_concept_list()

Get list of industry or concept sectors.

**Returns:** DataFrame with sector codes, names, and constituent counts

### 1.5 get_industry_constituents() / get_concept_constituents()

Get constituent stocks of a sector.

**Parameters:**
- `industry_code` or `concept_code` (str): Sector code

**Returns:** DataFrame with stock symbols, names, and weights

---


## 2. Disclosure Module

**Import**: `from akshare_one.modules.disclosure import *`

### 2.1 get_disclosure_news()

Get company disclosure and announcement data.

**Parameters:**
- `symbol` (str | None): Stock symbol, None for all stocks
- `start_date` (str): Start date
- `end_date` (str): End date
- `category` (Literal["all", "dividend", "repurchase", "st", "major_event"]): Category filter
- `source` (str): Data source

**Returns:** DataFrame with columns:
- `date`: Announcement date
- `symbol`: Stock symbol
- `title`: Announcement title
- `category`: Announcement category
- `content`: Announcement summary
- `url`: Announcement URL

**Example:**
```python
# Get all announcements for a stock
df = get_disclosure_news("600000", start_date="2024-01-01", category="all")

# Get only dividend announcements
df = get_disclosure_news("600000", category="dividend")
```

### 2.2 get_dividend_data()

Get dividend distribution data.

**Returns:** DataFrame with columns:
- `symbol`: Stock symbol
- `fiscal_year`: Dividend fiscal year
- `dividend_per_share`: Dividend per share (元)
- `record_date`: Record date
- `ex_dividend_date`: Ex-dividend date
- `payment_date`: Payment date
- `dividend_ratio`: Dividend ratio (%)

**Example:**
```python
df = get_dividend_data("600000", start_date="2024-01-01")
```

### 2.3 get_repurchase_data()

Get stock buyback progress data.

**Returns:** DataFrame with buyback amount, quantity, price range, and progress

### 2.4 get_st_delist_data()

Get ST/delisting risk warnings.

**Returns:** DataFrame with ST type, risk level, and announcement date

---

## 3. Northbound Capital Module

**Import**: `from akshare_one.modules.northbound import *`

### 3.1 get_northbound_flow()

Get northbound capital flow data (Shanghai/Shenzhen Connect).

**Parameters:**
- `start_date` (str): Start date
- `end_date` (str): End date
- `market` (Literal["sh", "sz", "all"]): Market selection
- `source` (str): Data source

**Returns:** DataFrame with columns:
- `date`: Date
- `market`: Market ('sh', 'sz', or 'all')
- `net_buy`: Net buy amount (亿元)
- `buy_amount`: Buy amount (亿元)
- `sell_amount`: Sell amount (亿元)
- `balance`: Balance (亿元)

**Example:**
```python
# Get all northbound flow
df = get_northbound_flow(start_date="2024-01-01", market="all")

# Get Shanghai market only
df = get_northbound_flow(start_date="2024-01-01", market="sh")
```

### 3.2 get_northbound_holdings()

Get northbound holdings details with historical tracking.

**Returns:** DataFrame with holdings shares, value, ratio, and changes

### 3.3 get_northbound_top_stocks()

Get top stocks by northbound capital holdings.

**Parameters:**
- `date` (str): Date
- `market` (Literal["sh", "sz", "all"]): Market
- `top_n` (int): Number of top stocks (default: 100)

**Example:**
```python
df = get_northbound_top_stocks("2024-12-31", market="all", top_n=50)
```

---


## 4. Macro Data Module

**Import**: `from akshare_one.modules.macro import *`

### 4.1 get_lpr_rate()

Get LPR (Loan Prime Rate) data.

**Returns:** DataFrame with columns:
- `date`: Date
- `lpr_1y`: 1-year LPR rate (%)
- `lpr_5y`: 5-year LPR rate (%)

**Example:**
```python
df = get_lpr_rate(start_date="2024-01-01")
```

### 4.2 get_pmi_index()

Get PMI (Purchasing Managers' Index) data.

**Parameters:**
- `pmi_type` (Literal["manufacturing", "non_manufacturing", "caixin"]): PMI type

**Returns:** DataFrame with PMI value, YoY, and MoM changes

### 4.3 get_cpi_data() / get_ppi_data()

Get CPI (Consumer Price Index) or PPI (Producer Price Index) data.

**Returns:** DataFrame with current value, YoY, MoM, and cumulative changes

### 4.4 get_m2_supply()

Get M2 money supply data.

**Returns:** DataFrame with M2 balance and YoY growth rate

### 4.5 get_shibor_rate()

Get Shibor (Shanghai Interbank Offered Rate) data.

**Returns:** DataFrame with rates for multiple terms (overnight, 1W, 2W, 1M, 3M, 6M, 9M, 1Y)

### 4.6 get_social_financing()

Get social financing scale data.

**Returns:** DataFrame with total social financing, YoY, MoM, and new RMB loans

**Example:**
```python
# Get multiple macro indicators
lpr = get_lpr_rate(start_date="2024-01-01")
pmi = get_pmi_index(start_date="2024-01-01", pmi_type="manufacturing")
cpi = get_cpi_data(start_date="2024-01-01")
```

---

## 5. Block Deal Module

**Import**: `from akshare_one.modules.blockdeal import *`

### 5.1 get_block_deal()

Get block trade details.

**Parameters:**
- `symbol` (str | None): Stock symbol, None for all stocks
- `start_date` (str): Start date
- `end_date` (str): End date

**Returns:** DataFrame with columns:
- `date`: Trade date
- `symbol`: Stock symbol
- `price`: Trade price (元)
- `volume`: Trade volume (shares)
- `amount`: Trade amount (元)
- `buyer_branch`: Buyer broker branch
- `seller_branch`: Seller broker branch
- `premium_rate`: Premium/discount rate (%)

**Example:**
```python
# Get block deals for a stock
df = get_block_deal("600000", start_date="2024-01-01")

# Get all block deals
df = get_block_deal(symbol=None, start_date="2024-01-01")
```

### 5.2 get_block_deal_summary()

Get block trade statistics.

**Parameters:**
- `group_by` (Literal["stock", "date", "broker"]): Grouping dimension

**Returns:** DataFrame with trade counts, total amount, and average premium rate

---


## 6. Dragon-Tiger List Module

**Import**: `from akshare_one.modules.lhb import *`

### 6.1 get_dragon_tiger_list()

Get dragon-tiger list data (stocks with unusual trading activity).

**Parameters:**
- `date` (str): Date
- `symbol` (str | None): Stock symbol, None for all stocks

**Returns:** DataFrame with date, symbol, reason for listing, buy/sell amounts, and broker details

**Example:**
```python
df = get_dragon_tiger_list("2024-12-31")
```

### 6.2 get_dragon_tiger_summary()

Get dragon-tiger list statistics.

**Parameters:**
- `group_by` (Literal["stock", "broker", "reason"]): Grouping dimension

### 6.3 get_dragon_tiger_broker_stats()

Get top broker statistics from dragon-tiger list.

**Parameters:**
- `top_n` (int): Number of top brokers (default: 50)

---

## 7. Limit Up/Down Module

**Import**: `from akshare_one.modules.limitup import *`

### 7.1 get_limit_up_pool()

Get limit-up pool data.

**Parameters:**
- `date` (str): Date

**Returns:** DataFrame with columns:
- `symbol`: Stock symbol
- `limit_up_time`: Time when limit-up occurred
- `open_count`: Number of times limit opened
- `seal_amount`: Seal order amount (元)
- `consecutive_days`: Consecutive limit-up days
- `reason`: Reason for limit-up

**Example:**
```python
df = get_limit_up_pool("2024-12-31")
```

### 7.2 get_limit_down_pool()

Get limit-down pool data.

### 7.3 get_limit_up_stats()

Get limit up/down statistics.

**Returns:** DataFrame with date, limit-up count, limit-down count, and broken board rate

---

## 8. Margin Trading Module

**Import**: `from akshare_one.modules.margin import *`

### 8.1 get_margin_data()

Get margin trading data (financing and securities lending).

**Parameters:**
- `symbol` (str | None): Stock symbol, None for all stocks
- `start_date` (str): Start date
- `end_date` (str): End date

**Returns:** DataFrame with columns:
- `date`: Date
- `symbol`: Stock symbol
- `financing_balance`: Financing balance (元)
- `securities_balance`: Securities lending balance (元)
- `financing_buy`: Financing buy amount (元)
- `securities_sell`: Securities sell volume (shares)

**Example:**
```python
df = get_margin_data("600000", start_date="2024-01-01")
```

### 8.2 get_margin_summary()

Get market-wide margin trading summary.

**Parameters:**
- `market` (Literal["sh", "sz", "all"]): Market selection

**Returns:** DataFrame with total financing and securities lending balances

---


## 9. Equity Pledge Module

**Import**: `from akshare_one.modules.pledge import *`

### 9.1 get_equity_pledge()

Get equity pledge data.

**Parameters:**
- `symbol` (str | None): Stock symbol, None for all stocks
- `start_date` (str): Start date
- `end_date` (str): End date

**Returns:** DataFrame with columns:
- `symbol`: Stock symbol
- `shareholder_name`: Shareholder name
- `pledge_quantity`: Pledged quantity (shares)
- `pledge_ratio`: Pledge ratio (%)
- `pledgee`: Pledgee institution
- `pledge_date`: Pledge date

**Example:**
```python
df = get_equity_pledge("600000", start_date="2024-01-01")
```

### 9.2 get_equity_pledge_ratio_rank()

Get stocks ranked by pledge ratio.

**Parameters:**
- `date` (str): Date
- `top_n` (int): Number of top stocks (default: 100)

**Returns:** DataFrame with ranking, symbol, pledge ratio, and pledge market value

---

## 10. Restricted Release Module

**Import**: `from akshare_one.modules.restricted import *`

### 10.1 get_restricted_release()

Get restricted share release data.

**Parameters:**
- `symbol` (str | None): Stock symbol, None for all stocks
- `start_date` (str): Start date
- `end_date` (str): End date

**Returns:** DataFrame with columns:
- `symbol`: Stock symbol
- `release_date`: Release date
- `release_quantity`: Release quantity (shares)
- `release_value`: Release market value (元)
- `release_type`: Release type
- `shareholder_name`: Shareholder name

**Example:**
```python
df = get_restricted_release("600000", start_date="2024-01-01")
```

### 10.2 get_restricted_release_calendar()

Get restricted share release calendar.

**Parameters:**
- `start_date` (str): Start date
- `end_date` (str): End date

**Returns:** DataFrame with date, number of stocks releasing, and total market value

---

## 11. Goodwill Module

**Import**: `from akshare_one.modules.goodwill import *`

### 11.1 get_goodwill_data()

Get goodwill balance and impairment data.

**Parameters:**
- `symbol` (str | None): Stock symbol, None for all stocks
- `start_date` (str): Start date
- `end_date` (str): End date

**Returns:** DataFrame with columns:
- `symbol`: Stock symbol
- `report_period`: Report period
- `goodwill_balance`: Goodwill balance (元)
- `goodwill_ratio`: Goodwill to net assets ratio (%)
- `goodwill_impairment`: Goodwill impairment (元)

**Example:**
```python
df = get_goodwill_data("600000", start_date="2024-01-01")
```

### 11.2 get_goodwill_impairment()

Get goodwill impairment expectations.

**Parameters:**
- `date` (str): Date

**Returns:** DataFrame with expected impairment amount and risk level

### 11.3 get_goodwill_by_industry()

Get industry-level goodwill statistics.

**Parameters:**
- `date` (str): Date

**Returns:** DataFrame with industry name, total goodwill, average ratio, and total impairment

---


## 12. ESG Rating Module

**Import**: `from akshare_one.modules.esg import *`

### 12.1 get_esg_rating()

Get ESG (Environmental, Social, Governance) ratings.

**Parameters:**
- `symbol` (str | None): Stock symbol, None for all stocks
- `start_date` (str): Start date
- `end_date` (str): End date

**Returns:** DataFrame with columns:
- `symbol`: Stock symbol
- `rating_date`: Rating date
- `esg_score`: Overall ESG score
- `e_score`: Environmental score
- `s_score`: Social score
- `g_score`: Governance score
- `rating_agency`: Rating agency

**Example:**
```python
df = get_esg_rating("600000", start_date="2024-01-01")
```

### 12.2 get_esg_rating_rank()

Get ESG rating rankings.

**Parameters:**
- `date` (str): Date
- `industry` (str | None): Industry filter, None for all industries
- `top_n` (int): Number of top stocks (default: 100)

**Returns:** DataFrame with ranking, symbol, ESG score, and industry ranking

**Example:**
```python
# Get top 50 ESG rated stocks
df = get_esg_rating_rank("2024-12-31", top_n=50)

# Get top ESG stocks in a specific industry
df = get_esg_rating_rank("2024-12-31", industry="银行", top_n=20)
```

---

## Error Handling

All interfaces use a consistent exception hierarchy:

- `InvalidParameterError`: Invalid input parameters (e.g., wrong date format, invalid symbol)
- `DataSourceUnavailableError`: Data source is unavailable or timeout
- `NoDataError`: No data available for the requested parameters
- `UpstreamChangedError`: Upstream data structure has changed

**Example:**
```python
from akshare_one.modules.exceptions import InvalidParameterError, NoDataError

try:
    df = get_stock_fund_flow("invalid_symbol", start_date="2024-01-01")
except InvalidParameterError as e:
    print(f"Parameter error: {e}")
except NoDataError as e:
    print(f"No data available: {e}")
```

---

## Data Quality Guarantees

All interfaces guarantee:

1. **JSON Compatibility**: No NaN, Infinity, or non-serializable values
2. **Date Format**: All dates in YYYY-MM-DD string format
3. **Symbol Format**: All stock symbols as 6-digit strings with leading zeros
4. **Empty Results**: Empty DataFrames preserve column structure
5. **Type Consistency**: Consistent data types across all rows

---

## Performance Considerations

- **Caching**: Consider implementing caching for frequently accessed data
- **Date Ranges**: Limit date ranges to improve response time
- **Batch Queries**: Use `symbol=None` for batch queries when available
- **Concurrent Requests**: All providers are stateless and support concurrent access

---

## Migration from AKShare

If migrating from raw AKShare, note these key differences:

1. **Unified Interface**: All functions follow consistent naming and parameter patterns
2. **Standardized Output**: All outputs are standardized DataFrames with English column names
3. **Better Error Handling**: Clear exceptions instead of silent failures
4. **JSON Ready**: All outputs can be directly serialized to JSON
5. **Type Safety**: Full type hints for better IDE support

**Example Migration:**
```python
# Old AKShare way
import akshare as ak
df = ak.stock_individual_fund_flow(stock="600000", market="sh")

# New akshare-one way
from akshare_one.modules.fundflow import get_stock_fund_flow
df = get_stock_fund_flow("600000", start_date="2024-01-01")
```

---

## Additional Resources

- **Full API Reference**: See individual module `__init__.py` files for complete docstrings
- **Examples**: Check `examples/` directory for usage examples
- **Tests**: See `tests/` directory for comprehensive test cases
- **GitHub**: https://github.com/zwldarren/akshare-one

---

*Last Updated: 2024*
