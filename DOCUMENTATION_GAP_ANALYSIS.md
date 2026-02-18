# 文档与代码对比报告

## 发现的问题

经过详细检查，发现文档和代码存在显著不一致。实际代码中有很多**文档中未提及**的模块。

## 代码中存在但文档缺失的模块

### 1. Analyst（分析师）模块
- **代码路径**: `src/akshare_one/modules/analyst/`
- **导出函数**:
  - `get_analyst_rank()` - 获取分析师排名
  - `get_research_report()` - 获取个股研报
- **文档状态**: ❌ 完全缺失
- **建议**: 新建 `docs/extended-modules/analyst.md`

### 2. Bond（债券）模块
- **代码路径**: `src/akshare_one/modules/bond/`
- **导出函数**:
  - `get_bond_list()` - 可转债列表
  - `get_bond_hist_data()` - 债券历史数据
  - `get_bond_realtime_data()` - 债券实时行情
- **文档状态**: ⚠️ 只有占位符 `docs/api/bonds.md`（未迁移）
- **建议**: 新建 `docs/extended-modules/bonds.md`

### 3. ETF 模块
- **代码路径**: `src/akshare_one/modules/etf/`
- **导出函数**:
  - `get_etf_hist_data()` - ETF历史数据
  - `get_etf_realtime_data()` - ETF实时行情
  - `get_etf_list()` - ETF列表
  - `get_fund_manager_info()` - 基金经理信息
  - `get_fund_rating_data()` - 基金评级
- **文档状态**: ❌ 完全缺失
- **建议**: 新建 `docs/extended-modules/etf.md`

### 4. Index（指数）模块
- **代码路径**: `src/akshare_one/modules/index/`
- **导出函数**:
  - `get_index_hist_data()` - 指数历史数据
  - `get_index_realtime_data()` - 指数实时行情
  - `get_index_list()` - 指数列表
  - `get_index_constituents()` - 指数成分股
- **文档状态**: ❌ 完全缺失
- **建议**: 新建 `docs/extended-modules/index.md`

### 5. Performance（业绩）模块
- **代码路径**: `src/akshare_one/modules/performance/`
- **导出函数**:
  - `get_performance_forecast()` - 业绩预告
  - `get_performance_express()` - 业绩快报
- **文档状态**: ❌ 完全缺失
- **建议**: 新建 `docs/extended-modules/performance.md`

### 6. Sentiment（情绪）模块
- **代码路径**: `src/akshare_one/modules/sentiment/`
- **导出函数**:
  - `get_hot_rank()` - 热度排行
  - `get_stock_sentiment()` - 个股情绪
- **文档状态**: ❌ 完全缺失
- **建议**: 新建 `docs/extended-modules/sentiment.md`

### 7. Shareholder（股东）模块
- **代码路径**: `src/akshare_one/modules/shareholder/`
- **导出函数**:
  - `get_shareholder_changes()` - 股东增减持
  - `get_top_shareholders()` - 十大股东
  - `get_institution_holdings()` - 机构持仓
- **文档状态**: ❌ 完全缺失
- **建议**: 新建 `docs/extended-modules/shareholder.md`

### 8. Valuation（估值）模块
- **代码路径**: `src/akshare_one/modules/valuation/`
- **导出函数**:
  - `get_stock_valuation()` - 个股估值（PE/PB/PS等）
  - `get_market_valuation()` - 市场估值
- **文档状态**: ❌ 完全缺失
- **建议**: 新建 `docs/extended-modules/valuation.md`

### 9. LHB（龙虎榜）模块
- **代码路径**: `src/akshare_one/modules/lhb/`
- **文档状态**: ⚠️ 存在但文件名不一致
- **文档文件**: `docs/extended-modules/dragon-tiger.md`
- **问题**: 代码用 `lhb`，文档用 `dragon-tiger`

### 10. LimitUp（涨停池）模块
- **代码路径**: `src/akshare_one/modules/limitup/`
- **文档状态**: ⚠️ 存在但文件名不一致
- **文档文件**: `docs/extended-modules/limit-up-down.md`
- **问题**: 代码用 `limitup`，文档用 `limit-up-down`

