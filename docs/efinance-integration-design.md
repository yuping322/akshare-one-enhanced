# Efinance Integration Design Document

## Overview

This document describes the design for integrating efinance library interfaces into akshare-one-enhanced project. Efinance is a Python library for obtaining stock, fund, bond, and futures data.

## Module Structure

Efinance provides four main data modules:

1. **Stock Module** - Stock market data
2. **Fund Module** - Fund data
3. **Bond Module** - Bond data (mainly convertible bonds)
4. **Futures Module** - Futures market data

## Interface Catalog

### Stock Module (`efinance.stock`)

| Interface | Description | Parameters | Return Type |
|-----------|-------------|------------|-------------|
| `get_quote_history` | Historical K-line data | stock_codes, beg, end, klt, fqt | DataFrame |
| `get_realtime_quotes` | Real-time quotes | fs | DataFrame |
| `get_base_info` | Stock basic info | stock_codes | Series/DataFrame |
| `get_daily_billboard` | Dragon-Tiger list | start_date, end_date | DataFrame |
| `get_all_company_performance` | Quarterly performance | date | DataFrame |
| `get_history_bill` | Historical fund flow | stock_code | DataFrame |
| `get_today_bill` | Today's fund flow | stock_code | DataFrame |
| `get_deal_detail` | Transaction details | stock_code, max_count | DataFrame |
| `get_top10_stock_holder_info` | Top 10 shareholders | stock_code, top | DataFrame |
| `get_belong_board` | Board membership | stock_code | DataFrame |
| `get_members` | Index members | index_code | DataFrame |
| `get_quote_snapshot` | Quote snapshot | stock_code | Series |
| `get_latest_quote` | Latest quote | stock_codes | DataFrame |
| `get_latest_ipo_info` | IPO info | - | DataFrame |
| `get_latest_holder_number` | Holder count | date | DataFrame |
| `get_all_report_dates` | Report dates | - | DataFrame |

### Fund Module (`efinance.fund`)

| Interface | Description | Parameters | Return Type |
|-----------|-------------|------------|-------------|
| `get_quote_history` | Historical net value | fund_code, pz | DataFrame |
| `get_quote_history_multi` | Multi-fund history | fund_codes, pz | Dict[DataFrame] |
| `get_base_info` | Fund basic info | fund_codes | Series/DataFrame |
| `get_invest_position` | Holdings info | fund_code, dates | DataFrame |
| `get_fund_codes` | Fund codes | ft | DataFrame |
| `get_fund_manager` | Fund manager | ft | DataFrame |
| `get_industry_distribution` | Industry distribution | fund_code, dates | DataFrame |
| `get_types_percentage` | Asset allocation | fund_code, dates | DataFrame |
| `get_period_change` | Period changes | fund_code | DataFrame |
| `get_public_dates` | Public dates | fund_code | List[str] |
| `get_realtime_increase_rate` | Real-time change | fund_codes | DataFrame |
| `get_pdf_reports` | PDF reports | fund_code, max_count, save_dir | None |

### Bond Module (`efinance.bond`)

| Interface | Description | Parameters | Return Type |
|-----------|-------------|------------|-------------|
| `get_quote_history` | Historical K-line | bond_codes, beg, end, klt | DataFrame |
| `get_realtime_quotes` | Real-time quotes | **kwargs | DataFrame |
| `get_all_base_info` | All bonds info | - | DataFrame |
| `get_base_info` | Bond basic info | bond_codes | DataFrame/Series |
| `get_deal_detail` | Transaction details | bond_code, max_count | DataFrame |
| `get_history_bill` | Historical flow | bond_code | DataFrame |
| `get_today_bill` | Today's flow | bond_code | DataFrame |

### Futures Module (`efinance.futures`)

| Interface | Description | Parameters | Return Type |
|-----------|-------------|------------|-------------|
| `get_quote_history` | Historical K-line | quote_ids, beg, end, klt | DataFrame |
| `get_realtime_quotes` | Real-time quotes | - | DataFrame |
| `get_futures_base_info` | Futures info | - | DataFrame |
| `get_deal_detail` | Transaction details | quote_id, max_count | DataFrame |

## Integration Architecture

### Wrapper Module Design

```python
# efinance_wrapper.py
import efinance as ef

class EfinanceWrapper:
    """Efinance API wrapper"""
    
    def __init__(self):
        self.stock = ef.stock
        self.fund = ef.fund
        self.bond = ef.bond
        self.futures = ef.futures
```

### Unified Interface Design

**Stock Data Interfaces:**
- `get_stock_history(code, start_date, end_date, freq='daily')` - Unified historical data
- `get_stock_realtime(code)` - Real-time quote
- `get_stock_info(code)` - Basic info

**Fund Data Interfaces:**
- `get_fund_history(code)` - Historical net value
- `get_fund_holdings(code)` - Holdings
- `get_fund_info(code)` - Basic info

**Bond Data Interfaces:**
- `get_bond_history(code)` - Historical data
- `get_bond_realtime()` - Real-time quotes
- `get_bond_info(code)` - Basic info

**Futures Data Interfaces:**
- `get_futures_history(code)` - Historical data
- `get_futures_realtime()` - Real-time quotes

## Parameter Specifications

### Time Format
- Date format: `YYYYMMDD` or `YYYY-MM-DD`
- Time frequency: 101=daily, 102=weekly, 103=monthly, 5=5min, 15=15min, etc.

### Code Format
- Stock: `600519`, `000001`, `AAPL`
- Fund: `161725`, `005827`
- Bond: `123111`, `110081`
- Futures: Use quote_id like `115.ZCM`

## Error Handling

```python
try:
    data = ef.stock.get_quote_history('600519')
except Exception as e:
    print(f"Error fetching data: {e}")
    return None
```

## Data Format

All interfaces return pandas DataFrame or Series, including:
- Price data: open, close, high, low
- Volume data: volume, turnover
- Derived data: amplitude, change_rate, change_amount, turnover_rate

## Usage Recommendations

1. **Rate Limiting**: Implement request throttling to avoid API blocking
2. **Error Handling**: Wrap calls with exception handling
3. **Data Validation**: Validate returned data before use
4. **Caching**: Cache frequently accessed data
5. **Async Support**: Consider async implementation for bulk queries

## Implementation Plan

1. Create wrapper module
2. Implement unified interfaces
3. Add error handling
4. Add caching mechanism
5. Create example scripts
6. Write tests