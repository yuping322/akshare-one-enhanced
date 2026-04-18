# Modules 包重构技术方案

## 一、现状分析

### 1.1 当前架构问题

| 问题类型 | 具体表现 |
|---------|---------|
| **扁平化过度** | 56 个顶级条目，45+ 数据域模块平铺，缺乏层次 |
| **职责混淆** | `info` 混合 6 种功能；`sentiment` 与 `alpha/sentiment.py` 同名异义 |
| **粒度过细** | `date`(67行)、`st`、`suspended` 等功能单一却独立成包 |
| **粒度过粗** | `financial` 含 10+ 数据类型；`alpha` 混合因子/信号/回测/风控 |
| **基础与计算混杂** | 接口转换型 Provider 与计算型 Calculator 平级放置 |
| **命名不规范** | `lhb`(拼音)、`hkus`(缩写)、`info`(过于宽泛) |

### 1.2 模块分类（按计算性质）

#### 类型 A：基础数据 Provider（仅接口转换）
继承 `BaseProvider`，通过 `_execute_api_mapped()` 调用外部 API，只做列名重命名/过滤等轻量转换。

共 **40+ 模块**：historical, realtime, financial, valuation, northbound, fundflow, lhb, limitup, blockdeal, bond, options, futures, index, etf, macro, industry, concept, dividend, margin, pledge, insider, analyst, news, company, esg, goodwill, ipo, sentiment, st, suspended, restricted, disclosure, performance, shareholder, fund, fund_company, fund_manager, hkus, board, special, market

#### 类型 B：计算数据 Calculator（大量计算）
基于基础数据进行密集计算，包含 numpy/pandas 数组运算、回归分析、迭代算法等。

| 模块 | 计算内容 |
|------|---------|
| `indicators/talib.py` | 30+ 技术指标：SMA/EMA/MACD/BBANDS/RSI/ATR/ADX/STOCH |
| `indicators/simple.py` | 纯 pandas 实现：rolling/ewm/diff/线性回归/迭代循环(SAR) |
| `alpha/factors.py` | 动量、波动率、市值因子 |
| `alpha/signals.py` | RSRS(滚动OLS)、均线交叉、突破信号 |
| `alpha/backtest.py` | 累计收益、Sharpe/Sortino、最大回撤、胜率 |
| `alpha/risk.py` | ATR止损、Kelly公式、风险平价、仓位管理 |
| `alpha/preprocess.py` | 去极值、Z-Score标准化、市值/行业中性化 |

### 1.3 模块依赖关系

```
基础架构层 (base, factory_base, multi_source, exceptions, cache)
        ↓ 继承/使用
数据源层 (40+ Provider 模块)
        ↓ 依赖
计算分析层 (indicators, alpha)
```

**跨模块引用**（单向，无循环）：
- `alpha/base.py` → `date.get_trade_dates_between`
- `alpha/factors.py` → `historical.get_hist_data`, `valuation.get_stock_valuation`
- `alpha/signals.py` → `historical.get_hist_data`
- `sentiment/__init__.py` → `alpha/sentiment.py`（API 聚合，非循环）

---

## 二、目标架构设计

### 2.1 设计原则

1. **分层清晰**：基础设施 → 数据提供者 → 计算引擎 → 统一 API
2. **基础与计算分离**：Provider 仅做接口转换，Calculator 做密集计算
3. **按市场/品种分组**：A股、港股、美股、宏观；个股、ETF、基金、债券、衍生品
4. **渐进式迁移**：保持向后兼容，通过别名过渡
5. **可扩展**：新增数据源只需在对应 Provider 下添加文件

### 2.2 目录结构

