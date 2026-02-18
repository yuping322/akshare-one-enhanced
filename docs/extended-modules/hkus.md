# 港股美股（HKUS）

港股美股模块提供香港和美国股票市场相关数据接口。

**数据源**: 东方财富（eastmoney）  
**更新频率**: 实时（交易时段）

## 导入方式

```python
from akshare_one.modules.hkus import (
    get_hk_stocks,
)
```

## 接口列表

### get_hk_stocks

获取港股列表和实时行情。

**功能描述**: 查询所有港股的实时行情数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "00700" |
| name | str | 股票名称 | "腾讯控股" |
| price | float | 最新价 | 350.5 |
| pct_change | float | 涨跌幅(%) | 2.5 |
| change | float | 涨跌额 | 8.5 |
| volume | int | 成交量 | 1000000 |
| amount | float | 成交额 | 350000000 |
| high | float | 最高价 | 355.0 |
| low | float | 最低价 | 348.0 |
| open | float | 开盘价 | 342.0 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.hkus import get_hk_stocks

# 获取港股实时行情
hk_stocks = get_hk_stocks()
print(hk_stocks.head(10))

# 筛选涨幅前10的港股
top_gainers = hk_stocks.nlargest(10, 'pct_change')
print("\n港股涨幅前10:")
print(top_gainers[['name', 'price', 'pct_change']])
```

## 使用场景

### 场景1: 港股热点追踪

```python
from akshare_one.modules.hkus import get_hk_stocks

# 获取港股数据
hk_stocks = get_hk_stocks()

# 筛选大市值股票（假设成交额>1亿）
large_cap = hk_stocks[hk_stocks['amount'] > 100000000]
large_cap = large_cap.nlargest(10, 'pct_change')

print("港股大市值领涨:")
print(large_cap[['name', 'price', 'pct_change', 'amount']])
```

### 场景2: 港股通标的筛选

```python
from akshare_one.modules.hkus import get_hk_stocks

# 获取港股数据
hk_stocks = get_hk_stocks()

# 筛选活跃股票（换手率>1%）
active_stocks = hk_stocks[hk_stocks['turnover'] > 1]
active_stocks = active_stocks.sort_values('pct_change', ascending=False)

print("活跃港股:")
print(active_stocks[['name', 'price', 'pct_change', 'turnover']].head(20))
```

## 港股交易时间

| 时段 | 时间（北京时间） | 说明 |
|------|----------------|------|
| 开市前时段 | 09:00-09:30 | 竞价时段 |
| 早市 | 09:30-12:00 | 连续交易 |
| 午市 | 13:00-16:00 | 连续交易 |
| 收市竞价 | 16:00-16:10 | 竞价时段 |

## 港股特点

1. **T+0交易**: 当日可买卖
2. **无涨跌停限制**: 波动可能较大
3. **港币计价**: 注意汇率风险
4. **港股通**: 内地投资者可通过港股通投资

## 相关模块

- [指数数据](index.md) - 恒生指数等
- [沪深港通](northbound.md) - 互联互通资金流向

## 注意事项

1. 港股受国际市场影响较大
2. 汇率波动会影响实际收益
3. 部分小盘股流动性较差
4. 交易规则与A股有差异
