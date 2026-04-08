# API Contract: get_analyst_rank

## Overview

**API Function**: `get_analyst_rank`

**Purpose**: Get analyst ranking based on recommendation accuracy and performance.

**Module**: `akshare_one.modules.analyst`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `rank` | float | - | Analyst ranking position | `1` |
| `analyst_name` | string | - | Analyst name | `张三` |
| `broker` | string | - | Broker/securities firm name | `中信证券` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `accuracy_rate` | float | percent | Recommendation accuracy rate | Most sources |
| `total_recommendations` | float | - | Total recommendations count | Most sources |
| `profit_rate` | float | percent | Average profit rate | Most sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare analyst ranking API):
- `排名` → `rank`
- `分析师` → `analyst_name`
- `机构` → `broker`
- `准确率` → `accuracy_rate`
- `推荐次数` → `total_recommendations`
- `盈利率` → `profit_rate`

**Field Transformations**:
- Standard field names
- Percentages as numeric values

## Update Frequency

- **Periodic**: Updated regularly (monthly/quarterly)
- Historical rankings available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_analyst_rank

# Get analyst rankings
df = get_analyst_rank()

# With column filtering
df = get_analyst_rank(
    columns=['rank', 'analyst_name', 'broker', 'accuracy_rate']
)
```

## Example Response

```python
# Example DataFrame structure
   rank analyst_name      broker  accuracy_rate  total_recommendations  profit_rate
0   1.0        张三      中信证券          85.0                   100.0         15.0
1   2.0        李四      华泰证券          80.0                    90.0         12.0
```

## Validation Rules

1. **Required Fields**: `rank`, `analyst_name`, `broker`
2. **Type Validation**:
   - `rank`: float, positive
   - Percentage fields: float, 0-100

## Error Handling

- **Empty DataFrame**: API unavailable or no data
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_research_report`: Get research reports for stocks

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestAnalystContract`

## Notes

- Rankings based on historical recommendation accuracy
- Useful for evaluating analyst quality
- Consider analyst reputation when reading reports
- Rankings may change over time