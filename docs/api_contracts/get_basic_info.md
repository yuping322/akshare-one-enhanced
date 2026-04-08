# API Contract: get_basic_info

## Overview

**API Function**: `get_basic_info`

**Purpose**: 获取股票基础信息，包括市值、股本、行业分类等

**Module**: `src.akshare_one.modules.info`

**Data Sources**: eastmoney

## Minimum Field Set (Required Fields)

The following fields MUST be present in every API response.

| Field Name | Type | Unit | Description | Example |
|------------|------|------|-------------|---------|
| `symbol` | string | - | 股票代码 | '600000' |
| `name` | string | - | 股票简称 | '浦发银行' |
| `price` | float | yuan | 最新价格 | 10.25 |
| `total_shares` | float | shares | 总股本 | 2.93e9 |
| `float_shares` | float | shares | 流通股 | 2.93e9 |
| `total_market_cap` | float | yuan | 总市值 | 3.0e10 |
| `float_market_cap` | float | yuan | 流通市值 | 3.0e10 |
| `industry` | string | - | 行业分类 | '银行' |
| `listing_date` | datetime | - | 上市日期 | '1999-11-10' |

## Optional Fields

无可选字段，上述为完整字段集。

## Data Source Mapping

### Source: `eastmoney`

**Original Fields** (from upstream API):
- `最新` → `price`
- `股票代码` → `symbol`
- `股票简称` → `name`
- `总股本` → `total_shares`
- `流通股` → `float_shares`
- `总市值` → `total_market_cap`
- `流通市值` → `float_market_cap`
- `行业` → `industry`
- `上市时间` → `listing_date`

**Field Transformations**:
- 无特殊转换，直接映射

## Update Frequency

- **Daily**: 每日更新（市值、股本数据）
- **Static**: 行业分类、上市日期为静态数据

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | yes | - | 股票代码（6位数字） |
| `source` | string | no | 'eastmoney' | 数据源 |
| `columns` | list | no | None | 保留的列 |
| `row_filter` | dict | no | None | 行过滤规则 |

## Example Usage

```python
from akshare_one import get_basic_info

# Basic usage
df = get_basic_info(symbol="600000")

# With column filtering
df = get_basic_info(
    symbol="600000",
    columns=['symbol', 'name', 'industry', 'listing_date']
)
```

## Example Response

```python
   symbol    name  price  total_shares  float_shares  ...
0  600000  浦发银行  10.25      2.93e9        2.93e9  ...
```

## Validation Rules

1. **Required Fields**: 所有字段必须存在
2. **Type Validation**:
   - `symbol`: 6位数字字符串
   - `price`: 正数
   - `total_shares`: 正数
   - `total_market_cap`: 正数
3. **Consistency Rules**:
   - `float_shares` <= `total_shares`
   - `float_market_cap` <= `total_market_cap`

## Error Handling

- **Empty DataFrame**: 股票代码不存在时返回空DataFrame
- **Exception Handling**: 抛出 ValueError

## Contract Stability

**Stability Level**: `stable`

**Version**: `1.0`

## Related APIs

- `get_realtime_data`: 获取实时行情数据
- `get_stock_valuation`: 获取估值数据
- `get_financial_metrics`: 获取财务指标

## Testing

Contract tests for this API are located in:
- `tests/test_api_field_contracts.py::TestBasicInfoContract`

## Notes

- 市值单位为元（yuan），股本单位为股（shares）
- 行业分类使用东方财富的标准行业分类体系