# API Contract: get_concept_stocks

## Overview

**API Function**: `get_concept_stocks`

**Purpose**: Get constituent stocks within a concept sector (概念板块).

**Module**: `akshare_one.modules.concept`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `浦发银行` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `concept_code` | string | - | Concept sector code | Most sources |
| `concept_name` | string | - | Concept sector name | Most sources |
| `change_pct` | float | percent | Stock price change % | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare concept stocks API):
- `代码` → `symbol`
- `名称` → `name`
- `板块代码` → `concept_code`
- `板块名称` → `concept_name`
- `涨跌幅` → `change_pct`

**Field Transformations**:
- Standard field names
- Symbol in 6-digit format

## Update Frequency

- **Daily**: Updated with market data
- Constituent list may change over time

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `concept` | string | yes | - | Concept name or code (e.g., '人工智能', 'BK0001') |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_concept_stocks

# Get stocks in AI concept
df = get_concept_stocks(concept="人工智能")

# Get stocks by concept code
df = get_concept_stocks(concept="BK0001")

# With column filtering
df = get_concept_stocks(
    concept="人工智能",
    columns=['symbol', 'name', 'change_pct']
)
```

## Example Response

```python
# Example DataFrame structure
  concept_code concept_name  symbol     name  change_pct
0      BK0001      人工智能  600000  浦发银行         2.5
1      BK0001      人工智能  000001  平安银行         1.8
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`
2. **Type Validation**:
   - `symbol`: string, 6-digit
   - `change_pct`: float

## Error Handling

- **Empty DataFrame**: Invalid concept name/code
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_concept_list`: Get list of all concepts

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestConceptContract`

## Notes

- Stocks may belong to multiple concepts
- Constituent list changes over time
- Use concept name OR concept code as parameter
- Useful for thematic portfolio construction
- Check multiple concepts for stock coverage