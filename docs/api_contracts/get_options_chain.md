# API Contract: get_options_chain

## Overview

**API Function**: `get_options_chain`

**Purpose**: 获取期权链数据

**Module**: `src.akshare_one.modules.options`

**Data Sources**: sina

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `underlying` | string | - | 标的代码 | '510300' |
| `symbol` | string | - | 期权代码 | '10004005' |
| `name` | string | - | 期权名称 | '300ETF购3月4000' |
| `option_type` | string | - | 期权类型 | 'call' |
| `strike` | float | yuan | 行权价 | 4.0 |
| `expiration` | datetime | - | 到期日 | '2024-03-27' |
| `price` | float | yuan | 最新价 | 0.15 |
| `change` | float | yuan | 涨跌额 | 0.02 |
| `pct_change` | float | percent | 涨跌幅 | 15.0 |
| `volume` | float | hands | 成交量 | 5000 |
| `open_interest` | float | hands | 持仓量 | 1.2e4 |
| `implied_volatility` | float | percent | 隐含波动率 | 20.5 |

## Optional Fields

- 其他期权相关字段

## Data Source Mapping

### Source: `sina`

**Original Fields**:
- 自动映射中文字段
- 通过 get_options_chain 方法获取

**Field Transformations**:
- 自动识别期权类型（认购call/认沽put）
- 提取行权价和到期日
- 计算隐含波动率

## Update Frequency

- **Realtime**: 实时更新（交易时间）
- **Delayed**: 非交易时间使用最后收盘数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `underlying_symbol` | string | yes | - | 标的代码（如'510300'） |
| `source` | string | no | 'sina' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_options_chain

# Get 300ETF options chain
df = get_options_chain(underlying_symbol="510300")
```

## Example Response

```python
  underlying  symbol       name option_type  strike  expiration  price
0    510300  10004005  300ETF购3月4000         call    4.0  2024-03-27   0.15
1    510300  10004006  300ETF沽3月4000          put    4.0  2024-03-27   0.08
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `option_type`: 'call' 或 'put'
   - `strike` > 0
   - `price` > 0
   - `volume` >= 0
   - `open_interest` >= 0
3. **Consistency Rules**:
   - 同一行权价应有call和put两个期权

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_options_realtime`: 期权实时行情
- `get_options_expirations`: 可用到期日列表
- `get_options_hist`: 期权历史数据

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestOptionsChainContract`

## Notes

- option_type: call（认购期权）, put（认沽期权）
- 行权价单位为元
- 隐含波动率单位为百分比
- 期权价格可能很小（如0.01-0.5元）