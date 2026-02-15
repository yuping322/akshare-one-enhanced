# API 文档目录

本目录包含 AKShare One 的完整 API 文档。

## 📚 文档结构

### 总览文档
- **[overview.md](overview.md)** - API 概览和快速导航

### 核心数据接口
这些接口可以直接从 `akshare_one` 模块导入：

- **[basic-info.md](basic-info.md)** - `get_basic_info()` - 获取股票基础信息
- **[historical.md](historical.md)** - `get_hist_data()` - 获取历史行情数据
- **[realtime.md](realtime.md)** - `get_realtime_data()` - 获取实时行情数据
- **[financial.md](financial.md)** - 财务数据接口
  - `get_balance_sheet()` - 资产负债表
  - `get_income_statement()` - 利润表
  - `get_cash_flow()` - 现金流量表
  - `get_financial_metrics()` - 财务关键指标
- **[news.md](news.md)** - `get_news_data()` - 获取个股新闻
- **[futures.md](futures.md)** - 期货数据接口
  - `get_futures_hist_data()` - 期货历史数据
  - `get_futures_realtime_data()` - 期货实时行情
  - `get_futures_main_contracts()` - 期货主力合约
- **[options.md](options.md)** - 期权数据接口
  - `get_options_chain()` - 期权链
  - `get_options_realtime()` - 期权实时行情
  - `get_options_expirations()` - 期权到期日
  - `get_options_hist()` - 期权历史数据
- **[insider.md](insider.md)** - `get_inner_trade_data()` - 内部交易数据
- **[indicators.md](indicators.md)** - 技术指标参考

### 扩展数据接口
这些接口需要从子模块导入，如 `from akshare_one.modules.fundflow import get_stock_fund_flow`：

- **[fundflow.md](fundflow.md)** - 资金流模块
  - 个股资金流、板块资金流、主力资金排名
- **[disclosure.md](disclosure.md)** - 公告信披模块
  - 公告数据、分红派息、股票回购、ST/退市风险
- **[northbound.md](northbound.md)** - 北向资金模块
  - 北向资金流向、持股明细、排名
- **[macro.md](macro.md)** - 宏观数据模块
  - LPR利率、PMI指数、CPI/PPI、M2货币供应、Shibor利率
- **[blockdeal.md](blockdeal.md)** - 大宗交易模块
  - 大宗交易明细和统计
- **[lhb.md](lhb.md)** - 龙虎榜模块
  - 龙虎榜数据、统计、营业部活跃度
- **[limitup.md](limitup.md)** - 涨停池模块
  - 涨停池、跌停池、涨停统计
- **[margin.md](margin.md)** - 融资融券模块
  - 融资融券数据和统计
- **[pledge.md](pledge.md)** - 股权质押模块
  - 股权质押数据和比例排名
- **[restricted.md](restricted.md)** - 限售解禁模块
  - 限售解禁数据和日历
- **[goodwill.md](goodwill.md)** - 商誉模块
  - 商誉数据和减值统计
- **[esg.md](esg.md)** - ESG评级模块
  - ESG评级和排名

## 🔍 如何使用

### 核心接口使用
```python
from akshare_one import get_hist_data, get_realtime_data

# 获取历史数据
df_hist = get_hist_data("600000", interval="day")

# 获取实时数据
df_realtime = get_realtime_data("600000")
```

### 扩展接口使用
```python
from akshare_one.modules.fundflow import get_stock_fund_flow
from akshare_one.modules.northbound import get_northbound_flow

# 获取资金流数据
df_flow = get_stock_fund_flow("600000", start_date="2024-01-01")

# 获取北向资金数据
df_north = get_northbound_flow(start_date="2024-01-01")
```

## 📝 文档约定

所有接口文档遵循统一格式：
- **函数签名** - 完整的函数定义
- **参数说明** - 详细的参数表格（类型、必填、默认值、描述、示例）
- **返回值** - 返回的 DataFrame 列说明
- **异常** - 可能抛出的异常类型
- **使用示例** - 实际代码示例

## 🔗 相关资源

- [示例程序](../../examples/) - 完整的使用示例
- [异常处理](../exceptions.md) - 异常类型和处理方法
- [项目主页](../../README.md) - 项目介绍和安装指南
