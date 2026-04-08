# API Contract: get_disclosure_news

## Overview

**API Function**: `get_disclosure_news`

**Purpose**: Get corporate disclosure news and announcements.

**Module**: `akshare_one.modules.disclosure`

**Data Sources**: `eastmoney`

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | Stock symbol (6-digit) | `600000` |
| `title` | string | - | News/announcement title | `2023年年度报告` |
| `publish_date` | datetime | - | Publication date | `2024-01-15` |

## Optional Fields

| Field Name | Type | Unit | Description | Availability |
|------------|------|------|-------------|--------------|
| `category` | string | - | Announcement category | Most sources |
| `content` | string | - | Announcement content | Some sources |
| `url` | string | - | Link to full announcement | Some sources |

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from akshare disclosure news API):
- `股票代码` → `symbol`
- `公告标题` → `title`
- `公告日期` → `publish_date`
- `公告类型` → `category`
- `公告内容` → `content`

**Field Transformations**:
- Date converted to datetime
- Standard field names

## Update Frequency

- **Daily**: Updated continuously
- Real-time disclosure updates

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | Stock symbol (if None, returns all) |
| `start_date` | string | no | `1970-01-01` | Start date (YYYY-MM-DD) |
| `end_date` | string | no | `2030-12-31` | End date (YYYY-MM-DD) |
| `category` | string | no | `all` | Category filter ('all', 'dividend', 'repurchase', 'st', 'major_event') |
| `source` | string | no | `eastmoney` | Data source |
| `columns` | list | no | None | Column filter |
| `row_filter` | dict | no | None | Row filter |

## Example Usage

```python
from akshare_one import get_disclosure_news

# Get all disclosure news
df = get_disclosure_news()

# Get news for specific stock
df = get_disclosure_news(symbol="600000")

# Get dividend announcements
df = get_disclosure_news(
    category="dividend",
    start_date="2024-01-01"
)

# With column filtering
df = get_disclosure_news(
    symbol="600000",
    columns=['symbol', 'title', 'publish_date', 'category']
)
```

## Example Response

```python
# Example DataFrame structure
   symbol           title publish_date        category
0  600000    2023年年度报告   2024-01-15        年度报告
1  600000    分红派息公告   2024-01-10        分红
```

## Validation Rules

1. **Required Fields**: `symbol`, `title`, `publish_date`
2. **Type Validation**:
   - `publish_date`: datetime
   - `symbol`: string, 6-digit

## Error Handling

- **Empty DataFrame**: No news in period
- **Exception Handling**: API errors caught

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

**Breaking Changes**: None

## Related APIs

- `get_dividend_data`: Get dividend data
- `get_repurchase_data`: Get repurchase data

## Testing

Contract tests in:
- `tests/test_api_contract.py::TestDisclosureContract`

## Notes

- Categories: 年报, 半年报, 季报, 分红, 回购, ST, 重大事项
- Important for fundamental analysis
- Monitor announcements for material events
- Major events may affect stock price
- Check announcements before trading
- category parameter filters announcement type