# API Contract: get_index_realtime_data

## Overview

**API Function**: `get_index_realtime_data`

**Purpose**: 获取指数实时行情数据

**Module**: `src.akshare_one.modules.index`

**Data Sources**: eastmoney

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | 指数代码 | '000001' |
| `name` | string | - | 指数名称 | '上证指数' |
| `price` | float | yuan | 最新点位 | 3110.5 |
| `pct_change` | float | percent | 涨跌幅 | 0.5 |
| `change` | float | yuan | 涨跌点数 | 15.5 |
| `volume` | float | hands | 成交量 | 2.5e8 |
| `amount` | float | yuan | 成交额 | 1.8e12 |
| `open` | float | yuan | 开盘点位 | 3100.5 |
| `high` | float | yuan | 最高点位 | 3120.8 |
| `low` | float | yuan | 最低点位 | 3095.2 |
| `prev_close` | float | yuan | 昨日收盘 | 3095.0 |

## Optional Fields

- 其他指数相关字段（根据数据源）

## Data Source Mapping

### Source: `eastmoney`

**Original Fields**:
- 使用 standardize_and_filter 自动映射
- 原始字段为中文

**Field Transformations**:
- 涨跌点数而非涨跌额
- 自动标准化字段名称

## Update Frequency

- **Realtime**: 实时更新（交易时间）
- **Delayed**: 非交易时间使用最后收盘数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | 指数代码，None时返回所有指数 |
| `source` | string | no | 'eastmoney' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_index_realtime_data

# Get all indices realtime data
df = get_index_realtime_data()

# Get specific index
df = get_index_realtime_data(symbol="000001")
```

## Example Response

```python
   symbol      name    price  pct_change  change    volume      amount
0  000001   上证指数  3110.5        0.5    15.5    2.5e8    1.8e12
1  000300   沪深300  3900.5        0.6    23.5    1.8e8    1.2e12
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `symbol`: 有效指数代码
   - 价格字段 > 0
3. **OHLCV Consistency**:
   - `high` >= `low`
   - 标准OHLCV规则

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_index_hist_data`: 指数历史数据
- `get_index_list`: 指数列表
- `get_realtime_data`: 股票实时行情

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestIndexRealtimeContract`

## Notes

- 指数涨跌用点数表示，而非金额
- 成交额数值很大（万亿级别）
- symbol为None时返回所有指数