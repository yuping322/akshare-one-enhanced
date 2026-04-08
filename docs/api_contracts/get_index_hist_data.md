# API Contract: get_index_hist_data

## Overview

**API Function**: `get_index_hist_data`

**Purpose**: 获取指数历史数据

**Module**: `src.akshare_one.modules.index`

**Data Sources**: eastmoney, sina, lixinger

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `date` | datetime | - | 日期 | '2024-03-15' |
| `symbol` | string | - | 指数代码 | '000001' |
| `open` | float | yuan | 开盘点位 | 3100.5 |
| `high` | float | yuan | 最高点位 | 3120.8 |
| `low` | float | yuan | 最低点位 | 3095.2 |
| `close` | float | yuan | 收盘点位 | 3110.5 |
| `volume` | float | hands | 成交量 | 2.5e8 |
| `amount` | float | yuan | 成交额 | 1.8e12 |

## Optional Fields

- `pct_change`: 涨跌幅（百分比）
- `turnover_rate`: 换手率

## Data Source Mapping

### Source: `eastmoney`

**Original Fields**:
- 使用 standardize_and_filter 自动映射
- 中文字段映射为英文标准字段

**Field Transformations**:
- 自动添加 symbol 字段
- 成交额单位标准化

## Update Frequency

- **Daily**: 日线数据每日更新
- **Weekly**: 周线数据每周更新
- **Monthly**: 月线数据每月更新
- **Historical**: 提供完整历史数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | 指数代码 |
| `start_date` | string | no | '1970-01-01' | 开始日期 |
| `end_date` | string | no | '2030-12-31' | 结束日期 |
| `interval` | string | no | 'daily' | 时间间隔 ('daily', 'weekly', 'monthly') |
| `source` | string | no | 'eastmoney' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_index_hist_data

# Basic usage
df = get_index_hist_data(symbol="000001")

# With date range and interval
df = get_index_hist_data(
    symbol="000001",
    start_date="2024-01-01",
    end_date="2024-03-31",
    interval="weekly"
)
```

## Example Response

```python
         date  symbol     open     high      low    close    volume      amount
0  2024-03-15  000001  3100.5  3120.8  3095.2  3110.5  2.5e8    1.8e12
1  2024-03-14  000001  3090.0  3105.3  3088.5  3100.2  2.3e8    1.6e12
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `symbol`: 有效指数代码
   - 价格字段 > 0
3. **OHLCV Consistency**:
   - `high` >= `low`
   - `high` >= `open`, `high` >= `close`
   - `low` <= `open`, `low` <= `close`

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_index_realtime_data`: 指数实时数据
- `get_index_list`: 指数列表
- `get_index_constituents`: 指数成分股

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestIndexHistContract`

## Notes

- 指数点位数值较大，如上证指数3000点左右
- 成交额单位为元（可能数值很大）
- 支持日线、周线、月线数据