```
src/akshare_one/modules/
│
├── __init__.py                          # 统一导出
│
├── core/                                # 核心基础设施
│   ├── __init__.py
│   ├── base.py                          # BaseProvider（原 base.py）
│   ├── factory.py                       # BaseFactory + create_*_router（原 factory_base.py + multi_source.py 尾部）
│   ├── cache.py                         # 缓存装饰器（原 cache.py）
│   ├── exceptions.py                    # 异常类（原 exceptions.py）
│   ├── router.py                        # MultiSourceRouter（原 multi_source.py 主体）
│   ├── calendar.py                      # 交易日历（原 date/）
│   ├── symbols.py                       # Symbol 工具函数（原 utils.py）
│   └── field_mapping/                   # 字段映射（合并 config/ + field_mappings/ + field_naming/）
│       ├── __init__.py
│       ├── standardizer.py
│       ├── mapper.py
│       ├── validator.py
│       ├── unit_converter.py
│       ├── alias_manager.py
│       └── configs/                     # JSON 配置文件
│           ├── field_mappings/
│           └── aliases/
│
├── providers/                           # 基础数据提供者（仅接口转换）
│   ├── __init__.py
│   │
│   ├── equities/                        # A 股股票
│   │   ├── __init__.py
│   │   ├── quotes/                      # 行情数据
│   │   │   ├── __init__.py
│   │   │   ├── historical/              # 历史行情（原 historical/）
│   │   │   └── realtime/                # 实时行情（原 realtime/）
│   │   ├── fundamentals/                # 基本面数据
│   │   │   ├── __init__.py
│   │   │   ├── info/                    # 基本信息（原 info/ 拆分）
│   │   │   ├── financial/               # 财务报表（原 financial/）
│   │   │   ├── valuation/               # 估值数据（原 valuation/）
│   │   │   ├── dividend/                # 分红数据（原 dividend/）
│   │   │   ├── performance/             # 业绩预告（原 performance/）
│   │   │   ├── esg/                     # ESG 评分（原 esg/）
│   │   │   └── disclosure/              # 信息披露（原 disclosure/）
│   │   ├── capital/                     # 资金流向
│   │   │   ├── __init__.py
│   │   │   ├── fundflow/                # 资金流向（原 fundflow/）
│   │   │   ├── northbound/              # 北向资金（原 northbound/）
│   │   │   └── margin/                  # 融资融券（原 margin/）
│   │   ├── corporate_events/            # 公司事件
│   │   │   ├── __init__.py
│   │   │   ├── ipo/                     # IPO（原 ipo/）
│   │   │   ├── insider/                 # 内部交易（原 insider/）
│   │   │   ├── shareholder/             # 股东数据（原 shareholder/）
│   │   │   ├── pledge/                  # 股权质押（原 pledge/）
│   │   │   ├── goodwill/                # 商誉数据（原 goodwill/）
│   │   │   ├── analyst/                 # 分析师（原 analyst/）
│   │   │   └── status/                  # 股票状态（合并 st/ + suspended/ + special/）
│   │   │       ├── st.py
│   │   │       ├── suspended.py
│   │   │       └── special.py
│   │   └── trading_events/              # 交易事件
│   │       ├── __init__.py
│   │       ├── dragon_tiger/            # 龙虎榜（原 lhb/，重命名）
│   │       ├── limit_up/                # 涨跌停（原 limitup/）
│   │       └── block_deal/              # 大宗交易（原 blockdeal/）
│   │
│   ├── funds/                           # 基金
│   │   ├── __init__.py
│   │   ├── etf/                         # ETF（原 etf/）
│   │   ├── mutual/                      # 公募基金（原 fund/）
│   │   └── entities/                    # 基金主体
│   │       ├── companies.py             # 基金公司（原 fund_company/）
│   │       └── managers.py              # 基金经理（原 fund_manager/）
│   │
│   ├── indices/                         # 指数（原 index/）
│   │
│   ├── sectors/                         # 板块/行业/概念
│   │   ├── __init__.py
│   │   ├── industry/                    # 行业（原 industry/）
│   │   ├── concept/                     # 概念（原 concept/）
│   │   └── boards/                      # 板块（原 board/，科创板/创业板）
│   │
│   ├── fixed_income/                    # 固定收益
│   │   ├── __init__.py
│   │   └── bonds/                       # 债券（原 bond/）
│   │
│   ├── derivatives/                     # 衍生品
│   │   ├── __init__.py
│   │   ├── futures/                     # 期货（原 futures/）
│   │   └── options/                     # 期权（原 options/）
│   │
│   ├── hk_equities/                     # 港股（原 hkus/ 拆分）
│   ├── us_equities/                     # 美股（原 hkus/ 拆分）
│   │
│   ├── macro/                           # 宏观经济（原 macro/）
│   ├── news/                            # 新闻资讯（原 news/）
│   └── sentiment/                       # 市场情绪原始数据（原 sentiment/ 原始数据部分）
│
├── calculators/                         # 计算模块（大量计算）
│   ├── __init__.py
│   │
│   ├── technical/                       # 技术指标
│   │   ├── __init__.py
│   │   ├── base.py                      # IndicatorFactory, BaseIndicatorCalculator
│   │   ├── talib_indicators.py          # TA-Lib 封装
│   │   └── simple_indicators.py         # 纯 pandas 实现
│   │
│   ├── factors/                         # Alpha 因子
│   │   ├── __init__.py
│   │   ├── base.py                      # FactorRegistry, 预处理工具
│   │   ├── momentum.py                  # 动量因子
│   │   ├── volatility.py                # 波动率因子
│   │   ├── size.py                      # 市值因子
│   │   └── value.py                     # 价值因子（PE/PB）
│   │
│   ├── signals/                         # 交易信号
│   │   ├── __init__.py
│   │   ├── rsrs.py                      # RSRS 择时
│   │   ├── crossover.py                 # 均线交叉
│   │   └── breakout.py                  # 突破信号
│   │
│   ├── risk/                            # 风险管理
│   │   ├── __init__.py
│   │   ├── volatility.py                # 年化波动率、ATR、regime 检测
│   │   ├── drawdown.py                  # 回撤计算、恢复时间
│   │   └── position_sizing.py           # Kelly公式、风险平价、ATR仓位
│   │
│   ├── backtest/                        # 回测引擎
│   │   ├── __init__.py
│   │   ├── metrics.py                   # Sharpe/Sortino/最大回撤/胜率
│   │   └── engine.py                    # 回测执行器
│   │
│   └── preprocessing/                   # 数据预处理
│       ├── __init__.py
│       ├── cleaning.py                  # NaN/Inf 处理、类型推断
│       ├── normalization.py             # 去极值、标准化、中性化
│       └── alignment.py                 # 交易日历对齐
│
```

