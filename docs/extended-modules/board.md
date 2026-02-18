# 科创板创业板（Board）

科创板创业板模块提供特殊板块股票数据接口。

**数据源**: 东方财富（eastmoney）  
**更新频率**: 实时

## 导入方式

```python
from akshare_one.modules.board import (
    get_kcb_stocks,
    get_cyb_stocks,
)
```

## 接口列表

### get_kcb_stocks

获取科创板股票列表和实时行情。

**功能描述**: 查询所有科创板股票的实时行情数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "688001" |
| name | str | 股票名称 | "华兴源创" |
| price | float | 最新价 | 25.5 |
| pct_change | float | 涨跌幅(%) | 2.5 |
| change | float | 涨跌额 | 0.63 |
| volume | int | 成交量 | 1000000 |
| amount | float | 成交额 | 25500000 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.board import get_kcb_stocks

# 获取科创板股票
kcb_stocks = get_kcb_stocks()
print(kcb_stocks.head(10))

# 筛选涨幅前10的科创板股票
top_kcb = kcb_stocks.nlargest(10, 'pct_change')
print("\n科创板涨幅前10:")
print(top_kcb[['name', 'price', 'pct_change']])
```

---

### get_cyb_stocks

获取创业板股票列表和实时行情。

**功能描述**: 查询所有创业板股票的实时行情数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "300001" |
| name | str | 股票名称 | "特锐德" |
| price | float | 最新价 | 15.5 |
| pct_change | float | 涨跌幅(%) | 1.5 |
| change | float | 涨跌额 | 0.23 |
| volume | int | 成交量 | 2000000 |
| amount | float | 成交额 | 31000000 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.board import get_cyb_stocks

# 获取创业板股票
cyb_stocks = get_cyb_stocks()
print(cyb_stocks.head(10))

# 筛选活跃的创业板股票
active_cyb = cyb_stocks[cyb_stocks['amount'] > 10000000]
active_cyb = active_cyb.nlargest(10, 'pct_change')
print("\n活跃创业板涨幅前10:")
print(active_cyb[['name', 'price', 'pct_change', 'amount']])
```

## 使用场景

### 场景1: 特殊板块监控

```python
from akshare_one.modules.board import get_kcb_stocks, get_cyb_stocks

# 获取科创板和创业板数据
kcb = get_kcb_stocks()
cyb = get_cyb_stocks()

# 合并分析
all_special = pd.concat([kcb, cyb])
print(f"科创板数量: {len(kcb)}")
print(f"创业板数量: {len(cyb)}")
print(f"特殊板块总数: {len(all_special)}")

# 查看整体表现
avg_change = all_special['pct_change'].mean()
print(f"特殊板块平均涨跌幅: {avg_change:.2f}%")
```

### 场景2: 板块轮动分析

```python
from akshare_one.modules.board import get_kcb_stocks, get_cyb_stocks

# 获取数据
kcb = get_kcb_stocks()
cyb = get_cyb_stocks()

# 计算各板块强度
kcb_strength = kcb['pct_change'].mean()
cyb_strength = cyb['pct_change'].mean()

print(f"科创板强度: {kcb_strength:.2f}%")
print(f"创业板强度: {cyb_strength:.2f}%")

if kcb_strength > cyb_strength:
    print("科创板相对强势")
else:
    print("创业板相对强势")
```

## 特殊板块特点

### 科创板 (KCB)
- **股票代码**: 688开头
- **交易规则**: T+1，无涨跌停限制（上市前5天）
- **定位**: 科技创新企业
- **风险特征**: 高波动、高成长

### 创业板 (CYB)
- **股票代码**: 300开头
- **交易规则**: T+1，20%涨跌停限制
- **定位**: 成长型创新创业企业
- **风险特征**: 中高波动、成长性好

## 相关模块

- [指数数据](index.md) - 科创50、创业板指
- [市场情绪](sentiment.md) - 市场情绪指标
- [资金流](fundflow.md) - 资金流向分析

## 注意事项

1. 科创板和创业板交易规则与主板不同
2. 波动性较大，需注意风险控制
3. 建议结合基本面和技术面综合分析
4. 关注相关政策对特殊板块的影响
