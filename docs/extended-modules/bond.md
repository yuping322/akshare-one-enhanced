# 可转债（Bonds）

可转债模块提供可转债相关数据接口。

**数据源**: 东方财富（eastmoney）、集思录（jsl）  
**更新频率**: 实时

## 导入方式

```python
from akshare_one.modules.bond import (
    get_bond_list,
    get_bond_hist_data,
    get_bond_realtime_data,
)
```

## 接口列表

### get_bond_list

获取可转债列表。

**功能描述**: 查询所有可转债的基本信息，包括正股、转股价、信用评级等。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney", "jsl"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 债券代码 | "sh113050" |
| name | str | 债券名称 | "南银转债" |
| stock_symbol | str | 正股代码 | "600000" |
| stock_name | str | 正股名称 | "浦发银行" |
| convert_price | float | 转股价 | 10.5 |
| list_date | str | 上市日期 | "2021-07-01" |
| credit_rating | str | 信用评级 | "AAA" |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.bond import get_bond_list

# 获取可转债列表
bonds = get_bond_list()
print(bonds.head())

# 筛选AAA级债券
aaa_bonds = bonds[bonds['credit_rating'] == 'AAA']
print(f"AAA级可转债数量: {len(aaa_bonds)}")
```

---

### get_bond_hist_data

获取可转债历史数据。

**功能描述**: 查询指定可转债的历史行情数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 是 | - | 债券代码 | "sh113050" |
| start_date | str | 否 | "1970-01-01" | 开始日期 | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期 | "2024-12-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期 | "2024-01-15" |
| symbol | str | 债券代码 | "sh113050" |
| open | float | 开盘价 | 120.5 |
| high | float | 最高价 | 121.0 |
| low | float | 最低价 | 119.5 |
| close | float | 收盘价 | 120.8 |
| volume | int | 成交量 | 10000 |

#### 异常

- `InvalidParameterError` - 参数无效（如债券代码格式错误）
- `NoDataError` - 指定时间范围内无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.bond import get_bond_hist_data

# 获取可转债历史数据
df = get_bond_hist_data("sh113050", start_date="2024-01-01")
print(df.head())

# 计算涨跌幅
df['return'] = df['close'].pct_change() * 100
print(df[['date', 'close', 'return']].head())
```

---

### get_bond_realtime_data

获取可转债实时行情。

**功能描述**: 查询可转债实时行情数据，包括价格、溢价率等。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney", "jsl"] | 否 | "jsl" | 数据源 | "jsl" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 债券代码 | "sh113050" |
| name | str | 债券名称 | "南银转债" |
| price | float | 当前价格 | 120.5 |
| pct_change | float | 涨跌幅(%) | 2.5 |
| stock_symbol | str | 正股代码 | "600000" |
| stock_price | float | 正股价格 | 10.2 |
| convert_price | float | 转股价 | 10.5 |
| convert_value | float | 转股价值 | 97.14 |
| premium_rate | float | 溢价率(%) | 24.06 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.bond import get_bond_realtime_data

# 获取可转债实时行情
df = get_bond_realtime_data()
print(df.head())

# 筛选低溢价率债券
low_premium = df[df['premium_rate'] < 10]
print("低溢价率可转债:")
print(low_premium[['name', 'premium_rate']])
```

## 使用场景

### 场景1: 可转债筛选

```python
from akshare_one.modules.bond import get_bond_realtime_data

# 获取实时数据
bonds = get_bond_realtime_data()

# 筛选双低转债（价格低+溢价率低）
filtered = bonds[
    (bonds['price'] < 130) & 
    (bonds['premium_rate'] < 30)
]
print("双低转债:")
print(filtered[['name', 'price', 'premium_rate']].head(10))
```

### 场景2: 可转债与正股对比

```python
from akshare_one.modules.bond import get_bond_realtime_data

bonds = get_bond_realtime_data()

# 查看某只可转债
bond = bonds[bonds['symbol'] == 'sh113050'].iloc[0]
print(f"转债: {bond['name']}, 价格: {bond['price']}")
print(f"正股: {bond['stock_name']}, 价格: {bond['stock_price']}")
print(f"转股价值: {bond['convert_value']:.2f}")
print(f"溢价率: {bond['premium_rate']:.2f}%")
```

## 可转债基础知识

### 什么是可转债？

可转债（Convertible Bond）是一种可以在特定时间、按特定条件转换为普通股票的特殊企业债券。

### 关键指标

- **转股价值**: 可转债转换为股票后的价值
- **溢价率**: 可转债价格相对于转股价值的溢价程度
- **双低策略**: 选择价格低（<130元）且溢价率低（<30%）的可转债

### 数据来源对比

| 数据源 | 优势 | 适用场景 |
|--------|------|----------|
| eastmoney | 数据全面 | 历史数据查询 |
| jsl | 实时性强，字段丰富 | 实时行情监控 |

## 相关模块

- [ETF数据](etf.md) - ETF基金数据
- [市场情绪](sentiment.md) - 市场情绪指标

## 注意事项

1. 可转债存在强赎风险，需关注强赎公告
2. 转股溢价率会随正股价格波动
3. 建议结合正股基本面进行投资决策
