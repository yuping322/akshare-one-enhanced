<div align="center">
  <h1>AKShare One</h1>
  <div>
    <a href="README.md">English</a> | <strong>中文</strong>
  </div>
</div>

**AKShare One** 是用于获取中国A股的数据接口，基于 [AKShare](https://github.com/akfamily/akshare) 开发，目的是简化AKShare的调用，并且统一不同数据源的输入输出格式，使得数据可以更加方便的传递给大语言模型。

## ✨ 项目特色

- 📊 统一不同数据源的股票代码格式
- 🏗️ 标准化返回数据结构
- 🛠️ 简化API参数设计
- ⏱️ 自动处理时间戳和复权数据

## 🚀 核心功能

### 基础数据接口

| 功能 | 接口 |
|------|------|
| 历史数据 | `get_hist_data` |
| 实时行情 | `get_realtime_data` |
| 个股新闻 | `get_news_data` |
| 财务数据 | `get_balance_sheet`/`get_income_statement`/`get_cash_flow` |
| 期货数据 | `get_futures_hist_data`/`get_futures_realtime_data` |
| 期权数据 | `get_options_chain`/`get_options_realtime`/`get_options_hist` |
| 内部交易 | `get_inner_trade_data` |
| 股票基本信息 | `get_basic_info` |
| 财务指标 | `get_financial_metrics` |
| 技术指标 | 参见 [indicators.py](src/akshare_one/indicators.py) |

### 市场数据扩展接口（新增）

| 功能模块 | 主要接口 | 说明 |
|---------|---------|------|
| **资金流数据** | `get_stock_fund_flow`<br>`get_sector_fund_flow`<br>`get_main_fund_flow_rank` | 个股/板块资金流向、主力资金排名 |
| **公告信披** | `get_disclosure_news`<br>`get_dividend_data`<br>`get_repurchase_data`<br>`get_st_delist_data` | 公告数据、分红派息、股票回购、ST/退市风险 |
| **北向资金** | `get_northbound_flow`<br>`get_northbound_holdings`<br>`get_northbound_top_stocks` | 北向资金流向、持股明细、排名 |
| **宏观数据** | `get_lpr_rate`<br>`get_pmi_index`<br>`get_cpi_data`<br>`get_m2_supply`<br>`get_shibor_rate` | LPR利率、PMI指数、CPI/PPI、M2货币供应、Shibor利率 |
| **大宗交易** | `get_block_deal`<br>`get_block_deal_summary` | 大宗交易明细、统计分析 |
| **龙虎榜** | `get_dragon_tiger_list`<br>`get_dragon_tiger_summary`<br>`get_dragon_tiger_broker_stats` | 龙虎榜数据、统计、营业部分析 |
| **涨停池** | `get_limit_up_pool`<br>`get_limit_down_pool`<br>`get_limit_up_stats` | 涨停/跌停池、统计分析 |
| **融资融券** | `get_margin_data`<br>`get_margin_summary` | 融资融券数据、市场汇总 |
| **股权质押** | `get_equity_pledge`<br>`get_equity_pledge_ratio_rank` | 股权质押数据、质押比例排名 |
| **限售解禁** | `get_restricted_release`<br>`get_restricted_release_calendar` | 限售解禁数据、解禁日历 |
| **商誉** | `get_goodwill_data`<br>`get_goodwill_impairment`<br>`get_goodwill_by_industry` | 商誉数据、减值预期、行业统计 |
| **ESG评级** | `get_esg_rating`<br>`get_esg_rating_rank` | ESG评分、评级排名 |

## 📦 快速安装

```bash
pip install akshare-one
```

## 💻 使用示例

### 基础数据获取

```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma

# 获取历史数据
df = get_hist_data(
    symbol="600000",
    interval="day",
    adjust="hfq"
)

# 计算20日简单移动平均
df_sma = get_sma(df, window=20)
```

### 资金流分析

```python
from akshare_one.modules.fundflow import (
    get_stock_fund_flow,
    get_sector_fund_flow,
    get_main_fund_flow_rank
)

# 获取个股资金流
fund_flow = get_stock_fund_flow(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 获取行业板块资金流
sector_flow = get_sector_fund_flow(
    sector_type="industry",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 获取主力资金排名
rank = get_main_fund_flow_rank(
    date="2024-12-31",
    indicator="net_inflow"
)
```

### 公告信披监控

```python
from akshare_one.modules.disclosure import (
    get_disclosure_news,
    get_dividend_data,
    get_repurchase_data
)

# 获取公告数据
news = get_disclosure_news(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31",
    category="all"
)

# 获取分红派息数据
dividend = get_dividend_data(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

### 北向资金追踪

```python
from akshare_one.modules.northbound import (
    get_northbound_flow,
    get_northbound_holdings,
    get_northbound_top_stocks
)

# 获取北向资金流向
flow = get_northbound_flow(
    start_date="2024-01-01",
    end_date="2024-12-31",
    market="all"
)

# 获取北向持股明细
holdings = get_northbound_holdings(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

### 宏观数据分析

```python
from akshare_one.modules.macro import (
    get_lpr_rate,
    get_pmi_index,
    get_cpi_data
)

# 获取LPR利率
lpr = get_lpr_rate(
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 获取PMI指数
pmi = get_pmi_index(
    start_date="2024-01-01",
    end_date="2024-12-31",
    pmi_type="manufacturing"
)
```

## 📚 文档

完整API文档现已迁移至GitHub Pages：

https://zwldarren.github.io/akshare-one/
