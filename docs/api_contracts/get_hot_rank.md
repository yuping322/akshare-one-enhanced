# API Contract: get_hot_rank

## Overview

**API Function**: `get_hot_rank`

**Purpose**: Get hot stock ranking based on market attention and trading activity.

**Module**: `akshare_one.modules.sentiment`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `rank` | float | - | Hot ranking position | `1` |
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `name` | string | - | Stock name | `浦发银行` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `click_count` | float | - | Click/view count | Most sources |
| `change_pct` | float | percent | Price change percentage | Most sources |
| `volume` | float | hands | Trading volume | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare hot stock API):
- `排名` → `rank`
- `代码` → `symbol`
- `名称` → `name`
- `点击量` → `click_count`
- `涨跌幅` → `change_pct`
- `成交量` → `volume`

**Field Transformations**:
- Standard field names
- Percentages as numeric values

## Update Frequency

- **Realtime**: Updated continuously during trading hours
- Reflects current market attention

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_hot_rank

# Get hot stock ranking
df = get_hot_rank()

# With column filtering
df = get_hot_rank(
    columns=['rank', 'symbol', 'name', 'change_pct']
)
```

## Example Response

```python
# Example DataFrame structure
   rank  symbol     name  click_count  change_pct      volume
0   1.0  600000  浦发银行     5000000         5.0   1000000.0
1   2.0  000001  平安银行     3000000         3.0    800000.0
```

## Validation Rules

1. **Required Fields**: `rank`, `symbol`, `name`
2. **Type Validation**:
   - `rank`: float, positive
   - `symbol`: string, 6-digit

## Error Handling

- **Empty DataFrame**: API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_stock_sentiment`: Get stock sentiment scores

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestSentimentContract`

## Notes

- Hot stocks reflect high market attention
- May indicate trending topics or news
- Click count shows investor interest
- Useful for identifying momentum stocks
- High attention may not mean good investment