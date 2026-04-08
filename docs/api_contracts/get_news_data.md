# API Contract: get_news_data

## Overview

**API Function**: `get_news_data`

**Purpose**: 获取个股或市场新闻数据

**Module**: `src.akshare_one.modules.news`

**Data Sources**: eastmoney, sina

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `keyword` | string | - | 关键词/标签 | '东方财富' |
| `title` | string | - | 新闻标题 | '东方财富发布年报' |
| `content` | string | - | 新闻内容摘要 | '东方财富发布2024年年报...' |
| `publish_time` | datetime | - | 发布时间 | '2024-03-15 09:30:00' |
| `source` | string | - | 文章来源 | '东方财富' |
| `url` | string | - | 新闻链接URL | 'https://news.eastmoney.com/...' |

## Optional Fields

无额外可选字段。

## Data Source Mapping

### Source: `eastmoney`

**Original Fields**:
- 字段名称由 akshare API 直接返回
- 使用 standardize_and_filter 进行标准化处理

**Field Transformations**:
- 自动应用 FIELD_EQUIVALENTS 映射
- 时间格式标准化为 ISO 8601

## Update Frequency

- **Realtime**: 实时更新，反映最新新闻动态
- **Historical**: 提供历史新闻数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | 股票代码，None时返回市场新闻 |
| `source` | string | no | 'eastmoney' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_news_data

# Get stock-specific news
df = get_news_data(symbol="300059")

# With filtering
df = get_news_data(
    symbol="300059",
    columns=['title', 'publish_time', 'source']
)
```

## Example Response

```python
     keyword     title          content    publish_time     source        url
0  东方财富  东方财富发布年报  东方财富发布2024年年报...  2024-03-15 09:30  东方财富  https://...
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `title`: 非空字符串
   - `url`: 有效URL格式
3. **Consistency Rules**:
   - `publish_time` 为有效日期时间

## Error Handling

- **Empty DataFrame**: 无新闻时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_disclosure_news`: 获取公告披露新闻
- `get_basic_info`: 获取股票基础信息

## Testing

Contract tests for this API are located in:
- `tests/test_api_field_contracts.py::TestNewsDataContract`

## Notes

- 新闻内容可能为摘要而非全文
- 来源字段表示新闻发布平台，不是数据源