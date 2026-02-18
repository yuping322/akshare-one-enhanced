# 大宗交易（BlockDeal）

大宗交易模块提供相关数据接口。

**数据源**：东方财富（eastmoney）  
**更新频率**：T+1  
**示例程序**：[examples/blockdeal_example.py](../../examples/blockdeal_example.py)

## 导入方式

```python
from akshare_one.modules.blockdeal import (
    get_block_deal,
    get_block_deal_summary
)
```

## 接口列表

### get_block_deal

获取大宗交易明细。

**功能描述**：查询指定股票或全市场的大宗交易明细数据。

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
| date | str | 交易日期（YYYY-MM-DD） | "2024-01-15" |
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| price | float | 成交价格（元） | 12.50 |
| volume | float | 成交数量（股） | 10000000.0 |
| amount | float | 成交金额（元） | 125000000.0 |
| buyer_branch | str | 买方营业部 | "某某证券营业部" |
| seller_branch | str | 卖方营业部 | "某某证券营业部" |
| premium_rate | float | 溢价率（%） | -2.5 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.blockdeal import get_block_deal

# 获取浦发银行的大宗交易数据
df = get_block_deal("600000", start_date="2024-01-01", end_date="2024-01-31")
print(df.head())
```

### get_block_deal_summary

获取大宗交易统计。

**功能描述**：按股票、日期或营业部汇总大宗交易数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| start_date | str | 否 | "1970-01-01" | 开始日期（YYYY-MM-DD格式） | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期（YYYY-MM-DD格式） | "2024-01-31" |
| group_by | Literal["stock", "date", "broker"] | 否 | "stock" | 分组维度 | "stock" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**：pd.DataFrame

**列说明**（根据group_by不同而变化）：

**按股票分组（group_by="stock"）**：
- symbol: 股票代码
- name: 股票名称
- deal_count: 交易次数
- total_amount: 总成交金额（元）
- avg_premium_rate: 平均溢价率（%）

**按日期分组（group_by="date"）**：
- date: 日期
- deal_count: 交易次数
- total_amount: 总成交金额（元）
- avg_premium_rate: 平均溢价率（%）

**按营业部分组（group_by="broker"）**：
- broker_name: 营业部名称
- deal_count: 交易次数
- total_amount: 总成交金额（元）
- avg_premium_rate: 平均溢价率（%）

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.blockdeal import get_block_deal_summary

# 按股票汇总大宗交易数据
df = get_block_deal_summary(start_date="2024-01-01", end_date="2024-01-31", group_by="stock")
print(df.head())
```