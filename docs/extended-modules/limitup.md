# 涨停池（LimitUpDown）

涨停池模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：实时  
**示例程序**：[examples/limitup_example.py](../../examples/limitup_example.py)

## 导入方式

```python
from akshare_one.modules.limitup import (
    get_limit_up_pool,
    get_limit_down_pool,
    get_limit_up_stats
)
```

## 接口列表

### get_limit_up_pool

获取涨停池数据。

**功能描述**：查询指定日期的涨停股票池数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 是 | - | 日期（YYYY-MM-DD格式） | "2024-01-15" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-15" |
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| close_price | float | 收盘价（元） | 12.50 |
| limit_up_time | str | 涨停时间 | "09:30:00" |
| open_count | int | 打开次数 | 0 |
| seal_amount | float | 封单金额（万元） | 50000.0 |
| consecutive_days | int | 连续涨停天数 | 1 |
| reason | str | 涨停原因 | "业绩预增" |
| turnover_rate | float | 换手率（%） | 2.5 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定日期无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.limitup import get_limit_up_pool

# 获取涨停池数据
df = get_limit_up_pool("2024-01-15")
print(df.head())
```

### get_limit_down_pool

获取跌停池数据。

**功能描述**：查询指定日期的跌停股票池数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 是 | - | 日期（YYYY-MM-DD格式） | "2024-01-15" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-15" |
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| close_price | float | 收盘价（元） | 11.25 |
| limit_down_time | str | 跌停时间 | "09:35:00" |
| open_count | int | 打开次数 | 1 |
| turnover_rate | float | 换手率（%） | 3.5 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定日期无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.limitup import get_limit_down_pool

# 获取跌停池数据
df = get_limit_down_pool("2024-01-15")
print(df.head())
```

### get_limit_up_stats

获取涨停统计。

**功能描述**：统计指定时间范围内的涨停和跌停数量。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 是 | - | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 是 | - | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-15" |
| limit_up_count | int | 涨停数量 | 50 |
| limit_down_count | int | 跌停数量 | 10 |
| broken_rate | float | 破板率（%） | 15.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.limitup import get_limit_up_stats

# 获取涨停统计数据
df = get_limit_up_stats("2024-01-01", "2024-01-31")
print(df.head())
```