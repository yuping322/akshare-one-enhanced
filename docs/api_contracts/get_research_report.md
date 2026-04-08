# API Contract: get_research_report

## Overview

**API Function**: `get_research_report`

**Purpose**: Get research reports (研报) for a specific stock from securities analysts.

**Module**: `akshare_one.modules.analyst`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `title` | string | - | Report title | `浦发银行2023年报点评` |
| `broker` | string | - | Broker/securities firm | `中信证券` |
| `publish_date` | datetime | - | Publication date | `2024-01-15` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `analyst_name` | string | - | Analyst name | Most sources |
| `rating` | string | - | Stock rating (买入/增持/中性等) | Most sources |
| `target_price` | float | yuan | Target price | Most sources |
| `summary` | string | - | Report summary/content | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare research report API):
- `股票代码` → `symbol`
- `标题` → `title`
- `机构` → `broker`
- `发布日期` → `publish_date`
- `分析师` → `analyst_name`
- `评级` → `rating`
- `目标价` → `target_price`

**Field Transformations**:
- publish_date converted to datetime
- Standard field names

## Update Frequency

- **Daily**: New reports added continuously
- Historical reports available

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock symbol (6-digit) |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_research_report

# Get research reports for a stock
df = get_research_report(symbol="600000")

# With column filtering
df = get_research_report(
    symbol="600000",
    columns=['symbol', 'title', 'broker', 'rating', 'target_price']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol              title      broker analyst_name rating  target_price  publish_date
0  600000  浦发银行2023年报点评      中信证券      张三      买入           15.0   2024-01-15
```

## Validation Rules

1. **Required Fields**: `symbol`, `title`, `broker`, `publish_date`
2. **Type Validation**:
   - `publish_date`: datetime
   - `target_price`: float, positive

## Error Handling

- **Empty DataFrame**: No reports for symbol
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_analyst_rank`: Get analyst rankings

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestAnalystContract`

## Notes

- Common ratings: 买入, 增持, 中性, 减持, 卖出
- Target price may be None for some reports
- Check analyst ranking before relying on reports
- Reports provide detailed analysis and recommendations