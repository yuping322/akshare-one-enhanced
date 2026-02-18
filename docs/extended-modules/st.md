# ST股票（ST）

ST股票模块提供特别处理股票相关数据接口。

**数据源**: 东方财富（eastmoney）  
**更新频率**: 日度

## 导入方式

```python
from akshare_one.modules.st import (
    get_st_stocks,
)
```

## 接口列表

### get_st_stocks

获取ST股票列表和实时行情。

**功能描述**: 查询所有被实施特别处理（ST/*ST）的股票列表和行情数据。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "600001" |
| name | str | 股票名称 | "*ST某某" |
| price | float | 最新价 | 2.5 |
| pct_change | float | 涨跌幅(%) | -5.0 |
| change | float | 涨跌额 | -0.13 |
| volume | int | 成交量 | 1000000 |
| amount | float | 成交额 | 2500000 |
| st_reason | str | ST原因 | "连续亏损" |
| st_date | str | ST实施日期 | "2023-04-30" |
| risk_level | str | 风险等级 | "高风险" |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.st import get_st_stocks

# 获取ST股票列表
st_stocks = get_st_stocks()
print(st_stocks.head(10))

# 统计ST股票数量
print(f"ST股票总数: {len(st_stocks)}")

# 筛选*ST股票
star_st = st_stocks[st_stocks['name'].str.contains('\*ST')]
print(f"*ST股票数量: {len(star_st)}")
```

## 使用场景

### 场景1: ST股票风险监控

```python
from akshare_one.modules.st import get_st_stocks

# 获取ST股票
st_stocks = get_st_stocks()

# 分析风险等级分布
risk_dist = st_stocks['risk_level'].value_counts()
print("ST股票风险等级分布:")
print(risk_dist)

# 筛选高风险股票
high_risk = st_stocks[st_stocks['risk_level'] == '高风险']
print(f"\n高风险ST股票: {len(high_risk)}只")
print(high_risk[['name', 'st_reason']].head())
```

### 场景2: ST股票摘帽预期

```python
from akshare_one.modules.st import get_st_stocks

# 获取ST股票
st_stocks = get_st_stocks()

# 查看近期实施ST的股票
import pandas as pd
st_stocks['st_date'] = pd.to_datetime(st_stocks['st_date'])
recent_st = st_stocks[st_stocks['st_date'] >= '2023-10-01']

print("近期ST股票:")
print(recent_st[['name', 'st_date', 'st_reason']].head())

# 分析ST原因分布
reason_dist = recent_st['st_reason'].value_counts()
print("\nST原因分布:")
print(reason_dist)
```

## ST股票基础知识

### ST标识含义
- **ST**: Special Treatment (特别处理)
- **\*ST**: 退市风险警示
- **退市整理期**: 进入退市程序

### 实施条件
- **ST**: 连续两年净利润为负
- **\*ST**: 连续三年净利润为负或其他重大风险
- **退市**: 连续四年净利润为负或其他严重违规

### 交易规则
- **涨跌停限制**: 5% (主板)
- **风险警示**: 名称前加ST/*ST标识
- **投资者适当性**: 部分券商要求开通权限

### 投资策略
1. **规避策略**: 避免持有ST股票
2. **博弈策略**: 博弈摘帽或重组
3. **对冲策略**: 作为风险对冲工具

## 相关模块

- [公告信披](disclosure.md) - ST相关公告
- [财务数据](../core-api/financial.md) - 财务指标分析
- [股东数据](shareholder.md) - 股东增减持情况

## 注意事项

1. ST股票风险极高，普通投资者应谨慎参与
2. ST股票可能面临退市风险，需密切关注公告
3. 不同交易所的ST规则可能略有差异
4. ST股票的流动性通常较差

## 风险提示

- ST股票可能存在重大财务或经营风险
- 股价波动剧烈，可能造成重大损失
- 退市风险真实存在，投资需谨慎
- 本数据仅供参考，不构成投资建议
