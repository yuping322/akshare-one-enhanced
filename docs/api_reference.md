# API Field Reference Manual

## Overview

This document provides a comprehensive reference for all API field schemas in the akshare-one library. Each API follows a strict contract defining minimum required fields, types, units, and validation rules.

## API Categories

### 1. Market Data APIs

#### Historical Data APIs

| API | Module | Required Fields | Data Sources | Doc Link |
|-----|--------|----------------|--------------|----------|
| `get_hist_data` | historical | `timestamp`, `open`, `high`, `low`, `close`, `volume` | eastmoney, eastmoney_direct, sina | [Contract](api_contracts/get_hist_data.md) |
| `get_etf_hist_data` | etf | `date`, `symbol`, `open`, `high`, `low`, `close`, `volume` | eastmoney, sina | [Contract](api_contracts/get_etf_hist_data.md) |
| `get_bond_hist_data` | bond | `date`, `symbol`, `open`, `high`, `low`, `close`, `volume` | eastmoney, jsl | [Contract](api_contracts/get_bond_hist_data.md) |
| `get_index_hist_data` | index | `date`, `symbol`, `open`, `high`, `low`, `close`, `volume` | eastmoney, sina | - |
| `get_futures_hist_data` | futures | `timestamp`, `symbol`, `contract`, `open`, `high`, `low`, `close`, `volume`, `open_interest` | sina | [Contract](api_contracts/get_futures_hist_data.md) |

#### Realtime Data APIs

| API | Module | Required Fields | Data Sources | Doc Link |
|-----|--------|----------------|--------------|----------|
| `get_realtime_data` | realtime | `symbol`, `price`, `timestamp`, `volume`, `amount` | eastmoney, eastmoney_direct, xueqiu | [Contract](api_contracts/get_realtime_data.md) |
| `get_etf_realtime_data` | etf | `symbol`, `price`, `timestamp`, `volume` | eastmoney | - |
| `get_bond_realtime_data` | bond | `symbol`, `price`, `timestamp`, `volume` | eastmoney | - |
| `get_index_realtime_data` | index | `symbol`, `price`, `timestamp` | eastmoney | - |

### 2. Fund Flow & Capital Flow APIs

| API | Module | Required Fields | Data Sources | Doc Link |
|-----|--------|----------------|--------------|----------|
| `get_stock_fund_flow` | fundflow | `date`, `symbol`, `main_net_inflow`, `main_net_inflow_ratio` | eastmoney | [Contract](api_contracts/get_fund_flow.md) |
| `get_sector_fund_flow` | fundflow | `date`, `sector`, `net_inflow` | eastmoney | - |
| `get_northbound_flow` | northbound | `date`, `northbound_net_buy`, `northbound_buy_amount`, `northbound_sell_amount` | eastmoney | [Contract](api_contracts/get_northbound_flow.md) |
| `get_northbound_holdings` | northbound | `date`, `symbol`, `holdings_shares`, `holdings_value` | eastmoney | - |

### 3. Dragon Tiger List APIs

| API | Module | Required Fields | Data Sources | Doc Link |
|-----|--------|----------------|--------------|----------|
| `get_dragon_tiger_list` | lhb | `date`, `symbol`, `name`, `close`, `pct_change`, `turnover`, `reason` | eastmoney | [Contract](api_contracts/get_dragon_tiger_list.md) |
| `get_dragon_tiger_summary` | lhb | `date`, `symbol`, `net_amount` | eastmoney | - |

### 4. Financial Data APIs

| API | Module | Required Fields | Data Sources | Doc Link |
|-----|--------|----------------|--------------|----------|
| `get_financial_metrics` | financial | `report_date`, `symbol` | eastmoney_direct, sina | [Contract](api_contracts/get_financial_metrics.md) |
| `get_balance_sheet` | financial | `report_date`, `symbol`, `total_assets`, `total_liabilities` | sina | - |
| `get_income_statement` | financial | `report_date`, `symbol`, `revenue`, `net_profit` | sina | - |
| `get_cash_flow` | financial | `report_date`, `symbol`, `operating_cash_flow` | sina | - |

### 5. List & Index APIs

