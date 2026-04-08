# API Contract: get_concept_list

## Overview

**API Function**: `get_concept_list`

**Purpose**: Get list of concept sectors (概念板块) in the market.

**Module**: `akshare_one.modules.concept`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `concept_code` | string | - | Concept sector code | `BK0001` |
| `concept_name` | string | - | Concept sector name | `人工智能` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `stock_count` | float | - | Number of stocks in concept | Most sources |
| `change_pct` | float | percent | Concept index change % | Most sources |
| `amount` | float | yuan | Total trading amount | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare concept list API):
- `板块代码` → `concept_code`
- `板块名称` → `concept_name`
- `成分股数量` → `stock_count`
- `涨跌幅` → `change_pct`
- `成交额` → `amount`

**Field Transformations**:
- Standard field names
- Code standardized to BK format

## Update Frequency

- **Daily**: Updated daily with market data
- Historical concept lists available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_concept_list

# Get concept sector list
df = get_concept_list()

# With column filtering
df = get_concept_list(
    columns=['concept_code', 'concept_name', 'stock_count', 'change_pct']
)
```

## Example Response

```python
# Example DataFrame structure
  concept_code concept_name  stock_count  change_pct        amount
0      BK0001      人工智能          50.0         2.5  5000000000.0
1      BK0002        新能源          40.0         1.8  3000000000.0
```

## Validation Rules

1. **Required Fields**: `concept_code`, `concept_name`
2. **Type Validation**:
   - `concept_code`: string, BK format
   - `stock_count`: float, positive

## Error Handling

- **Empty DataFrame**: API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_concept_stocks`: Get stocks in a concept sector

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestConceptContract`

## Notes

- Concepts represent thematic investment themes
- Examples: AI, EV, new energy, healthcare
- Concepts change over time (new ones added)
- Useful for thematic investing
- Check stock_count for concept maturity