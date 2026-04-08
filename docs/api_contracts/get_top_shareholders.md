# API Contract: get_top_shareholders

## Overview

**API Function**: `get_top_shareholders`

**Purpose**: Get top shareholders information for a stock, including institution count and holdings.

**Module**: `akshare_one.modules.shareholder`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `institution_count` | float | - | Number of institutions holding | `150` |
| `holding_pct` | float | percent | Holdings percentage | `25.5` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `name` | string | - | Stock name | Most sources |
| `institution_change` | float | - | Change in institution count | Most sources |
| `holding_pct_change` | float | percent | Change in holdings percentage | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_institute_hold`):
- `证券代码` → `symbol`
- `证券简称` → `name`
- `机构数` → `institution_count`
- `机构数变化` → `institution_change`
- `持股比例` → `holding_pct`
- `持股比例增幅` → `holding_pct_change`

**Field Transformations**:
- Standard field names
- Percentage values kept as numeric

## Update Frequency

- **Quarterly**: Updated with quarterly reports
- Latest data from most recent report

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock symbol (6-digit) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_top_shareholders

# Get top shareholders for a stock
df = get_top_shareholders(symbol="600000")

# With column filtering
df = get_top_shareholders(
    symbol="600000",
    columns=['symbol', 'institution_count', 'holding_pct']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name  institution_count  institution_change  holding_pct  holding_pct_change
0  600000  浦发银行              150.0                10.0         25.5                 2.3
```

## Validation Rules

1. **Required Fields**: `symbol`, `institution_count`, `holding_pct`
2. **Type Validation**:
   - `institution_count`: float, positive
   - `holding_pct`: float, 0-100 range
3. **Value Ranges**:
   - institution_count >= 0
   - holding_pct between 0 and 100

## Error Handling

- **Empty DataFrame**: Invalid symbol or API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_shareholder_changes`: Get shareholder change records
- `get_institution_holdings`: Get detailed institution holdings

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestShareholderContract`

## Notes

- Focuses on institutional shareholders
- Institution count shows popularity among funds
- API may be unstable for some symbols
- Useful for tracking institutional investor interest