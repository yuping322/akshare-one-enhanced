<div align="center">
  <h1>AKShare One</h1>
  <p>中国金融市场数据的标准化接口</p>
  <p>
    <a href="https://github.com/zwldarren/akshare-one/actions/workflows/test.yml">
      <img src="https://github.com/zwldarren/akshare-one/actions/workflows/test.yml/badge.svg" alt="Tests">
    </a>
    <a href="https://codecov.io/gh/zwldarren/akshare-one">
      <img src="https://codecov.io/gh/zwldarren/akshare-one/branch/main/graph/badge.svg" alt="Coverage">
    </a>
    <a href="https://pypi.org/project/akshare-one/">
      <img src="https://img.shields.io/pypi/v/akshare-one.svg" alt="PyPI">
    </a>
    <a href="https://github.com/zwldarren/akshare-one/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/zwldarren/akshare-one.svg" alt="License">
    </a>
    <a href="https://python.org">
      <img src="https://img.shields.io/pypi/pyversions/akshare-one.svg" alt="Python">
    </a>
  </p>
</div>

**AKShare One** 是用于获取中国A股数据的接口库，基于 [AKShare](https://github.com/akfamily/akshare) 开发。旨在简化 AKShare 的调用，统一不同数据源的输入输出格式，使数据更容易传递给大语言模型（LLM）。

## ✨ 项目特色

- 📊 **统一股票代码格式** - 跨数据源的一致性体验
- 🏗️ **标准化数据结构** - 统一的返回格式，便于数据处理
- 🛠️ **简化的 API 设计** - 减少参数复杂性，提高易用性
- ⏱️ **自动处理** - 时间戳自动转换、复权数据自动处理
- 🔧 **多数据源支持** - 自动故障转移和智能路由
- 🚀 **丰富的数据类型** - 覆盖 8 大类数据接口

## 🚀 核心功能

### 基础数据接口

| 功能 | 接口 |
|------|------|
| 历史数据 | `get_hist_data` |
| 实时行情 | `get_realtime_data` |
| 个股新闻 | `get_news_data` |
| 财务数据 | `get_balance_sheet` / `get_income_statement` / `get_cash_flow` |
| 期货数据 | `get_futures_hist_data` / `get_futures_realtime_data` |
| 期权数据 | `get_options_chain` / `get_options_realtime` / `get_options_hist` |
| 内部交易 | `get_inner_trade_data` |
| 股票基本信息 | `get_basic_info` |
| 财务指标 | `get_financial_metrics` |
| 技术指标 | 参见 `src/akshare_one/indicators.py` |

### 市场数据扩展接口

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

完整安装（包含 TA-Lib 技术指标支持）：

```bash
pip install akshare-one[talib]
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

完整API文档现已发布：

- **在线文档**: https://zwldarren.github.io/akshare-one/
- **快速开始**: [docs/quickstart.md](docs/quickstart.md)
- **最小测试集**: [docs/MINIMUM_TEST_SUITE.md](docs/MINIMUM_TEST_SUITE.md)
- **产品就绪状态**: [PRODUCT_READINESS_STATUS.md](PRODUCT_READINESS_STATUS.md)

**更多文档**：
- **字段标准**: [docs/FIELD_NAMING_STANDARDS.md](docs/FIELD_NAMING_STANDARDS.md)
- **兼容性契约**: [docs/COMPATIBILITY_CONTRACT.md](docs/COMPATIBILITY_CONTRACT.md)
- **错误码参考**: [docs/error_codes.md](docs/error_codes.md)
- **变更日志**: [CHANGELOG.md](CHANGELOG.md)

## 🔧 技术栈

**核心依赖**:
- akshare (>=1.17.80) - 底层数据接口
- pandas - 数据处理
- requests - HTTP客户端
- cachetools (>=5.5.0) - 缓存系统

**可选依赖**:
- ta-lib (>=0.6.4) - 技术指标计算
- fastmcp (>=2.11.3) - MCP服务器
- pydantic (>=2.0.0) - 数据验证

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进 AKShare One！

详细开发指南请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [GitHub 仓库](https://github.com/zwldarren/akshare-one)
- [PyPI 包](https://pypi.org/project/akshare-one/)
- [AKShare 原项目](https://github.com/akfamily/akshare)