| API | Module | Required Fields | Data Sources | Doc Link |
|-----|--------|----------------|--------------|----------|
| `get_index_list` | index | `symbol`, `name` | eastmoney, sina | [Contract](api_contracts/get_index_list.md) |
| `get_etf_list` | etf | `symbol`, `name` | eastmoney | - |
| `get_bond_list` | bond | `symbol`, `name` | eastmoney | - |

### 6. Options APIs

| API | Module | Required Fields | Data Sources | Doc Link |
|-----|--------|----------------|--------------|----------|
| `get_options_chain` | options | `symbol`, `underlying`, `option_type`, `strike`, `expiration` | sina | - |
| `get_options_realtime` | options | `symbol`, `price`, `volume`, `open_interest` | sina | - |

## Common Field Types

### Price Fields

| Field | Type | Unit | Description | Common APIs |
|-------|------|------|-------------|-------------|
| `open` | float | yuan | Opening price | Historical APIs |
| `high` | float | yuan | Highest price | Historical APIs |
| `low` | float | yuan | Lowest price | Historical APIs |
| `close` | float | yuan | Closing price | Historical APIs |
| `price` | float | yuan | Current/latest price | Realtime APIs |
| `prev_close` | float | yuan | Previous close | Realtime APIs |
| `settlement` | float | yuan | Settlement price | Futures APIs |

### Volume & Amount Fields

| Field | Type | Unit | Description | Common APIs |
|-------|------|------|-------------|-------------|
| `volume` | float | hands | Trading volume | All market APIs |
| `amount` | float | yuan | Trading amount | All market APIs |
| `open_interest` | float | hands | Open interest | Futures APIs |
| `turnover` | float | percent | Turnover rate | Dragon tiger, realtime |

### Change Fields

| Field | Type | Unit | Description | Common APIs |
|-------|------|------|-------------|-------------|
| `change` | float | yuan | Price change amount | Historical, realtime |
| `pct_change` | float | percent | Price change percentage | Historical, realtime |

### Capital Flow Fields

| Field | Type | Unit | Description | Common APIs |
|-------|------|------|-------------|-------------|
| `net_inflow` | float | yuan | Net capital inflow | Fund flow, northbound |
| `net_inflow_ratio` | float | percent | Net inflow ratio | Fund flow |
| `buy_amount` | float | yuan | Buy amount | Northbound, dragon tiger |
| `sell_amount` | float | yuan | Sell amount | Northbound, dragon tiger |

### Identity Fields

| Field | Type | Unit | Description | Common APIs |
|-------|------|------|-------------|-------------|
| `symbol` | string | - | Stock/ETF/Bond code | All APIs |
| `name` | string | - | Security name | List APIs, dragon tiger |
| `contract` | string | - | Futures contract code | Futures APIs |
| `underlying` | string | - | Underlying symbol | Options APIs |

### Time Fields

| Field | Type | Unit | Description | Common APIs |
|-------|------|------|-------------|-------------|
| `timestamp` | datetime | - | Trading timestamp | Historical (minute/hour) |
| `date` | datetime | - | Trading date | Historical (daily), fund flow |
| `report_date` | datetime | - | Financial report date | Financial APIs |

### Financial Statement Fields

| Field | Type | Unit | Description | Common APIs |
|-------|------|------|-------------|-------------|
| `total_revenue` | float | yuan | Total revenue | Financial metrics |
| `net_profit` | float | yuan | Net profit | Financial metrics |
| `total_assets` | float | yuan | Total assets | Balance sheet |
| `total_liabilities` | float | yuan | Total liabilities | Balance sheet |
| `operating_cash_flow` | float | yuan | Operating cash flow | Cash flow |

### Financial Ratios

| Field | Type | Unit | Description | Common APIs |
|-------|------|------|-------------|-------------|
| `roe` | float | percent | Return on equity | Financial metrics |
| `roa` | float | percent | Return on assets | Financial metrics |
| `debt_ratio` | float | percent | Debt ratio | Financial metrics |
| `current_ratio` | float | ratio | Current ratio | Financial metrics |
| `gross_margin` | float | percent | Gross margin | Financial metrics |
| `net_margin` | float | percent | Net margin | Financial metrics |

## Field Type Definitions

### Numeric Types

- `float`: Floating-point number (most financial/market data)
- `int`: Integer number (rankings, counts)

### String Types

- `symbol`: 6-digit security code (stocks, ETFs, bonds)
- `contract`: Futures contract code (YYMM format)
- `name`: Security name in Chinese
- `reason`: Listing reason text (dragon tiger)

