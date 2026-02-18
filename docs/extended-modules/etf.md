# ETF基金（ETF）

ETF模块提供ETF基金相关数据接口。

**数据源**: 东方财富（eastmoney）、新浪财经（sina）  
**更新频率**: 实时

## 导入方式

```python
from akshare_one.modules.etf import (
    get_etf_hist_data,
    get_etf_realtime_data,
    get_etf_list,
    get_fund_manager_info,
    get_fund_rating_data,
)
```

## 接口列表

### get_etf_hist_data

获取ETF历史数据。

**功能描述**: 查询指定ETF的历史行情数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 是 | - | ETF代码 | "159915" |
| start_date | str | 否 | "1970-01-01" | 开始日期 | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期 | "2024-12-31" |
| interval | Literal["daily","weekly","monthly"] | 否 | "daily" | 时间粒度 | "daily" |
| source | Literal["eastmoney","sina"] | 否 | "eastmoney" | 数据源 | "eastmoney" |
| columns | list[str] | 否 | None | 返回列 | ["date", "close"] |
| row_filter | dict | 否 | None | 行过滤 | {"top_n": 10} |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期 | "2024-01-15" |
| symbol | str | ETF代码 | "159915" |
| open | float | 开盘价 | 2.5 |
| high | float | 最高价 | 2.55 |
| low | float | 最低价 | 2.48 |
| close | float | 收盘价 | 2.52 |
| volume | int | 成交量 | 1000000 |
| amount | float | 成交额 | 2520000 |
| pct_change | float | 涨跌幅(%) | 1.2 |

#### 示例代码

```python
from akshare_one.modules.etf import get_etf_hist_data

# 获取创业板ETF历史数据
df = get_etf_hist_data("159915", start_date="2024-01-01")
print(df.head())
```

---

### get_etf_realtime_data

获取ETF实时行情。

**功能描述**: 查询所有ETF的实时行情数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney","sina"] | 否 | "eastmoney" | 数据源 | "eastmoney" |
| columns | list[str] | 否 | None | 返回列 | ["symbol", "price"] |
| row_filter | dict | 否 | None | 行过滤 | {"top_n": 20} |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | ETF代码 | "159915" |
| name | str | ETF名称 | "创业板ETF" |
| price | float | 当前价格 | 2.52 |
| pct_change | float | 涨跌幅(%) | 1.2 |
| change | float | 涨跌额 | 0.03 |
| volume | int | 成交量 | 1000000 |
| turnover | float | 换手率(%) | 5.2 |

#### 示例代码

```python
from akshare_one.modules.etf import get_etf_realtime_data

# 获取ETF实时行情
df = get_etf_realtime_data()
print(df.head())

# 筛选涨幅前10
import pandas as pd
top_gainers = df.nlargest(10, 'pct_change')
print(top_gainers[['name', 'pct_change']])
```

---

### get_etf_list

获取ETF列表。

**功能描述**: 查询所有ETF的基本信息。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| category | str | 否 | "all" | 类别 | "stock"/"bond"/"money" |
| source | Literal["eastmoney","sina"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | ETF代码 | "159915" |
| name | str | ETF名称 | "创业板ETF" |
| type | str | 基金类型 | "股票型" |

#### 示例代码

```python
from akshare_one.modules.etf import get_etf_list

# 获取所有ETF
etfs = get_etf_list()
print(f"ETF总数: {len(etfs)}")

# 筛选股票型ETF
stock_etfs = etfs[etfs['type'] == '股票型']
print(f"股票型ETF数: {len(stock_etfs)}")
```

---

### get_fund_manager_info

获取基金经理信息。

**功能描述**: 查询基金经理的任职信息和业绩。

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| manager_name | str | 经理姓名 | "张三" |
| company | str | 所属公司 | "易方达" |
| fund_symbol | str | 基金代码 | "159915" |
| fund_name | str | 基金名称 | "创业板ETF" |
| tenure_days | int | 任职天数 | 1000 |
| aum_billion | float | 管理规模(亿) | 500.5 |
| best_return_pct | float | 最佳回报(%) | 150.2 |

#### 示例代码

```python
from akshare_one.modules.etf import get_fund_manager_info

# 获取基金经理信息
managers = get_fund_manager_info()
print(managers.head())

# 按管理规模排序
top_managers = managers.nlargest(10, 'aum_billion')
print(top_managers[['manager_name', 'aum_billion']])
```

---

### get_fund_rating_data

获取基金评级数据。

**功能描述**: 查询基金的评级信息。

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 基金代码 | "159915" |
| name | str | 基金名称 | "创业板ETF" |
| manager | str | 基金经理 | "张三" |
| star_count | int | 五星评级数 | 3 |
| morningstar_rating | str | 晨星评级 | "★★★★★" |
| fee | float | 费率(%) | 0.5 |

#### 示例代码

```python
from akshare_one.modules.etf import get_fund_rating_data

# 获取基金评级
ratings = get_fund_rating_data()

# 筛选五星基金
five_star = ratings[ratings['star_count'] == 5]
print(f"五星基金数量: {len(five_star)}")
```

## 使用场景

### 场景1: ETF定投分析

```python
from akshare_one.modules.etf import get_etf_hist_data
import pandas as pd

# 获取历史数据
df = get_etf_hist_data("159915", start_date="2023-01-01")

# 计算定投收益（假设每月1日定投）
df['date'] = pd.to_datetime(df['date'])
monthly = df[df['date'].dt.day == 1]
avg_price = monthly['close'].mean()
current_price = df['close'].iloc[-1]
return_pct = (current_price - avg_price) / avg_price * 100

print(f"定投平均成本: {avg_price:.2f}")
print(f"当前价格: {current_price:.2f}")
print(f"收益率: {return_pct:.2f}%")
```

### 场景2: 行业ETF轮动

```python
from akshare_one.modules.etf import get_etf_realtime_data

# 获取实时行情
etfs = get_etf_realtime_data()

# 筛选行业ETF（假设名称包含行业关键词）
industry_keywords = ['消费', '医药', '科技', '金融']
industry_etfs = etfs[etfs['name'].str.contains('|'.join(industry_keywords))]

# 按涨跌幅排序
ranked = industry_etfs.sort_values('pct_change', ascending=False)
print(ranked[['name', 'pct_change']].head(10))
```

## 相关模块

- [债券](bond.md) - 可转债数据
- [分析师](analyst.md) - 研报数据
- [估值](valuation.md) - 估值分析

## 注意事项

1. ETF存在跟踪误差，需关注与基准指数的偏离度
2. 交易时需注意流动性，选择成交量大的ETF
3. 费率会影响长期收益，建议选择费率较低的ETF
