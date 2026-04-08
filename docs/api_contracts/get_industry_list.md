# API Contract: get_industry_list

## Overview

**API Function**: `get_industry_list`

**Purpose**: Get list of industry classifications (行业分类).

**Module**: `akshare_one.modules.industry`

**Data Sources**: `eastmoney`, `sw` (申万)

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `industry_code` | string | - | Industry classification code | `801010` |
| `industry_name` | string | - | Industry classification name | `农林牧渔` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `level` | string | - | Classification level (一级/二级/三级) | Some sources |
| `stock_count` | float | - | Number of stocks in industry | Most sources |
| `change_pct` | float | percent | Industry index change % | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare industry list API):
- `行业代码` → `industry_code`
- `行业名称` → `industry_name`
- `成分股数量` → `stock_count`
- `涨跌幅` → `change_pct`

### Source: `sw` (申万)

**Original Fields**:
- 申万行业分类标准字段
- 一级/二级/三级分类

**Field Transformations**:
- Standard field names
- Code format varies by source

## Update Frequency

- **Daily**: Updated with market data
- Industry classification relatively stable

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source ('eastmoney', 'sw') |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_industry_list

# Get industry list (eastmoney)
df = get_industry_list()

# Get SW industry classification
df = get_industry_list(source="sw")

# With column filtering
df = get_industry_list(
    columns=['industry_code', 'industry_name', 'stock_count']
)
```

## Example Response

```python
# Example DataFrame structure
  industry_code industry_name  stock_count  change_pct
0        801010     农林牧渔          30.0         1.5
1        801020     采掘行业          25.0         2.0
```

## Validation Rules

1. **Required Fields**: `industry_code`, `industry_name`
2. **Type Validation**:
   - `industry_code`: string
   - `stock_count`: float, positive

## Error Handling

- **Empty DataFrame**: API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_industry_stocks`: Get stocks in an industry

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestIndustryContract`

## Notes

- SW classification widely used in China
- Three levels: 一级, 二级, 三级
- Industry classification more stable than concepts
- Useful for sector rotation analysis
- Compare performance across industries