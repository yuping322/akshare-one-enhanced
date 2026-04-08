# API Contract: get_industry_stocks

## Overview

**API Function**: `get_industry_stocks`

**Purpose**: Get constituent stocks within an industry classification.

**Module**: `akshare_one.modules.industry`

**Data Sources**: `eastmoney`, `sw` (申万)

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `浦发银行` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `industry_code` | string | - | Industry code | Most sources |
| `industry_name` | string | - | Industry name | Most sources |
| `change_pct` | float | percent | Stock price change % | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare industry stocks API):
- `代码` → `symbol`
- `名称` → `name`
- `行业代码` → `industry_code`
- `行业名称` → `industry_name`
- `涨跌幅` → `change_pct`

### Source: `sw` (申万)

**Original Fields**:
- 申万行业成分股字段
- JQ-style symbol format

**Field Transformations**:
- Standard field names
- Symbol in 6-digit format

## Update Frequency

- **Daily**: Updated with market data
- Constituent list may change quarterly

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `industry` | string | yes | - | Industry name or code |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_industry_stocks

# Get stocks in an industry
df = get_industry_stocks(industry="农林牧渔")

# Get stocks by industry code
df = get_industry_stocks(industry="801010")

# With column filtering
df = get_industry_stocks(
    industry="农林牧渔",
    columns=['symbol', 'name', 'change_pct']
)
```

## Example Response

```python
# Example DataFrame structure
  industry_code industry_name  symbol     name  change_pct
0        801010     农林牧渔  600000  浦发银行         2.5
1        801010     农林牧渔  000001  平安银行         1.8
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`
2. **Type Validation**:
   - `symbol`: string, 6-digit
   - `change_pct`: float

## Error Handling

- **Empty DataFrame**: Invalid industry name/code
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_industry_list`: Get list of all industries

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestIndustryContract`

## Notes

- Stocks assigned to one primary industry
- Classification may vary by source
- Use industry name OR code as parameter
- Useful for sector-focused analysis
- Compare stocks within same industry