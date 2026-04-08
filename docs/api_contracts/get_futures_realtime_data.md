# API Contract: get_futures_realtime_data

## Overview

**API Function**: `get_futures_realtime_data`

**Purpose**: 获取期货实时行情数据

**Module**: `src.akshare_one.modules.futures`

**Data Sources**: sina

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | 期货代码 | 'AG' |
| `contract` | string | - | 合约代码 | 'AG2406' |
| `price` | float | yuan | 最新价 | 6250.0 |
| `change` | float | yuan | 涨跌额 | 15.0 |
| `pct_change` | float | percent | 涨跌幅 | 0.24 |
| `timestamp` | datetime | - | 时间戳 | '2024-03-15 14:30:00' |
| `volume` | float | hands | 成交量 | 1.2e5 |
| `open_interest` | float | hands | 持仓量 | 5.0e5 |
| `open` | float | yuan | 开盘价 | 6240.0 |
| `high` | float | yuan | 最高价 | 6260.0 |
| `low` | float | yuan | 最低价 | 6235.0 |
| `prev_settlement` | float | yuan | 昨结算 | 6235.0 |
| `settlement` | float | yuan | 最新结算价 | 6250.0 |

## Optional Fields

- 其他期货相关字段

## Data Source Mapping

### Source: `sina`

**Original Fields**:
- 自动映射中文字段到英文标准字段

**Field Transformations**:
- 价格单位标准化
- 成交量和持仓量单位为手
- 添加结算价字段

## Update Frequency

- **Realtime**: 实时更新（交易时间）
- **Delayed**: 非交易时间使用最后收盘数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | 期货代码，None时返回所有期货 |
| `source` | string | no | 'sina' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_futures_realtime_data

# Get all futures quotes
df = get_futures_realtime_data()

# Get specific futures symbol
df = get_futures_realtime_data(symbol="AG")
```

## Example Response

```python
  symbol contract    price  change  pct_change  volume  open_interest
0    AG  AG2406   6250.0    15.0      0.24     1.2e5      5.0e5
1    AU  AU2406   480.0     5.0      1.05     8.5e4      3.2e5
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - 价格字段 > 0
   - volume >= 0
   - open_interest >= 0
3. **OHLCV Consistency**:
   - high >= low
   - settlement >= 0

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_futures_hist_data`: 期货历史数据
- `get_futures_main_contracts`: 主力合约列表

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestFuturesRealtimeContract`

## Notes

- 成交量和持仓量单位为手
- 结算价是期货特有的重要指标
- symbol为None时返回所有期货品种