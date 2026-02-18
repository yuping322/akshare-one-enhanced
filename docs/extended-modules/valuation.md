# 估值分析（Valuation）

估值模块提供股票和市场估值相关数据接口。

**数据源**: 东方财富（eastmoney）、乐估（legu）  
**更新频率**: 日度

## 导入方式

```python
from akshare_one.modules.valuation import (
    get_stock_valuation,
    get_market_valuation,
)
```

## 接口列表

### get_stock_valuation

获取个股估值数据。

**功能描述**: 查询股票的PE、PB、PS等估值指标历史数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| symbol | str | 是 | - | 股票代码 | "600000" |
| start_date | str | 否 | "1970-01-01" | 开始日期 | "2024-01-01" |
| end_date | str | 否 | "2030-12-31" | 结束日期 | "2024-12-31" |
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期 | "2024-01-15" |
| symbol | str | 股票代码 | "600000" |
| close | float | 收盘价 | 10.5 |
| pe_ttm | float | 市盈率TTM | 8.5 |
| pe_static | float | 静态市盈率 | 9.2 |
| pb | float | 市净率 | 0.85 |
| ps | float | 市销率 | 2.5 |
| pcf | float | 市现率 | 12.3 |
| peg | float | PEG比率 | 0.8 |
| market_cap | float | 总市值(亿) | 3000.5 |
| float_market_cap | float | 流通市值(亿) | 2500.2 |

#### 异常

- `InvalidParameterError` - 参数无效
- `NoDataError` - 无数据
- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.valuation import get_stock_valuation

# 获取估值数据
df = get_stock_valuation("600000", start_date="2023-01-01")
print(df.head())

# 查看最新估值
latest = df.iloc[-1]
print(f"\n当前估值:")
print(f"PE(TTM): {latest['pe_ttm']:.2f}")
print(f"PB: {latest['pb']:.2f}")
print(f"总市值: {latest['market_cap']:.2f}亿")
```

---

### get_market_valuation

获取市场估值数据。

**功能描述**: 查询主要市场指数的估值水平。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney","legu"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| date | str | 日期 | "2024-01-15" |
| index_name | str | 指数名称 | "上证指数" |
| pe | float | 市盈率 | 12.5 |
| pb | float | 市净率 | 1.2 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.valuation import get_market_valuation

# 获取市场估值
market = get_market_valuation()
print(market)

# 判断市场整体估值水平
sh_pe = market[market['index_name'] == '上证指数']['pe'].iloc[0]
if sh_pe < 15:
    print("市场整体估值偏低")
elif sh_pe > 25:
    print("市场整体估值偏高")
else:
    print("市场整体估值合理")
```

## 估值指标解读

### 市盈率（PE）

| PE范围 | 估值水平 | 适用行业 |
|--------|---------|---------|
| < 10 | 极低 | 银行、地产、基建 |
| 10-20 | 较低 | 制造业、传统行业 |
| 20-30 | 合理 | 消费品、医药 |
| 30-50 | 较高 | 科技、成长型 |
| > 50 | 极高 | 互联网、新兴行业 |

### 市净率（PB）

| PB范围 | 估值水平 | 说明 |
|--------|---------|------|
| < 1 | 破净 | 股价低于净资产 |
| 1-2 | 较低 | 传统行业常见 |
| 2-5 | 合理 | 大部分行业 |
| > 5 | 较高 | 轻资产、高成长 |

### PEG比率

| PEG | 评价 | 说明 |
|-----|------|------|
| < 0.5 | 低估 | 性价比高 |
| 0.5-1 | 合理 | 价格匹配增长 |
| 1-2 | 较高 | 需高增长支撑 |
| > 2 | 高估 | 风险较大 |

## 使用场景

### 场景1: 历史估值分位分析

```python
from akshare_one.modules.valuation import get_stock_valuation

# 获取历史估值
df = get_stock_valuation("600000", start_date="2019-01-01")

# 计算当前估值在历史中的分位
current_pe = df['pe_ttm'].iloc[-1]
pe_percentile = (df['pe_ttm'] < current_pe).mean() * 100

print(f"当前PE: {current_pe:.2f}")
print(f"历史分位: {pe_percentile:.1f}%")

if pe_percentile < 20:
    print("估值处于历史低位")
elif pe_percentile > 80:
    print("估值处于历史高位")
else:
    print("估值处于历史中位")
```

### 场景2: 同行业估值对比

```python
from akshare_one.modules.valuation import get_stock_valuation

# 银行股估值对比
bank_symbols = ['600000', '601398', '601288', '601939']
valuation_list = []

for symbol in bank_symbols:
    try:
        df = get_stock_valuation(symbol)
        if not df.empty:
            latest = df.iloc[-1]
            valuation_list.append({
                'symbol': symbol,
                'pe': latest['pe_ttm'],
                'pb': latest['pb'],
                'market_cap': latest['market_cap']
            })
    except:
        pass

# 对比
import pandas as pd
comparison = pd.DataFrame(valuation_list)
comparison = comparison.sort_values('pe')
print("银行股估值对比:")
print(comparison)
```

### 场景3: 估值趋势分析

```python
from akshare_one.modules.valuation import get_stock_valuation
import matplotlib.pyplot as plt

# 获取数据
df = get_stock_valuation("600000", start_date="2023-01-01")

# 计算PE的20日移动平均
df['pe_ma20'] = df['pe_ttm'].rolling(20).mean()

# 绘制估值趋势
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(df['date'], df['close'], label='股价')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(df['date'], df['pe_ttm'], label='PE(TTM)')
plt.plot(df['date'], df['pe_ma20'], label='PE(MA20)')
plt.legend()
plt.tight_layout()
plt.show()
```

## 估值策略

### 1. 低估值策略

```python
# 筛选低PE、低PB股票
if pe < 15 and pb < 1.5:
    print("符合低估值标准")
```

### 2. 高成长策略（PEG）

```python
# PEG < 1，性价比高
if peg < 1:
    print("高成长股，估值合理")
```

### 3. 破净策略

```python
# PB < 1，破净
if pb < 1:
    print("股价低于净资产，关注资产质量")
```

## 估值陷阱

### 1. 低PE陷阱

- 业绩即将大幅下滑
- 行业处于衰退期
- 一次性收益导致PE虚低

### 2. 高PE陷阱

- 业绩无法支撑高估值
- 行业景气度见顶
- 市场情绪推动的泡沫

### 3. 周期股估值

- 周期股PE低点往往是买入时机（盈利高点）
- PE高点往往是卖出时机（盈利低点）

## 相关模块

- [财务数据](../core-api/financial.md) - 详细财务报表
- [业绩](performance.md) - 业绩分析
- [指数](index.md) - 市场指数数据

## 注意事项

1. 估值需结合行业特点和公司成长性
2. 不同行业估值标准不同，不可简单对比
3. 历史估值分位仅供参考，不代表未来
4. 估值只是投资参考因素之一，需综合判断

## 行业估值参考

| 行业 | 合理PE | 合理PB | 特点 |
|------|--------|--------|------|
| 银行 | 5-10 | 0.5-1.0 | 低估值、高分红 |
| 消费 | 20-40 | 3-8 | 稳定增长 |
| 医药 | 25-50 | 3-6 | 成长性好 |
| 科技 | 30-60 | 4-10 | 高成长、高波动 |
| 周期 | 10-20 | 1-2 | 波动大 |
| 公用事业 | 15-25 | 1-2 | 防御性强 |