### Date/Time Types

- `datetime`: ISO 8601 format (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `timestamp`: Unix timestamp or datetime string

### Boolean Types

- `boolean`: True/false values (rare in financial data)

## Unit Definitions

### Monetary Units

- `yuan`: Chinese Yuan (元) - base unit for all prices and amounts
- Note: All APIs standardized to yuan (not 亿元 or 万元)

### Volume Units

- `hands`: Trading hands (手)
  - Stocks/ETFs: 1 hand = 100 shares
  - Bonds: 1 hand = 10 bonds
  - Futures: varies by contract type

### Percentage Units

- `percent`: Percentage value (e.g., 10.5 means 10.5%)
- `ratio`: Ratio in 0-1 range (e.g., 0.105 means 10.5%)

## Field Validation Standards

### Price Validation

- All prices must be positive (> 0)
- OHLC consistency: high >= low, high >= open/close, low <= open/close
- Price change can be negative (price drop)

### Volume Validation

- Volume must be non-negative (>= 0)
- Amount must be non-negative (>= 0)
- Consistency: amount ≈ avg_price × volume × unit_multiplier

### Symbol Format

- Stocks: 6-digit codes (600xxx, 000xxx, 300xxx)
- ETFs: 6-digit codes (510xxx, 159xxx)
- Bonds: 6-digit codes (110xxx, 123xxx)
- Futures: Symbol + Contract (e.g., AU0 + 2406)

### Date Format

- YYYY-MM-DD for daily data
- YYYY-MM-DD HH:MM:SS for minute/hour data
- Report dates: YYYY-MM-DD (03-31, 06-30, 09-30, 12-31)

## Cross-Source Field Mapping

Many APIs support multiple data sources. Field names are standardized across sources:

| Standard Field | eastmoney Field | sina Field |
|----------------|-----------------|------------|
| `symbol` | `代码` | `代码` |
| `name` | `名称` | `名称` |
| `open` | `开盘` | `开盘价` |
| `close` | `收盘` | `收盘价` |
| `high` | `最高` | `最高价` |
| `low` | `最低` | `最低价` |
| `volume` | `成交量` | `成交量` |
| `amount` | `成交额` | `成交额` |

## Multi-Source APIs

Several APIs support multi-source automatic failover:

| Single-Source API | Multi-Source API | Default Sources |
|-------------------|------------------|-----------------|
| `get_hist_data` | `get_hist_data_multi_source` | eastmoney_direct, eastmoney, sina |
| `get_realtime_data` | `get_realtime_data_multi_source` | eastmoney_direct, eastmoney, xueqiu |
| `get_financial_metrics` | `get_financial_metrics_multi_source` | eastmoney_direct, sina |
| `get_northbound_flow` | `get_northbound_flow_multi_source` | eastmoney |
| `get_stock_fund_flow` | `get_stock_fund_flow_multi_source` | eastmoney |

## Field Filtering

All APIs support column filtering via the `columns` parameter:

```python
# Select specific fields
df = get_hist_data(symbol="600000", columns=['timestamp', 'close', 'volume'])

# Select key metrics only
df = get_financial_metrics(symbol="600000", columns=['report_date', 'net_profit', 'roe'])
```

## Row Filtering

All APIs support row filtering via the `row_filter` parameter:

```python
# Sort and take top N
df = get_realtime_data(row_filter={"sort_by": "pct_change", "top_n": 10})

# Filter by condition
df = get_hist_data(symbol="600000", row_filter={"query": "close > 10"})
```

## API Contract Tests

Contract tests verify field schema stability:

- Location: `tests/test_api_field_contracts.py`
- Run: `pytest tests/test_api_field_contracts.py -v`

Each API has contract tests for:
- Required field presence
- Field type validation
- Value range validation
- Field consistency rules

## Version History

- Version 1.0 (Current): Initial field contract definitions
- All APIs follow strict field naming conventions
- All monetary amounts standardized to yuan (元)

## References

- Field Naming Standards: [docs/field_naming_standards.md](field_naming_standards.md)
- Compatibility Contract: [docs/COMPATIBILITY_CONTRACT.md](COMPATIBILITY_CONTRACT.md)
- API Contract Tests: [tests/test_api_field_contracts.py](../tests/test_api_field_contracts.py)