# AKShare One 文档导航

完整的文档结构和使用指南。

## 📚 文档总览

```
docs/
├── getting-started/     入门指南
├── core-api/           核心API参考  
├── extended-modules/   扩展市场数据模块（27个模块）
├── advanced/           高级主题
├── development/        开发文档
├── migration/          迁移指南
└── index.md            文档首页
```

**总文档数**: 48个  
**覆盖模块**: 27+  
**最后更新**: 2024年2月

---

## 🚀 入门指南 (getting-started/)

适合首次使用 AKShare One 的用户。

| 文档 | 描述 | 适用人群 |
|------|------|----------|
| [installation.md](getting-started/installation.md) | 安装配置，依赖说明，常见问题 | 所有用户 |
| [quickstart.md](getting-started/quickstart.md) | 快速上手，基本用法示例 | 新手 |
| [examples.md](getting-started/examples.md) | 实用代码示例，批量操作，图表绘制 | 开发者 |

**推荐阅读顺序**: installation → quickstart → examples

---

## 🔧 核心 API (core-api/)

AKShare One 的 8 个核心数据接口。

### 数据获取

| 文档 | 接口 | 描述 |
|------|------|------|
| [overview.md](core-api/overview.md) | API 概览 | 所有接口总览和数据源对比 |
| [historical.md](core-api/historical.md) | `get_hist_data()` | 历史行情数据 |
| [realtime.md](core-api/realtime.md) | `get_realtime_data()` | 实时行情数据 |
| [basic-info.md](core-api/basic-info.md) | `get_basic_info()` | 股票基本信息 |
| [news.md](core-api/news.md) | `get_news_data()` | 个股新闻 |

### 财务数据

| 文档 | 接口 | 描述 |
|------|------|------|
| [financial.md](core-api/financial.md) | `get_balance_sheet()`<br>`get_income_statement()`<br>`get_cash_flow()`<br>`get_financial_metrics()` | 财务报表和指标 |

### 衍生品

| 文档 | 接口 | 描述 |
|------|------|------|
| [futures.md](core-api/futures.md) | 期货历史/实时/主力合约 | 期货市场数据 |
| [options.md](core-api/options.md) | 期权链/实时/历史/到期日 | 期权市场数据 |

### 其他

| 文档 | 接口 | 描述 |
|------|------|------|
| [indicators.md](core-api/indicators.md) | 38+ 技术指标 | SMA, MACD, RSI, BOLL... |
| [insider.md](core-api/insider.md) | `get_inner_trade_data()` | 内部交易数据 |

---

## 📈 扩展模块 (extended-modules/)

20 个专业市场数据模块，提供更全面的数据覆盖。

### 概览

- **[overview.md](extended-modules/overview.md)** - 所有扩展模块的介绍和使用指南

### 基础数据模块