所有接口直接从 `providers/` 和 `calculators/` 导出，不设置额外的 API 封装层。

### 2.3 层次职责说明

| 层次 | 职责 | 计算强度 | 依赖方向 |
|------|------|---------|---------|
| **core/** | 基础设施：基类、工厂、缓存、异常、字段映射 | 无 | 无 |
| **providers/** | 数据提供者：调用外部 API，轻量转换（列名重命名/过滤） | 低 | → core |
| **calculators/** | 计算引擎：密集计算（数组运算/回归/迭代） | 高 | → core + providers |

---

## 三、模块映射表

### 3.1 基础数据 Provider 迁移映射

| 原路径 | 新路径 | 变更类型 |
|--------|--------|---------|
| `modules/base.py` | `modules/core/base.py` | 移动 |
| `modules/factory_base.py` | `modules/core/factory.py` | 移动+合并 |
| `modules/multi_source.py` | `modules/core/factory.py` + `modules/core/router.py` | 拆分 |
| `modules/cache.py` | `modules/core/cache.py` | 移动 |
| `modules/exceptions.py` | `modules/core/exceptions.py` | 移动 |
| `modules/utils.py` | `modules/core/symbols.py` | 移动+重命名 |
| `modules/date/` | `modules/core/calendar.py` | 移动+合并 |
| `modules/config/` | `modules/core/field_mapping/configs/` | 移动 |
| `modules/field_mappings/` | `modules/core/field_mapping/configs/field_mappings/` | 移动 |
| `modules/field_naming/` | `modules/core/field_mapping/` | 移动+合并 |
| `modules/historical/` | `modules/providers/equities/quotes/historical/` | 移动 |
| `modules/realtime/` | `modules/providers/equities/quotes/realtime/` | 移动 |
| `modules/info/` | `modules/providers/equities/fundamentals/info/` | 移动+拆分 |
| `modules/financial/` | `modules/providers/equities/fundamentals/financial/` | 移动 |
| `modules/valuation/` | `modules/providers/equities/fundamentals/valuation/` | 移动 |
| `modules/dividend/` | `modules/providers/equities/fundamentals/dividend/` | 移动 |
| `modules/performance/` | `modules/providers/equities/fundamentals/performance/` | 移动 |
| `modules/esg/` | `modules/providers/equities/fundamentals/esg/` | 移动 |
| `modules/disclosure/` | `modules/providers/equities/fundamentals/disclosure/` | 移动 |
| `modules/fundflow/` | `modules/providers/equities/capital/fundflow/` | 移动 |
| `modules/northbound/` | `modules/providers/equities/capital/northbound/` | 移动 |
| `modules/margin/` | `modules/providers/equities/capital/margin/` | 移动 |
| `modules/ipo/` | `modules/providers/equities/corporate_events/ipo/` | 移动 |
| `modules/insider/` | `modules/providers/equities/corporate_events/insider/` | 移动 |
| `modules/shareholder/` | `modules/providers/equities/corporate_events/shareholder/` | 移动 |
| `modules/pledge/` | `modules/providers/equities/corporate_events/pledge/` | 移动 |
| `modules/goodwill/` | `modules/providers/equities/corporate_events/goodwill/` | 移动 |
| `modules/analyst/` | `modules/providers/equities/corporate_events/analyst/` | 移动 |
| `modules/st/` | `modules/providers/equities/corporate_events/status/st.py` | 移动+合并 |
| `modules/suspended/` | `modules/providers/equities/corporate_events/status/suspended.py` | 移动+合并 |
| `modules/special/` | `modules/providers/equities/corporate_events/status/special.py` | 移动+合并 |
| `modules/lhb/` | `modules/providers/equities/trading_events/dragon_tiger/` | 移动+重命名 |
| `modules/limitup/` | `modules/providers/equities/trading_events/limit_up/` | 移动 |
| `modules/blockdeal/` | `modules/providers/equities/trading_events/block_deal/` | 移动 |
| `modules/fund/` | `modules/providers/funds/mutual/` | 移动+重命名 |
| `modules/etf/` | `modules/providers/funds/etf/` | 移动 |
| `modules/fund_company/` | `modules/providers/funds/entities/companies.py` | 移动+合并 |
| `modules/fund_manager/` | `modules/providers/funds/entities/managers.py` | 移动+合并 |
| `modules/index/` | `modules/providers/indices/` | 移动 |
| `modules/industry/` | `modules/providers/sectors/industry/` | 移动 |
| `modules/concept/` | `modules/providers/sectors/concept/` | 移动 |
| `modules/board/` | `modules/providers/sectors/boards/` | 移动 |
| `modules/bond/` | `modules/providers/fixed_income/bonds/` | 移动 |
| `modules/futures/` | `modules/providers/derivatives/futures/` | 移动 |
| `modules/options/` | `modules/providers/derivatives/options/` | 移动 |
| `modules/hkus/` | `modules/providers/hk_equities/` + `modules/providers/us_equities/` | 移动+拆分 |
| `modules/macro/` | `modules/providers/macro/` | 移动 |
| `modules/news/` | `modules/providers/news/` | 移动 |
| `modules/sentiment/` | `modules/providers/sentiment/` | 移动（仅原始数据部分） |
| `modules/market/` | `modules/providers/equities/market_infra/` | 移动+重命名 |

### 3.2 计算模块迁移映射

| 原路径 | 新路径 | 变更类型 |
|--------|--------|---------|
| `modules/indicators/` | `modules/calculators/technical/` | 移动+重组 |
| `modules/alpha/base.py` | `modules/calculators/factors/base.py` | 移动 |
| `modules/alpha/factors.py` | `modules/calculators/factors/` | 移动+拆分 |
| `modules/alpha/signals.py` | `modules/calculators/signals/` | 移动+拆分 |
| `modules/alpha/preprocess.py` | `modules/calculators/preprocessing/normalization.py` | 移动 |
| `modules/alpha/backtest.py` | `modules/calculators/backtest/metrics.py` | 移动 |
| `modules/alpha/risk.py` | `modules/calculators/risk/` | 移动+拆分 |
| `modules/alpha/sentiment.py` | `modules/providers/sentiment/macro_indicators.py` | 移动（归入 Provider） |

---

## 四、兼容性设计

### 4.1 向后兼容策略

所有原模块路径保留为 **别名导出**，通过 `__init__.py` 转发到新位置：

```python
# modules/historical/__init__.py（保留，仅转发）
from ..providers.equities.quotes.historical import get_hist_data, HistoricalDataFactory

__all__ = ["get_hist_data", "HistoricalDataFactory"]
```

### 4.2 废弃警告

```python
import warnings

def _deprecated_warning(old_path: str, new_path: str):
    warnings.warn(
        f"Import from '{old_path}' is deprecated. Use '{new_path}' instead.",
        DeprecationWarning,
        stacklevel=3
    )
```

### 4.3 过渡期 API

```python
# modules/__init__.py
# 新路径导出
from .core import BaseProvider, BaseFactory, MultiSourceRouter
from .providers.equities.quotes.historical import get_hist_data
from .calculators.technical import calculate_sma, calculate_macd

# 旧路径别名（带废弃警告）
from .historical import get_hist_data as _get_hist_data_legacy
```

---

## 五、迁移实施计划

### 阶段一：基础设施整理（core/）

| 任务 | 详情 |
|------|------|
| 创建 `core/` 目录 | 移动 base.py, factory_base.py, cache.py, exceptions.py |
| 拆分 `multi_source.py` | Router 主体 → `router.py`；工厂辅助函数 → `factory.py` |
| 合并字段映射 | `config/` + `field_mappings/` + `field_naming/` → `core/field_mapping/` |
| 移动工具模块 | `utils.py` → `core/symbols.py`；`date/` → `core/calendar.py` |
| 添加别名导出 | 所有原路径添加转发 `__init__.py` |

### 阶段二：Provider 分组（providers/）

| 任务 | 详情 |
|------|------|
| 创建 `providers/` 目录结构 | 按 equities/funds/indices/sectors 等分组 |
| 移动 A 股 Provider | historical, realtime, financial, valuation 等 → `providers/equities/` |
| 移动基金 Provider | fund, etf, fund_company, fund_manager → `providers/funds/` |
| 移动其他 Provider | index, industry, concept, board, bond, futures, options, macro, news 等 |
| 拆分 `hkus/` | → `providers/hk_equities/` + `providers/us_equities/` |
| 合并小模块 | `st/` + `suspended/` + `special/` → `corporate_events/status/` |
| 重命名 | `lhb/` → `dragon_tiger/`；`info/` 拆分 |

### 阶段三：Calculator 重组（calculators/）

| 任务 | 详情 |
|------|------|
| 创建 `calculators/` 目录结构 | technical/factors/signals/risk/backtest/preprocessing |
| 移动 indicators | → `calculators/technical/` |
| 拆分 alpha | factors → `calculators/factors/`；signals → `calculators/signals/`；risk → `calculators/risk/` |
| 移动 sentiment 计算 | `alpha/sentiment.py` → `providers/sentiment/macro_indicators.py` |

### 阶段四：清理与验证

| 任务 | 详情 |
|------|------|
| 运行测试 | 确保所有测试通过 |
| 更新导入 | 将代码库内部导入更新为新路径 |
| 移除废弃别名 | 确认无外部依赖后移除旧路径转发 |
| 更新文档 | README, API 文档, 迁移指南 |

---

## 六、关键设计决策

### 6.1 为什么保留 Provider 的细粒度？

Provider 模块虽然功能单一，但每个对应独立的数据源适配器，细粒度有利于：
- 独立测试每个数据源
- 独立更新数据源 API 变更
- 按需加载，减少内存占用

### 6.2 为什么拆分 `info/` 模块？

原 `info/` 混合了 6 种不同职责：
- `get_basic_info` → 元数据，应归入 `fundamentals/info/`
- `get_quote_snapshot` → 实时数据，应归入 `quotes/realtime/`
- `get_daily_basic` → 每日指标，应归入 `fundamentals/info/daily_basic.py`
- `get_suspend_data` → 停牌事件，应归入 `corporate_events/status/`
- `get_stk_limit` → 涨跌停价格，应归入 `trading_events/limit_up/`
- `get_adj_factor` → 复权因子，应归入 `quotes/historical/adj_factor.py`

### 6.3 为什么 `alpha/sentiment.py` 归入 Provider？

`alpha/sentiment.py` 中的 `compute_fed_model`, `compute_crowding_ratio` 等函数：
- 直接调用 akshare API 获取原始数据
- 计算逻辑相对简单（非密集计算）
- 本质是"宏观情绪指标数据源"
- 应归入 `providers/sentiment/macro_indicators.py`

### 6.4 为什么不设 API 层？

- 直接从 `providers/` 和 `calculators/` 导出接口，减少层次
- 用户可按需自行组合，避免过度封装
- 简化架构，降低维护成本

---

## 七、风险评估与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 导入路径断裂 | 高 | 中 | 保留别名导出，添加废弃警告 |
| 测试覆盖不足 | 高 | 低 | 迁移前确保测试完备 |
| 循环依赖引入 | 中 | 低 | 严格遵循依赖方向：core → providers → calculators → api |
| 迁移周期过长 | 中 | 中 | 分阶段实施，每阶段可独立发布 |
| 文档不同步 | 低 | 高 | 迁移同时更新文档 |

---

## 八、迁移检查清单

### 8.1 每个模块迁移时需完成

- [ ] 移动文件到新位置
- [ ] 更新模块内部 import 路径
- [ ] 在原位置创建转发 `__init__.py`
- [ ] 添加废弃警告
- [ ] 运行相关测试
- [ ] 更新模块 docstring

### 8.2 全局验证

- [ ] 所有测试通过
- [ ] 无循环依赖
- [ ] 导入路径正确
- [ ] 文档已更新
- [ ] CHANGELOG 已记录
- [ ] 迁移指南已编写

---

## 九、新架构优势

| 维度 | 重构前 | 重构后 |
|------|--------|--------|
| **层次清晰度** | 扁平化，56 个顶级条目 | 4 层架构，职责明确 |
| **基础/计算分离** | 混杂 | 严格分离 |
| **模块数量** | 45+ 平铺 | 分组管理，逻辑清晰 |
| **命名规范** | 拼音/缩写混用 | 英文全称，语义明确 |
| **可扩展性** | 新增模块直接平铺 | 按领域分组，易于定位 |
| **依赖方向** | 基本单向，但有例外 | 严格单向，无例外 |
| **用户友好** | 需要知道具体模块位置 | 可按市场/品种快速定位 |
