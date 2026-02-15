# 北向资金（Northbound）

北向资金模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：实时  
**示例程序**：[examples/northbound_example.py](../../examples/northbound_example.py)

## 导入方式

```python
from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks
)
```

## 接口列表

### get_northbound_flow

获取北向资金流向数据。

**功能描述**：查询沪股通、深股通或全部北向资金的流向数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| market | Literal["sh", "sz", "all"] | 否 | "all" | 市场类型（sh=沪股通，sz=深股通，all=全部） | "all" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-15" |
| market | str | 市场类型 | "all" |
| net_buy | float | 净买入金额（亿元） | 50.5 |
| buy_amount | float | 买入金额（亿元） | 200.0 |
| sell_amount | float | 卖出金额（亿元） | 149.5 |
| balance | float | 余额（亿元） | 3500.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.northbound import get_northbound_flow

# 获取北向资金流向数据
df = get_northbound_flow(start_date="2024-01-01", end_date="2024-01-31", market="all")
print(df.head())
```

### get_northbound_holdings

获取北向资金持股明细。

**功能描述**：查询指定股票或全市场的北向资金持股变化。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str \| None | 否 | None | 股票代码（None表示全市场） | "600000" |
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期（YYYY-MM-DD） | "2024-01-15" |
| symbol | str | 股票代码 | "600000" |
| holdings_shares | float | 持股数量（股） | 100000000.0 |
| holdings_value | float | 持股市值（元） | 1200000000.0 |
| holdings_ratio | float | 持股比例（%） | 5.5 |
| holdings_change | float | 持股变化（股） | 1000000.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.northbound import get_northbound_holdings

# 获取浦发银行的北向持股数据
df = get_northbound_holdings("600000", start_date="2024-01-01", end_date="2024-01-31")
print(df.head())
```

### get_northbound_top_stocks

获取北向资金排名。

**功能描述**：查询指定日期北向资金持股排名前N的股票。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 是 | - | 日期（YYYY-MM-DD格式） | "2024-01-15" |
| market | Literal["sh", "sz", "all"] | 否 | "all" | 市场类型 | "all" |
| top_n | int | 否 | 100 | 返回前N名 | 50 |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| rank | int | 排名 | 1 |
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| net_buy | float | 净买入金额（元） | 50000000.0 |
| holdings_shares | float | 持股数量（股） | 100000000.0 |
| holdings_ratio | float | 持股比例（%） | 5.5 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定日期无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.northbound import get_northbound_top_stocks

# 获取北向资金持股排名前50的股票
df = get_northbound_top_stocks("2024-01-15", market="all", top_n=50)
print(df.head())
```