# API Contract: get_institution_holdings

## Overview

**API Function**: `get_institution_holdings`

**Purpose**: Get institution holdings details for a stock, including holdings percentage of total and float shares.

**Module**: `akshare_one.modules.shareholder`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `institution_count` | float | - | Number of institutions | `150` |
| `holding_pct` | float | percent | Holdings percentage of total shares | `25.5` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `name` | string | - | Stock name | Most sources |
| `float_holding_pct` | float | percent | Holdings percentage of float shares | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare `stock_institute_hold`):
- `证券代码` → `symbol`
- `证券简称` → `name`
- `机构数` → `institution_count`
- `持股比例` → `holding_pct`
- `占流通股比例` → `float_holding_pct`

**Field Transformations**:
- Standard field names
- Percentages as numeric values

## Update Frequency

- **Quarterly**: Updated with quarterly reports
- Reflects latest institutional holdings

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock symbol (6-digit) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_institution_holdings

# Get institution holdings for a stock
df = get_institution_holdings(symbol="600000")

# With column filtering
df = get_institution_holdings(
    symbol="600000",
    columns=['symbol', 'institution_count', 'holding_pct', 'float_holding_pct']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name  institution_count  holding_pct  float_holding_pct
0  600000  浦发银行              150.0         25.5               35.8
```

## Validation Rules

1. **Required Fields**: `symbol`, `institution_count`, `holding_pct`
2. **Type Validation**:
   - `institution_count`: float, positive
   - `holding_pct`: float, 0-100
   - `float_holding_pct`: float, 0-100
3. **Value Ranges**:
   - All percentages between 0 and 100

## Error Handling

- **Empty DataFrame**: Invalid symbol or no data
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_top_shareholders`: Get top shareholders summary
- `get_shareholder_changes`: Get shareholder change records

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestShareholderContract`

## Notes

- holding_pct = percentage of total shares
- float_holding_pct = percentage of float (流通股) shares
- Useful for analyzing institutional ownership
- High institutional holdings may indicate quality