| 模块 | 文档 | 主要功能 | 数据源 |
|------|------|----------|--------|
| **指数数据** | [index.md](extended-modules/index.md) | 指数行情、实时数据、成分股 | 东方财富/新浪 |
| **ETF基金** | [etf.md](extended-modules/etf.md) | ETF数据、基金经理、基金评级 | 东方财富/新浪 |
| **可转债** | [bond.md](extended-modules/bond.md) | 可转债列表、历史、实时行情 | 东方财富/集思录 |
| **行业板块** | [industry.md](extended-modules/industry.md) | 行业板块行情和排名 | 东方财富 |
| **概念板块** | [concept.md](extended-modules/concept.md) | 概念板块行情和热点 | 东方财富 |
| **港股美股** | [hkus.md](extended-modules/hkus.md) | 港股实时行情 | 东方财富 |
| **科创板创业板** | [board.md](extended-modules/board.md) | 特殊板块股票数据 | 东方财富 |
| **新股次新** | [ipo.md](extended-modules/ipo.md) | IPO和新上市股票 | 东方财富/巨潮资讯 |
| **ST股票** | [st.md](extended-modules/st.md) | ST/*ST股票监控 | 东方财富 |
| **停复牌** | [suspended.md](extended-modules/suspended.md) | 停牌股票信息 | 东方财富 |

### 市场分析模块

| 模块 | 文档 | 主要功能 | 数据源 |
|------|------|----------|--------|
| **资金流** | [fundflow.md](extended-modules/fundflow.md) | 个股/板块资金流、主力排名 | 东方财富 |
| **公告信披** | [disclosure.md](extended-modules/disclosure.md) | 公告、分红、回购、ST风险 | 多源 |
| **北向资金** | [northbound.md](extended-modules/northbound.md) | 资金流向、持股明细、排名 | 东方财富 |
| **宏观数据** | [macro.md](extended-modules/macro.md) | LPR、PMI、CPI、M2、Shibor | 官方 |
| **大宗交易** | [blockdeal.md](extended-modules/blockdeal.md) | 大宗交易明细和统计 | 东方财富 |
| **龙虎榜** | [lhb.md](extended-modules/lhb.md) | 龙虎榜数据、营业部分析 | 东方财富 |
| **涨停池** | [limitup.md](extended-modules/limitup.md) | 涨停/跌停池和统计 | 东方财富 |
| **融资融券** | [margin.md](extended-modules/margin.md) | 融资融券数据 | 东方财富 |
| **股权质押** | [pledge.md](extended-modules/pledge.md) | 股权质押和比例排名 | 东方财富 |
| **限售解禁** | [restricted.md](extended-modules/restricted.md) | 限售解禁和解禁日历 | 东方财富 |
| **商誉** | [goodwill.md](extended-modules/goodwill.md) | 商誉数据和减值统计 | 东方财富 |
| **ESG评级** | [esg.md](extended-modules/esg.md) | ESG评分和排名 | 新浪财经 |

### 深度分析模块

| 模块 | 文档 | 主要功能 | 数据源 |
|------|------|----------|--------|
| **估值分析** | [valuation.md](extended-modules/valuation.md) | PE、PB、PS估值数据 | 东方财富/乐估 |
| **股东数据** | [shareholder.md](extended-modules/shareholder.md) | 股东增减持、机构持仓 | 东方财富/上交所 |
| **业绩快报** | [performance.md](extended-modules/performance.md) | 业绩预告、业绩快报 | 东方财富 |
| **分析师研报** | [analyst.md](extended-modules/analyst.md) | 分析师排名、个股研报 | 东方财富 |
| **市场情绪** | [sentiment.md](extended-modules/sentiment.md) | 热度排行、情绪评分 | 东方财富 |

---

## 🎓 高级主题 (advanced/)

深入理解 AKShare One 的高级功能。

| 文档 | 内容 | 适用人群 |
|------|------|----------|
| [multi-source.md](advanced/multi-source.md) | 多数据源架构、MultiSourceRouter、故障转移 | 高级开发者 |
| [error-handling.md](advanced/error-handling.md) | 异常体系、错误处理最佳实践 | 所有开发者 |
| [cache.md](advanced/cache.md) | 缓存系统、性能优化技巧 | 性能优化者 |
| [performance.md](advanced/performance.md) | 性能基准、优化策略、监控方法 | 运维/架构师 |

---

## 🔨 开发文档 (development/)

为 AKShare One 做贡献的开发者准备。

| 文档 | 内容 | 用途 |
|------|------|------|
| [architecture.md](development/architecture.md) | 整体架构、设计模式、核心组件 | 理解项目 |
| [testing.md](development/testing.md) | 测试框架、编写指南、覆盖率 | 编写测试 |
| [contributing.md](development/contributing.md) | 贡献流程、规范、PR指南 | 提交代码 |
| [release-notes/v0.5.0.md](development/release-notes/v0.5.0.md) | v0.5.0 版本发布说明 | 版本历史 |

**另见**: 根目录的 [CONTRIBUTING.md](../CONTRIBUTING.md) 有简化的贡献流程。

---

## 🔄 迁移指南 (migration/)

### 从 AKShare 迁移

- **[from-akshare.md](migration/from-akshare.md)** - 从原生 AKShare 迁移到 AKShare One

包含：
- 为什么要迁移
- 关键差异（参数命名、输出格式）
- 接口映射表（20个模块）
- 迁移示例（资金流、北向资金等）
- 常见陷阱和最佳实践
- 快速参考表

---

## 📖 快速查找

### 我想...

| 需求 | 推荐文档 |
|------|----------|
| 快速开始使用 | [getting-started/quickstart.md](getting-started/quickstart.md) |
| 安装 AKShare One | [getting-started/installation.md](getting-started/installation.md) |
| 查看所有接口 | [core-api/overview.md](core-api/overview.md) |
| 获取历史数据 | [core-api/historical.md](core-api/historical.md) |
| 计算技术指标 | [core-api/indicators.md](core-api/indicators.md) |
| 获取指数数据 | [extended-modules/index.md](extended-modules/index.md) |
| ETF投资分析 | [extended-modules/etf.md](extended-modules/etf.md) |
| 可转债投资 | [extended-modules/bond.md](extended-modules/bond.md) |
| 行业板块分析 | [extended-modules/industry.md](extended-modules/industry.md) |
| 概念板块追踪 | [extended-modules/concept.md](extended-modules/concept.md) |
| 港股数据获取 | [extended-modules/hkus.md](extended-modules/hkus.md) |
| 特殊板块分析 | [extended-modules/board.md](extended-modules/board.md) |
| 新股次新跟踪 | [extended-modules/ipo.md](extended-modules/ipo.md) |
| ST股票监控 | [extended-modules/st.md](extended-modules/st.md) |
| 停复牌查询 | [extended-modules/suspended.md](extended-modules/suspended.md) |
| 使用扩展模块 | [extended-modules/overview.md](extended-modules/overview.md) |
| 资金流分析 | [extended-modules/fundflow.md](extended-modules/fundflow.md) |
| 北向资金追踪 | [extended-modules/northbound.md](extended-modules/northbound.md) |
| 估值分析 | [extended-modules/valuation.md](extended-modules/valuation.md) |
| 股东分析 | [extended-modules/shareholder.md](extended-modules/shareholder.md) |
| 了解多源架构 | [advanced/multi-source.md](advanced/multi-source.md) |
| 性能优化 | [advanced/performance.md](advanced/performance.md) |
| 错误处理 | [advanced/error-handling.md](advanced/error-handling.md) |
| 添加新数据源 | [development/architecture.md](development/architecture.md) |
| 编写测试 | [development/testing.md](development/testing.md) |
| 提交贡献 | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| 从 AKShare 迁移 | [migration/from-akshare.md](migration/from-akshare.md) |

---

## 📊 文档统计

| 类别 | 文档数 | 主要文件 |
|------|--------|----------|
| 入门指南 | 3 | installation, quickstart, examples |
| 核心API | 8 | historical, realtime, financial, etc. |
| 扩展模块 | 28 | 27个模块 + overview |
| 高级主题 | 4 | multi-source, error-handling, cache, performance |
| 开发文档 | 4 | architecture, testing, contributing, release-notes |
| 迁移指南 | 1 | from-akshare |
| **总计** | **48** | - |

---

## 🔗 外部资源

- **GitHub**: https://github.com/zwldarren/akshare-one
- **PyPI**: https://pypi.org/project/akshare-one/
- **在线文档**: https://zwldarren.github.io/akshare-one/
- **AKShare**: https://github.com/akfamily/akshare

---

## 🆕 新增模块（2024年2月）

本次文档重构新增了15个模块文档：

1. ✅ [指数数据](extended-modules/index.md)
2. ✅ [ETF基金](extended-modules/etf.md)
3. ✅ [可转债](extended-modules/bond.md)
4. ✅ [行业板块](extended-modules/industry.md)
5. ✅ [概念板块](extended-modules/concept.md)
6. ✅ [港股美股](extended-modules/hkus.md)
7. ✅ [科创板创业板](extended-modules/board.md)
8. ✅ [新股次新](extended-modules/ipo.md)
9. ✅ [ST股票](extended-modules/st.md)
10. ✅ [停复牌](extended-modules/suspended.md)
11. ✅ [估值分析](extended-modules/valuation.md)
12. ✅ [股东数据](extended-modules/shareholder.md)
13. ✅ [业绩快报](extended-modules/performance.md)
14. ✅ [分析师研报](extended-modules/analyst.md)
15. ✅ [市场情绪](extended-modules/sentiment.md)

---

**文档版本**: 3.0  
**最后更新**: 2024年2月  
**维护**: AKShare One Team
