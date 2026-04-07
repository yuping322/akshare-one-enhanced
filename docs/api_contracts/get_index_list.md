# API Contract: get_index_list

## Overview

**API Function**: `get_index_list`

**Purpose**: Get list of available indices categorized by market (CN, HK, US, Global).

**Module**: `akshare_one.modules.index`

**Data Sources**: `eastmoney`, `sina`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Index symbol (code) | `000001` |
| `name` | string | - | Index name | `上证指数` |

### Field Types

- `string`: Index symbol and name in Chinese
- Index symbols vary by market:
  - CN indices: 000xxx, 399xxx (Shanghai/Shenzhen)
  - HK indices: HSIxxx (Hang Seng)
  - US indices: Dow, Nasdaq, S&P (names)

## Optional Fields

The following fields MAY be present depending on the data source and category.

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `exchange` | string | - | Exchange name | Some sources |
| `type` | string | - | Index type (大类) | Some sources |
| `category` | string | - | Index category | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `index_stock_info`):
- `指数代码` → `symbol`
- `指数中文全称` → `name`
- `指数英文名称` → `name_en` (optional)
- `指数类型` → `type` (optional)

**Field Transformations**:
- Symbol standardized to 6-digit format where applicable
- Name in Chinese

### Source: `sina`

**Original Fields**:
- Field names standardized to eastmoney format

## Update Frequency

- **Static data**: Index list is relatively static
- **Daily updates**: Some sources update index list daily
- New indices added periodically

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `category` | string | no | `cn` | Index category: `cn`, `hk`, `us`, `global` |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter list |
| `row_filter` | dict | no | None | Row filter configuration |

## Example Usage

```python
from akshare_one import get_index_list

# Get Chinese indices (A-share)
df = get_index_list(category="cn")

# Get Hong Kong indices
df = get_index_list(category="hk")

# Get US indices
df = get_index_list(category="us")

# Get global indices
df = get_index_list(category="global")

# With column filtering
df = get_index_list(
    category="cn",
    columns=['symbol', 'name']
)
```

## Example Response

```python
# Example DataFrame structure (CN indices)
  symbol        name
0  000001      上证指数
1  000002      上证A股指数
2  000003      上证B股指数
3  000004      上证180指数
4  000005      上证50指数
...
0  399001      深证成指
1  399006      创业板指
...

# Example DataFrame structure (HK indices)
  symbol          name
0  HSI         恒生指数
1  HSCEI       恒生中国企业指数
...

# Example DataFrame structure (US indices)
  symbol              name
0  Dow Jones       道琼斯工业平均指数
1  Nasdaq          纳斯达克综合指数
2  S&P 500         标普500指数
```

## Validation Rules

1. **Required Fields**: All minimum fields MUST be present (`symbol`, `name`)
2. **Type Validation**:
   - `symbol`: string (format varies by category)
   - `name`: string (Chinese or English)

3. **Value Ranges**:
   - Non-empty strings for both fields
   - No null values for required fields

4. **Symbol Format**:
   - CN indices: 6-digit codes (000xxx, 399xxx)
   - HK/US/Global: varies (names or codes)

## Error Handling

- **Empty DataFrame**: Returned when no indices available for category
- **Exception Handling**: Network errors and API failures are caught and logged
- Category validation: Invalid category returns empty DataFrame

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_index_hist_data`: Get historical data for a specific index
- `get_index_realtime_data`: Get realtime index quotes
- `get_index_constituents`: Get constituent stocks of an index

## Testing

Contract tests for this API are located in:
- `tests/test_api_field_contracts.py::TestIndexListContract`

Test coverage includes:
- Required field presence
- Field type validation
- Non-empty value validation
- Category-specific validation

## Notes

- CN indices include major Shanghai and Shenzhen indices (上证、深证、创业板)
- Popular CN indices: 上证指数(000001), 深证成指(399001), 创业板指(399006)
- Index list may vary slightly between data sources
- Some indices may be discontinued or renamed over time