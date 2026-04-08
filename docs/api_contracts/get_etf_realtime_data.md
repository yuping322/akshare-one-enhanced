# API Contract: get_etf_realtime_data

## Overview

**API Function**: `get_etf_realtime_data`

**Purpose**: 获取所有ETF实时行情数据

**Module**: `src.akshare_one.modules.etf`

**Data Sources**: eastmoney

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | ETF代码 | '510300' |
| `name` | string | - | ETF名称 | '300ETF' |
| `price` | float | yuan | 最新价 | 4.25 |
| `pct_change` | float | percent | 涨跌幅 | 2.5 |
| `change` | float | yuan | 涨跌额 | 0.105 |
| `volume` | float | hands | 成交量 | 1.2e5 |
| `amount` | float | yuan | 成交额 | 5.1e7 |
| `open` | float | yuan | 开盘价 | 4.15 |
| `high` | float | yuan | 最高价 | 4.30 |
| `low` | float | yuan | 最低价 | 4.10 |
| `prev_close` | float | yuan | 昨收价 | 4.145 |
| `turnover` | float | percent | 换手率 | 0.5 |

## Optional Fields

无额外可选字段。

## Data Source Mapping

### Source: `eastmoney`

**Original Fields**:
- `代码` → `symbol`
- `名称` → `name`
- `最新价` → `price`
- `涨跌幅` → `pct_change`
- `涨跌额` → `change`
- `成交量` → `volume`
- `成交额` → `amount`
- `开盘价` → `open`
- `最高价` → `high`
- `最低价` → `low`
- `昨收` → `prev_close`
- `换手率` → `turnover`

**Field Transformations**:
- 价格单位为元（yuan）
- 成交量单位为手（1手=100份）
- 涨跌幅为百分比数值（如2.5表示2.5%）

## Update Frequency

- **Realtime**: 实时更新（交易时间）
- **Delayed**: 非交易时间使用最后收盘数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | no | 'eastmoney' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_etf_realtime_data

# Get all ETF realtime quotes
df = get_etf_realtime_data()

# Filter specific ETF
df = get_etf_realtime_data(
    columns=['symbol', 'name', 'price', 'pct_change'],
    row_filter={'query': 'symbol == "510300"'}
)
```

## Example Response

```python
   symbol    name  price  pct_change  change  volume    amount
0  510300  300ETF   4.25        2.5   0.105  1.2e5   5.1e7
1  510050   50ETF   2.50        1.8   0.044  8.5e4   2.1e7
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `symbol`: 6位数字字符串
   - 价格字段 > 0
   - 成交量 >= 0
3. **OHLCV Consistency**:
   - `high` >= `low`
   - `high` >= `open`, `high` >= `price`
   - `low` <= `open`, `low` <= `price`

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_etf_hist_data`: ETF历史数据
- `get_etf_list`: ETF列表
- `get_realtime_data`: 股票实时行情

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestETFRealtimeContract`

## Notes

- ETF成交量单位为手（1手=100份）
- 换手率单位为百分比（如0.5表示0.5%）
- 所有ETF代码为6位数字