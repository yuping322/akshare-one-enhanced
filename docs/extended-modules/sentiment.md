# 市场情绪（Sentiment）

情绪模块提供市场情绪相关数据接口。

**数据源**: 东方财富（eastmoney）  
**更新频率**: 实时/日度

## 导入方式

```python
from akshare_one.modules.sentiment import (
    get_hot_rank,
    get_stock_sentiment,
)
```

## 接口列表

### get_hot_rank

获取热门股票排行。

**功能描述**: 查询当前市场热度最高的股票排名。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| rank | int | 热度排名 | 1 |
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| price | float | 当前价格 | 10.5 |
| pct_change | float | 涨跌幅(%) | 5.2 |
| hot_value | float | 热度值 | 98.5 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.sentiment import get_hot_rank

# 获取热门股票排行
hot_stocks = get_hot_rank()
print("今日热门股票Top10:")
print(hot_stocks.head(10))

# 查看热度变化
for _, row in hot_stocks.head(5).iterrows():
    print(f"{row['rank']}. {row['name']} ({row['symbol']}): "
          f"热度{row['hot_value']}, 涨跌{row['pct_change']:+.2f}%")
```

---

### get_stock_sentiment

获取个股情绪数据。

**功能描述**: 查询股票的市场情绪评分和关注度。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600000" |
| name | str | 股票名称 | "浦发银行" |
| sentiment_score | float | 情绪评分(0-100) | 75.5 |
| attention_index | float | 关注度指数 | 85.2 |
| comment_count | int | 评论数 | 1500 |
| bullish_pct | float | 看多比例(%) | 65.5 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.sentiment import get_stock_sentiment

# 获取市场情绪数据
sentiment = get_stock_sentiment()
print(sentiment.head())

# 筛选情绪高涨的股票
high_sentiment = sentiment[sentiment['sentiment_score'] > 80]
print("\n情绪高涨的股票:")
print(high_sentiment[['name', 'sentiment_score', 'bullish_pct']].head())

# 筛选高关注度股票
high_attention = sentiment.nlargest(10, 'attention_index')
print("\n关注度最高的股票:")
print(high_attention[['name', 'attention_index']])
```

## 情绪指标解读

### 情绪评分 (Sentiment Score)

| 分数范围 | 情绪状态 | 说明 |
|---------|---------|------|
| 80-100 | 极度乐观 | 市场看多情绪浓厚，需警惕回调风险 |
| 60-80 | 乐观 | 看多为主，可以参与 |
| 40-60 | 中性 | 多空平衡，观望为主 |
| 20-40 | 悲观 | 看空为主，谨慎操作 |
| 0-20 | 极度悲观 | 市场恐慌，可能存在机会 |

### 关注度指数

- **高关注** (>80): 市场焦点，波动可能加大
- **中关注** (40-80): 正常关注度
- **低关注** (<40): 冷门股票，流动性可能较差

## 使用场景

### 场景1: 热点追踪

```python
from akshare_one.modules.sentiment import get_hot_rank

# 获取并分析热门股票
hot = get_hot_rank()

# 查看涨停股票
limit_up = hot[hot['pct_change'] >= 9.9]
print("今日涨停股票:")
print(limit_up[['name', 'hot_value']])

# 查看热度突增的股票
hot_surge = hot[hot['hot_value'] > 90]
print("\n热度突增:")
print(hot_surge[['name', 'hot_value', 'pct_change']])
```

### 场景2: 情绪与价格背离分析

```python
from akshare_one.modules.sentiment import get_stock_sentiment

# 获取情绪数据
sentiment = get_stock_sentiment()

# 找出情绪高涨但下跌的股票（可能错杀）
divergence = sentiment[
    (sentiment['sentiment_score'] > 70) &
    (sentiment['bullish_pct'] > 60)
]

print("情绪高涨的股票（可关注）:")
print(divergence[['name', 'sentiment_score', 'bullish_pct']].head(10))
```

### 场景3: 综合热度筛选

```python
from akshare_one.modules.sentiment import (
    get_hot_rank,
    get_stock_sentiment
)

# 合并热度排行和情绪数据
hot = get_hot_rank()
sentiment = get_stock_sentiment()

# 合并数据
merged = hot.merge(
    sentiment[['symbol', 'sentiment_score', 'bullish_pct']],
    on='symbol',
    how='inner'
)

# 综合评分：热度排名 + 情绪评分
merged['composite_score'] = (
    (100 - merged['rank']) * 0.5 +  # 排名越前越好
    merged['sentiment_score'] * 0.5
)

# 排序
top_picks = merged.nlargest(10, 'composite_score')
print("综合热度Top10:")
print(top_picks[['name', 'rank', 'sentiment_score', 'composite_score']])
```

## 情绪数据应用

### 1.  contrarian 策略（逆向思维）

```python
# 当市场极度悲观时买入
if avg_sentiment < 20:
    print("市场情绪极度悲观，可能是买入机会")

# 当市场极度乐观时卖出
if avg_sentiment > 90:
    print("市场情绪极度乐观，可能是卖出时机")
```

### 2. 趋势确认

```python
# 价格上涨 + 情绪高涨 = 趋势确认
if price_change > 5 and sentiment_score > 70:
    print("上涨趋势得到情绪支持")

# 价格下跌 + 情绪低迷 = 可能继续下跌
if price_change < -5 and sentiment_score < 30:
    print("下跌趋势可能持续")
```

### 3. 异常检测

```python
# 价格大涨但情绪一般 = 警惕假突破
if price_change > 7 and sentiment_score < 50:
    print("价格大涨但情绪不配合，可能是诱多")

# 价格大跌但情绪稳定 = 可能错杀
if price_change < -7 and sentiment_score > 60:
    print("价格大跌但情绪稳定，可能是错杀")
```

## 相关模块

- [龙虎榜](lhb.md) - 异常交易监控
- [涨停池](limitup.md) - 涨停股票池
- [资金流向](fundflow.md) - 资金流入流出

## 注意事项

1. 情绪数据仅供参考，不构成投资建议
2. 情绪变化快速，需结合其他指标综合判断
3. 小盘股情绪容易操纵，大盘股情绪更可靠
4. 极端情绪往往预示转折点

## 数据局限性

- 情绪数据基于公开信息统计，可能存在延迟
- 不同数据源的情绪计算方法可能不同
- 情绪指标更适合短线交易参考
- 需结合基本面分析做出投资决策
