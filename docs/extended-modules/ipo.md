# 新股次新（IPO）

新股次新模块提供IPO和新上市股票相关数据接口。

**数据源**: 东方财富（eastmoney）、巨潮资讯（cninfo）  
**更新频率**: 日度

## 导入方式

```python
from akshare_one.modules.ipo import (
    get_new_stocks,
    get_ipo_info,
)
```

## 接口列表

### get_new_stocks

获取新上市股票列表。

**功能描述**: 查询最近上市的新股列表和基本信息。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["eastmoney"] | 否 | "eastmoney" | 数据源 | "eastmoney" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "603123" |
| name | str | 股票名称 | "某某科技" |
| ipo_date | str | 上市日期 | "2024-01-15" |
| issue_price | float | 发行价格 | 10.5 |
| issue_pe | float | 发行市盈率 | 25.5 |
| total_shares | int | 总股本(万股) | 10000 |
| circulate_shares | int | 流通股本(万股) | 2500 |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.ipo import get_new_stocks

# 获取新股列表
new_stocks = get_new_stocks()
print(new_stocks.head(10))

# 筛选近期上市的新股
recent_new = new_stocks[new_stocks['ipo_date'] >= '2024-01-01']
print(f"\n2024年上市新股: {len(recent_new)}只")
print(recent_new[['name', 'ipo_date', 'issue_price']].head())
```

---

### get_ipo_info

获取IPO详细信息。

**功能描述**: 查询IPO的详细信息，包括发行方案、承销商等。

#### 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例值 |
|--------|------|------|--------|------|--------|
| source | Literal["cninfo"] | 否 | "cninfo" | 数据源 | "cninfo" |

#### 返回值

**类型**: pd.DataFrame

**列说明**:

| 列名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| symbol | str | 股票代码 | "603123" |
| name | str | 公司名称 | "某某科技股份有限公司" |
| ipo_date | str | 上市日期 | "2024-01-15" |
| underwriter | str | 主承销商 | "中信证券" |
| legal_representative | str | 法定代表人 | "张三" |
| registered_capital | float | 注册资本(亿元) | 1.5 |
| industry | str | 所属行业 | "信息技术" |
| business_scope | str | 经营范围 | "软件开发、技术服务..." |

#### 异常

- `DataSourceUnavailableError` - 数据源不可用

#### 示例代码

```python
from akshare_one.modules.ipo import get_ipo_info

# 获取IPO详细信息
ipo_info = get_ipo_info()
print(ipo_info.head())

# 分析承销商分布
underwriter_dist = ipo_info['underwriter'].value_counts()
print("\n主承销商分布:")
print(underwriter_dist.head(5))
```

## 使用场景

### 场景1: 新股申购分析

```python
from akshare_one.modules.ipo import get_new_stocks, get_ipo_info

# 获取新股数据
new_stocks = get_new_stocks()
ipo_info = get_ipo_info()

# 合并数据
merged = new_stocks.merge(ipo_info, on='symbol', suffixes=('', '_info'))

# 分析发行估值
high_pe = merged[merged['issue_pe'] > 50]
low_pe = merged[merged['issue_pe'] <= 20]

print(f"高估值发行(PE>50): {len(high_pe)}只")
print(f"低估值发行(PE<=20): {len(low_pe)}只")

# 查看行业分布
industry_dist = merged['industry'].value_counts()
print("\n行业分布:")
print(industry_dist.head())
```

### 场景2: 次新股跟踪

```python
from akshare_one.modules.ipo import get_new_stocks
import pandas as pd

# 获取新股
new_stocks = get_new_stocks()

# 计算上市天数
today = pd.Timestamp.now().strftime('%Y-%m-%d')
new_stocks['ipo_date'] = pd.to_datetime(new_stocks['ipo_date'])
new_stocks['days_since_ipo'] = (pd.Timestamp(today) - new_stocks['ipo_date']).dt.days

# 筛选次新股（上市<90天）
sub_new = new_stocks[new_stocks['days_since_ipo'] < 90]
print(f"次新股数量(90天内): {len(sub_new)}")

# 按发行价格排序
price_sorted = sub_new.sort_values('issue_price')
print("\n发行价格最低的次新股:")
print(price_sorted[['name', 'issue_price', 'days_since_ipo']].head())
```

## IPO基础知识

### 发行流程
1. **申报阶段**: 向证监会提交IPO申请
2. **审核阶段**: 证监会审核材料
3. **发行阶段**: 确定发行价格，进行网下/网上申购
4. **上市阶段**: 股票正式在交易所挂牌交易

### 关键指标
- **发行市盈率(PE)**: 反映估值水平
- **发行价格**: 申购价格
- **中签率**: 申购成功率
- **首日涨幅**: 上市首日表现

### 数据来源对比

| 数据源 | 优势 | 适用场景 |
|--------|------|---------|
| **eastmoney** | 更新及时，界面友好 | 新股列表查询 |
| **cninfo** | 官方权威，信息详细 | IPO详细信息 |

## 相关模块

- [指数数据](index.md) - 新股对指数影响
- [资金流](fundflow.md) - 新股资金流向
- [市场情绪](sentiment.md) - 新股关注度

## 注意事项

1. 新股申购需满足市值要求
2. 发行市盈率仅供参考，实际估值需结合基本面
3. 次新股波动较大，注意风险控制
4. 关注解禁日期对股价的影响
