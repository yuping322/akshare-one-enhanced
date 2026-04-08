# API Contract: get_stock_sentiment

## Overview

**API Function**: `get_stock_sentiment`

**Purpose**: Get stock sentiment data including comments and scores reflecting investor sentiment.

**Module**: `akshare_one.modules.sentiment`

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
| `comment_count` | float | - | Number of comments | Most sources |
| `sentiment_score` | float | - | Sentiment score (positive/negative) | Most sources |
| `bullish_count` | float | - | Bullish comment count | Some sources |
| `bearish_count` | float | - | Bearish comment count | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare stock comment API):
- `代码` → `symbol`
- `名称` → `name`
- `评论数` → `comment_count`
- `评分` → `sentiment_score`
- `看多数` → `bullish_count`
- `看空数` → `bearish_count`

**Field Transformations**:
- Standard field names
- Sentiment score normalized

## Update Frequency

- **Realtime**: Updated continuously
- Reflects current investor sentiment

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_stock_sentiment

# Get stock sentiment data
df = get_stock_sentiment()

# With column filtering
df = get_stock_sentiment(
    columns=['symbol', 'name', 'sentiment_score', 'comment_count']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol     name  comment_count  sentiment_score  bullish_count  bearish_count
0  600000  浦发银行         10000.0              7.5         6000.0         4000.0
```

## Validation Rules

1. **Required Fields**: `symbol`, `name`
2. **Type Validation**:
   - Counts: float, positive
   - Sentiment score: float, typically 0-10 range

## Error Handling

- **Empty DataFrame**: API unavailable
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_hot_rank`: Get hot stock ranking

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestSentimentContract`

## Notes

- Sentiment reflects investor psychology
- High comment count shows active discussion
- Compare bullish vs bearish counts
- Sentiment may not predict actual performance
- Use as supplementary information, not sole indicator