### 11. Pledge（股权质押）模块
- **代码路径**: `src/akshare_one/modules/pledge/`
- **文档状态**: ⚠️ 存在但文件名不一致
- **文档文件**: `docs/extended-modules/equity-pledge.md`
- **问题**: 代码用 `pledge`，文档用 `equity-pledge`

### 12. Restricted（限售解禁）模块
- **代码路径**: `src/akshare_one/modules/restricted/`
- **文档状态**: ⚠️ 存在但文件名不一致
- **文档文件**: `docs/extended-modules/restricted-release.md`
- **问题**: 代码用 `restricted`，文档用 `restricted-release`

### 13. BlockDeal（大宗交易）模块
- **代码路径**: `src/akshare_one/modules/blockdeal/`
- **文档状态**: ⚠️ 存在但文件名不一致
- **文档文件**: `docs/extended-modules/block-deals.md`
- **问题**: 代码用 `blockdeal`，文档用 `block-deals`

## 命名不一致总结

| 代码目录 | 文档文件 | 建议统一为 |
|---------|---------|-----------|
| `lhb/` | `dragon-tiger.md` | `lhb.md` 或保持 `dragon-tiger.md` |
| `limitup/` | `limit-up-down.md` | `limitup.md` 或保持 `limit-up-down.md` |
| `pledge/` | `equity-pledge.md` | 保持 `equity-pledge.md`（更清晰） |
| `restricted/` | `restricted-release.md` | 保持 `restricted-release.md`（更清晰） |
| `blockdeal/` | `block-deals.md` | 保持 `block-deals.md`（更清晰） |

## 建议的文档补充计划

### 高优先级（核心功能）
1. **Index 模块** - 指数数据是基础功能
2. **ETF 模块** - ETF数据需求量大
3. **Bond 模块** - 可转债数据很重要
4. **Valuation 模块** - 估值分析必备

### 中优先级（分析功能）
5. **Shareholder 模块** - 股东分析
6. **Performance 模块** - 业绩分析
7. **Analyst 模块** - 研报分析

### 低优先级（特色功能）
8. **Sentiment 模块** - 情绪指标

## 当前文档统计

| 类别 | 现有文档数 | 应有文档数 | 缺失 |
|------|-----------|-----------|------|
| 入门指南 | 3 | 3 | 0 |
| 核心API | 8 | 8 | 0 |
| 扩展模块 | 13 | 21 | 8 |
| 高级主题 | 4 | 4 | 0 |
| 开发文档 | 5 | 5 | 0 |
| 迁移指南 | 1 | 1 | 0 |
| **总计** | **34** | **42** | **8** |

## 缺失文档详情

### 完全缺失（8个）
1. `docs/extended-modules/analyst.md`
2. `docs/extended-modules/bonds.md`
3. `docs/extended-modules/etf.md`
4. `docs/extended-modules/index.md`
5. `docs/extended-modules/performance.md`
6. `docs/extended-modules/sentiment.md`
7. `docs/extended-modules/shareholder.md`
8. `docs/extended-modules/valuation.md`

## 需要更新的文件

### 1. 扩展模块概览
- **文件**: `docs/extended-modules/overview.md`
- **需要**: 添加8个新模块的介绍

### 2. 文档索引
- **文件**: `DOCS_INDEX.md`, `QUICK_START_GUIDE.md`
- **需要**: 更新模块列表和链接

### 3. MkDocs 配置
- **文件**: `mkdocs.yml`
- **需要**: 添加新模块到导航

## 代码质量评估

### 优点
- ✅ 所有模块都有完整的 `__init__.py` 导出
- ✅ 都有 docstring 说明
- ✅ 都有 Factory 模式实现
- ✅ 参数和返回值类型清晰

### 发现的问题
- ⚠️ `performance` 模块的 `date` 参数格式为 `YYYYMMDD`，与其他模块的 `YYYY-MM-DD` 不一致
- ⚠️ 部分模块缺少 `source` 参数的可选值说明

## 建议操作

1. **立即行动**: 创建8个缺失模块的基础文档
2. **短期**: 更新概览文档和导航索引
3. **中期**: 统一命名规范（可选）
4. **长期**: 完善所有文档的细节和示例

## 下一步

是否需要我：
1. 创建这8个缺失模块的文档？
2. 更新扩展模块概览？
3. 更新 MkDocs 配置？
4. 修复命名不一致问题？

请告诉我您的优先级和决策。
