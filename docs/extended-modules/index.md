# 指数数据（Index）

指数模块提供股票指数相关数据接口。

**数据源**: 东方财富（eastmoney）、新浪财经（sina）  
**更新频率**: 实时

## 导入方式

```python
from akshare_one.modules.index import (
    get_index_hist_data,
    get_index_realtime_data,
    get_index_list,
    get_index_constituents,
)
```

## 接口列表

### get_index_hist_data

获取指数历史数据。

**功能描述**: 查询指定指数的历史行情数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 是 | - | 指数代码 | "000001" |
| start_date | str | 否 | "1970-01-01" | 开始日期 | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期 | "2024-12-31" |
| interval | Literal["daily","weekly","monthly"] | 否 | "daily" | 时间粒度 | "daily" |
| source | Literal["eastmoney","sina"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期 | "2024-01-15" |
| symbol | str | 指数代码 | "000001" |
| open | float | 开盘点数 | 3200.5 |
| high | float | 最高点数 | 3210.3 |
| low | float | 最低点数 | 3195.2 |
| close | float | 收盘点数 | 3205.8 |
| volume | int | 成交量 | 100000000 |
| amount | float | 成交额 | 5000000000 |

#### 示例代码

```python
from akshare_one.modules.index import get_index_hist_data

# 获取上证指数历史数据
df = get_index_hist_data("000001", start_date="2024-01-01")
print(df.head())

# 计算月度收益
df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
monthly = df.groupby('month')['close'].agg(['first', 'last'])
monthly['return'] = (monthly['last'] - monthly['first']) / monthly['first'] * 100
print(monthly)
```

---

### get_index_realtime_data

获取指数实时行情。

**功能描述**: 查询指数的实时行情数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 否 | None | 指数代码 | "000001" |
| source | Literal["eastmoney","sina"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 指数代码 | "000001" |
| name | str | 指数名称 | "上证指数" |
| value | float | 当前点数 | 3205.8 |
| pct_change | float | 涨跌幅(%) | 0.5 |
| change | float | 涨跌额 | 15.8 |
| volume | int | 成交量 | 100000000 |

#### 示例代码

```python
from akshare_one.modules.index import get_index_realtime_data

# 获取所有指数实时行情
df = get_index_realtime_data()
print(df)

# 获取特定指数
sh_index = get_index_realtime_data("000001")
print(sh_index)
```

---

### get_index_list

获取指数列表。

**功能描述**: 查询所有可用的指数列表。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| category | Literal["cn","global"] | 否 | "cn" | 类别 | "cn" |
| source | Literal["eastmoney","sina"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 指数代码 | "000001" |
| name | str | 指数名称 | "上证指数" |
| type | str | 指数类型 | "综合指数" |

#### 示例代码

```python
from akshare_one.modules.index import get_index_list

# 获取中国指数列表
cn_indices = get_index_list(category="cn")
print(cn_indices.head(10))

# 获取全球指数列表
global_indices = get_index_list(category="global")
print(global_indices.head(10))
```

---

### get_index_constituents

获取指数成分股。

**功能描述**: 查询指定指数的成分股列表及其权重。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 是 | - | 指数代码 | "000300" |
| include_weight | bool | 否 | True | 包含权重 | True |
| source | Literal["eastmoney","sina"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| weight | float | 权重(%) | 2.5 |

#### 示例代码

```python
from akshare_one.modules.index import get_index_constituents

# 获取沪深300成分股
df = get_index_constituents("000300")
print(df.head(10))

# 按权重排序
top_weights = df.nlargest(10, 'weight')
print(top_weights)
```

## 常用指数代码

| 指数名称 | 代码 | 说明 |
|---------|------|------|
| 上证指数 | 000001 | 上海证券交易所综合指数 |
| 深证成指 | 399001 | 深圳证券交易所成份指数 |
| 创业板指 | 399006 | 创业板指数 |
| 沪深300 | 000300 | 沪深两市300只大盘股 |
| 中证500 | 000905 | 中小市值股票指数 |
| 科创50 | 000688 | 科创板50只代表性股票 |

## 使用场景

### 场景1: 大盘趋势分析

```python
from akshare_one.modules.index import get_index_hist_data
import pandas as pd

# 获取主要指数数据
indices = {
    '上证指数': '000001',
    '深证成指': '399001',
    '创业板指': '399006'
}

for name, symbol in indices.items():
    df = get_index_hist_data(symbol, start_date="2024-01-01")
    df['ma20'] = df['close'].rolling(20).mean()
    latest = df.iloc[-1]
    
    print(f"\n{name}:")
    print(f"  当前: {latest['close']:.2f}")
    print(f"  MA20: {latest['ma20']:.2f}")
    print(f"  趋势: {'上涨' if latest['close'] > latest['ma20'] else '下跌'}")
```

### 场景2: 成分股权重分析

```python
from akshare_one.modules.index import get_index_constituents

# 获取沪深300成分股权重
df = get_index_constituents("000300")

# 行业分布分析（假设有行业数据）
industry_dist = df.groupby('industry')['weight'].sum().sort_values(ascending=False)
print("行业权重分布:")
print(industry_dist.head(10))
```

## 相关模块

- [ETF](etf.md) - ETF基金数据
- [估值](valuation.md) - 市场估值数据
- [情绪](sentiment.md) - 市场情绪指标

## 注意事项

1. 指数点位不代表实际可交易价格
2. 成分股会定期调整，需关注指数公司公告
3. 不同数据源的成分股权重可能略有差异
