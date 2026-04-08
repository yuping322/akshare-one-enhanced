# API Contract: get_bond_realtime_data

## Overview

**API Function**: `get_bond_realtime_data`

**Purpose**: 获取可转债实时行情数据

**Module**: `src.akshare_one.modules.bond`

**Data Sources**: eastmoney

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `bond_code` | string | - | 债券代码 | '110001' |
| `bond_name` | string | - | 债券名称 | '招路转债' |
| `price` | float | yuan | 最新价 | 120.5 |
| `pct_change` | float | percent | 涨跌幅 | 0.5 |
| `change` | float | yuan | 涨跌额 | 0.6 |
| `volume` | float | hands | 成交量 | 5.0e3 |
| `amount` | float | yuan | 成交额 | 6.0e5 |
| `open` | float | yuan | 开盘价 | 120.0 |
| `high` | float | yuan | 最高价 | 121.0 |
| `low` | float | yuan | 最低价 | 119.5 |
| `prev_close` | float | yuan | 昨收价 | 119.9 |

## Optional Fields

- `turnover`: 换手率
- 其他债券特有字段

## Data Source Mapping

### Source: `eastmoney`

**Original Fields**:
- 使用 standardize_and_filter 自动映射
- 中文字段映射为英文标准字段

**Field Transformations**:
- 价格单位为元
- 成交量单位为手（1手=10张债券）

## Update Frequency

- **Realtime**: 实时更新（交易时间）
- **Delayed**: 非交易时间使用最后收盘数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | no | None | 债券代码，None时返回所有债券 |
| `source` | string | no | 'eastmoney' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_bond_realtime_data

# Get all bond realtime quotes
df = get_bond_realtime_data()

# Get specific bond
df = get_bond_realtime_data(symbol="110001")
```

## Example Response

```python
  bond_code  bond_name  price  pct_change  change  volume   amount
0   110001   招路转债  120.5      0.5      0.6   5.0e3   6.0e5
1   110002   招商转债  115.0      0.3      0.3   3.2e3   3.7e5
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `bond_code`: 6位数字字符串
   - 价格字段 > 0
   - 成交量 >= 0
3. **OHLCV Consistency**:
   - high >= low
   - 标准OHLCV规则

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_bond_hist_data`: 可转债历史数据
- `get_bond_list`: 可转债列表

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestBondRealtimeContract`

## Notes

- 可转债成交量单位为手（1手=10张债券，与股票不同）
- 价格通常高于100元（发行价通常为100元）
- symbol为None时返回所有可转债