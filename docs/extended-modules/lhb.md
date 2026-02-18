# 龙虎榜（DragonTigerLHB）

龙虎榜模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：T+1  
**示例程序**：[examples/lhb_example.py](../../examples/lhb_example.py)

## 导入方式

```python
from akshare_one.modules.lhb import (
    get_dragon_tiger_list,
    get_dragon_tiger_summary,
    get_dragon_tiger_broker_stats
)
```

## 接口列表

### get_dragon_tiger_list

获取龙虎榜数据。

**功能描述**：查询指定日期的龙虎榜上榜股票数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| date | str | 是 | - | 日期（YYYY-MM-DD格式） | "2024-01-15" |
| symbol | str \| None | 否 | None | 股票代码（None表示全部） | "600000" |
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
| pct_change | float | 涨跌幅（%） | 10.0 |
| reason | str | 上榜原因 | "涨幅偏离值达7%" |
| buy_amount | float | 龙虎榜买入金额（元） | 50000000.0 |
| sell_amount | float | 龙虎榜卖出金额（元） | 30000000.0 |
| net_amount | float | 龙虎榜净额（元） | 20000000.0 |
| total_amount | float | 龙虎榜总成交额（元） | 80000000.0 |
| turnover_rate | float | 换手率（%） | 5.5 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定日期无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.lhb import get_dragon_tiger_list

# 获取某日的龙虎榜数据
df = get_dragon_tiger_list("2024-01-15")
print(df.head())
```

### get_dragon_tiger_summary

获取龙虎榜统计。

**功能描述**：按股票、营业部或上榜原因汇总龙虎榜数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 是 | - | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 是 | - | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| group_by | Literal["stock", "broker", "reason"] | 否 | "stock" | 分组维度 | "stock" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**（根据group_by不同而变化）：

**按股票分组（group_by="stock"）**：
- symbol: 股票代码
- name: 股票名称
- list_count: 上榜次数
- total_net_amount: 总净额（元）
- total_buy_amount: 总买入金额（元）
- total_sell_amount: 总卖出金额（元）

**按营业部分组（group_by="broker"）**：
- broker_name: 营业部名称
- list_count: 上榜次数
- total_net_amount: 总净额（元）
- total_buy_amount: 总买入金额（元）
- total_sell_amount: 总卖出金额（元）

**按原因分组（group_by="reason"）**：
- reason: 上榜原因
- stock_count: 股票数量
- total_net_amount: 总净额（元）
- avg_pct_change: 平均涨跌幅（%）

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.lhb import get_dragon_tiger_summary

# 按股票汇总龙虎榜数据
df = get_dragon_tiger_summary("2024-01-01", "2024-01-31", group_by="stock")
print(df.head())
```

### get_dragon_tiger_broker_stats

获取营业部统计。

**功能描述**：统计营业部在龙虎榜上的活跃度和交易情况。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 是 | - | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 是 | - | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| top_n | int | 否 | 50 | 返回前N名 | 20 |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**：

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| rank | int | 排名 | 1 |
| broker_name | str | 营业部名称 | "某某证券营业部" |
| list_count | int | 上榜次数 | 50 |
| buy_amount | float | 总买入金额（元） | 500000000.0 |
| buy_count | int | 买入次数 | 30 |
| sell_amount | float | 总卖出金额（元） | 300000000.0 |
| sell_count | int | 卖出次数 | 20 |
| net_amount | float | 净额（元） | 200000000.0 |
| total_amount | float | 总成交额（元） | 800000000.0 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.lhb import get_dragon_tiger_broker_stats

# 获取营业部活跃度排名
df = get_dragon_tiger_broker_stats("2024-01-01", "2024-01-31", top_n=20)
print(df.head())
```