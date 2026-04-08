# API Contract: get_inner_trade_data

## Overview

**API Function**: `get_inner_trade_data`

**Purpose**: 获取内部交易数据（高管交易）

**Module**: `src.akshare_one.modules.insider`

**Data Sources**: xueqiu

## Minimum Field Set (Required Fields)

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | 股票代码 | '600000' |
| `name` | string | - | 股票名称 | '浦发银行' |
| `insider_name` | string | - | 内部人姓名 | '张三' |
| `insider_title` | string | - | 内部人职位 | '董事长' |
| `trade_date` | datetime | - | 交易日期 | '2024-03-15' |
| `trade_type` | string | - | 交易类型 | 'buy' |
| `trade_shares` | float | shares | 交易股数 | 1.0e4 |
| `trade_price` | float | yuan | 交易价格 | 10.25 |
| `trade_amount` | float | yuan | 交易金额 | 1.025e5 |

## Optional Fields

- 其他交易相关字段
- 变动后持股数量

## Data Source Mapping

### Source: `xueqiu`

**Original Fields**:
- 使用 standardize_and_filter 自动映射
- 数据来自雪球网站

**Field Transformations**:
- 自动标准化字段名称
- 交易类型标准化为buy/sell

## Update Frequency

- **Daily**: 每日更新
- **Historical**: 提供历史内部交易数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | 股票代码 |
| `source` | string | no | 'xueqiu' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_inner_trade_data

# Get insider trading data
df = get_inner_trade_data(symbol="600000")
```

## Example Response

```python
  symbol    name insider_name insider_title  trade_date trade_type  trade_shares
0  600000  浦发银行        张三         董事长  2024-03-15      buy        1.0e4
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `trade_type`: 'buy' 或 'sell'
   - `trade_shares` > 0
   - `trade_price` > 0
   - `trade_amount` > 0
3. **Consistency Rules**:
   - trade_amount = trade_shares * trade_price

## Error Handling

- **Empty DataFrame**: 无数据时返回空DataFrame
- **Exception Handling**: 捕获并记录错误

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_shareholder_changes`: 股东变动数据
- `get_top_shareholders`: 十大股东
- `get_basic_info`: 股票基础信息

## Testing

Contract tests located in:
- `tests/test_api_field_contracts.py::TestInnerTradeContract`

## Notes

- 内部交易指高管、董事等人员的交易
- 数据源为雪球（xueqiu）
- 交易金额单位为元
- trade_type: buy（买入）, sell（卖出）