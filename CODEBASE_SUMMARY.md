# AKShare One 代码库总结

## 📋 项目概览

**AKShare One** 是一个基于 [AKShare](https://github.com/akfamily/akshare) 开发的中国A股数据接口库，旨在简化 AKShare 的使用，统一不同数据源的输入输出格式，使数据更容易传递给大语言模型（LLM）。

**当前版本**: 0.5.0
**Python 要求**: >=3.10
**许可证**: MIT

## 🎯 核心特性

### 1. 统一的数据接口
- 📊 **统一股票代码格式**：自动处理不同数据源的代码格式差异
- 🏗️ **标准化数据结构**：所有数据源返回一致的 DataFrame 格式
- 🛠️ **简化的 API 设计**：精简参数，易于使用
- ⏱️ **自动处理**：时间戳自动转换、复权数据自动处理

### 2. 多数据源支持与自动容错
- **自动故障转移**：当一个数据源失败时，自动切换到备用源
- **智能路由**：MultiSourceRouter 提供优先级配置和自动降级
- **详细的执行统计**：跟踪每个数据源的成功/失败次数
- **结果验证**：检查必需列、最小行数等数据质量要求

### 3. 丰富的数据类型
支持 8 大类数据接口：
- 历史行情数据（OHLCV）
- 实时行情数据
- 财务报表（资产负债表、利润表、现金流量表）
- 期货数据
- 期权数据
- 个股新闻
- 内部交易
- 股票基本信息

## 🏗️ 架构设计

### 整体架构

```
akshare-one/
├── src/akshare_one/
│   ├── __init__.py              # 统一API导出
│   ├── http_client.py           # HTTP客户端（支持SSL配置）
│   ├── indicators.py            # 技术指标模块
│   ├── eastmoney/               # 东方财富客户端
│   ├── mcp/                     # MCP服务器实现
│   └── modules/                 # 核心数据模块
│       ├── cache.py             # 缓存系统
│       ├── multi_source.py      # 多数据源路由器
│       ├── utils.py             # 工具函数
│       ├── historical/          # 历史数据模块
│       ├── realtime/            # 实时数据模块
│       ├── financial/           # 财务数据模块
│       ├── futures/             # 期货数据模块
│       ├── options/             # 期权数据模块
│       ├── news/                # 新闻数据模块
│       ├── insider/             # 内部交易模块
│       ├── info/                # 基本信息模块
│       └── indicators/          # 技术指标计算器
```

### 设计模式

#### 1. 工厂模式（Factory Pattern）
每个数据模块都有对应的工厂类，用于创建和管理数据提供者：

```python
# 示例：HistoricalDataFactory
class HistoricalDataFactory:
    _providers = {
        "eastmoney": EastMoneyHistorical,
        "eastmoney_direct": EastMoneyDirectHistorical,
        "sina": SinaHistorical,
        "tencent": TencentHistorical,
        "netease": NetEaseHistorical,
    }
    
    @classmethod
    def get_provider(cls, provider_name: str, **kwargs):
        provider_class = cls._providers.get(provider_name.lower())
        return provider_class(**kwargs)
```

**优势**：
- 易于扩展新数据源
- 统一的创建接口
- 支持运行时动态注册

#### 2. 抽象基类模式（ABC Pattern）
所有数据提供者都继承自抽象基类，确保接口一致性：

```python
class HistoricalDataProvider(ABC):
    @abstractmethod
    def get_hist_data(self) -> pd.DataFrame:
        """返回标准格式：timestamp, open, high, low, close, volume"""
        pass
```

#### 3. 策略模式（Strategy Pattern）
MultiSourceRouter 实现了策略模式，支持多个数据源策略：

```python
router = MultiSourceRouter([
    ("eastmoney_direct", provider1),  # 优先级1
    ("eastmoney", provider2),          # 优先级2
    ("sina", provider3),               # 优先级3
])
df = router.execute("get_hist_data")
```

## 📦 核心模块详解

### 1. MultiSourceRouter（多数据源路由器）

**文件位置**: [`src/akshare_one/modules/multi_source.py`](src/akshare_one/modules/multi_source.py:1)

**核心功能**：
- 自动故障转移和降级
- 结果验证（必需列、最小行数）
- 执行统计和健康监控
- 详细的错误跟踪

**关键类**：

```python
@dataclass
class ExecutionResult:
    """执行结果包装类"""
    success: bool                              # 是否成功
    data: pd.DataFrame | None                  # 返回数据
    source: str | None                         # 成功的数据源
    error: str | None                          # 错误信息
    attempts: int                              # 尝试次数
    error_details: list[tuple[str, str]]       # 详细错误列表
```

**使用示例**：

```python
# 方式1：抛出异常（向后兼容）
df = router.execute("get_hist_data")

# 方式2：返回详细结果（新增）
result = router.execute_with_result("get_hist_data")
if result.success:
    print(f"数据源: {result.source}, 行数: {len(result.data)}")
else:
    print(f"所有源都失败: {result.error}")
    for source, error in result.error_details:
        print(f"  {source}: {error}")

# 查看统计信息
stats = router.get_stats()
# {'eastmoney_direct': {'success': 10, 'failure': 2}, ...}
```

### 2. 历史数据模块（Historical）

**文件位置**: [`src/akshare_one/modules/historical/`](src/akshare_one/modules/historical/)

**支持的数据源**：
- `eastmoney_direct` - 东方财富直连（推荐）
- `eastmoney` - 东方财富（备用）
- `sina` - 新浪财经
- `tencent` - 腾讯财经
- `netease` - 网易财经

**标准输出格式**：
```
timestamp  | open | high | low | close | volume
-----------|------|------|-----|-------|-------
2024-01-01 | 10.5 | 10.8 | 10.4| 10.7  | 1000000
```

**支持的时间间隔**：
- minute（分钟）
- hour（小时）
- day（日）
- week（周）
- month（月）
- year（年）

**复权类型**：
- `none` - 不复权
- `qfq` - 前复权
- `hfq` - 后复权

### 3. 实时数据模块（Realtime）

**文件位置**: [`src/akshare_one/modules/realtime/`](src/akshare_one/modules/realtime/)

**支持的数据源**：
- `eastmoney_direct` - 东方财富直连（推荐）
- `eastmoney` - 东方财富（备用）
- `xueqiu` - 雪球

**标准输出格式**：
```
symbol | price | change | pct_change | timestamp | volume | amount | open | high | low | prev_close
-------|-------|--------|------------|-----------|--------|--------|------|------|-----|------------
600000 | 10.5  | 0.3    | 2.94       | ...       | 1000   | 10000  | 10.2 | 10.6 | 10.1| 10.2
```

### 4. 财务数据模块（Financial）

**文件位置**: [`src/akshare_one/modules/financial/`](src/akshare_one/modules/financial/)

**支持的数据源**：
- `sina` - 新浪财经（推荐）
- `eastmoney_direct` - 东方财富直连
- `cninfo` - 巨潮资讯网

**提供的报表**：
- 资产负债表 - [`get_balance_sheet()`](src/akshare_one/__init__.py:189)
- 利润表 - [`get_income_statement()`](src/akshare_one/__init__.py:202)
- 现金流量表 - [`get_cash_flow()`](src/akshare_one/__init__.py:215)
- 财务指标 - [`get_financial_metrics()`](src/akshare_one/__init__.py:228)

### 5. 技术指标模块（Indicators）

**文件位置**: [`src/akshare_one/indicators.py`](src/akshare_one/indicators.py:1)

**支持的计算引擎**：
- `talib` - TA-Lib库（需要单独安装，更准确）
- `simple` - 内置简单实现（无需额外依赖）

**支持的指标**（38种+）：

**趋势指标**：
- SMA - 简单移动平均
- EMA - 指数移动平均
- MACD - 移动平均收敛散度
- ADX - 平均趋向指数
- AROON - 阿隆指标

**震荡指标**：
- RSI - 相对强弱指数
- STOCH - 随机指标
- CCI - 商品通道指数
- WILLR - 威廉指标
- MFI - 资金流量指标
- CMO - 钱德动量摆动指标

**波动率指标**：
- BOLL - 布林带
- ATR - 平均真实波幅

**成交量指标**：
- OBV - 能量潮
- AD - 累积/派发线
- ADOSC - 累积/派发震荡指标

**动量指标**：
- MOM - 动量指标
- ROC - 变动率
- TRIX - 三重指数平滑移动平均

**使用示例**：
```python
from akshare_one import get_hist_data
from akshare_one.indicators import get_sma, get_macd, get_rsi

# 获取历史数据
df = get_hist_data("600000", interval="day")

# 计算20日均线
df = get_sma(df, window=20)

# 计算MACD
df = get_macd(df, fast=12, slow=26, signal=9)

# 计算RSI
df = get_rsi(df, window=14)
```

### 6. MCP服务器模块

**文件位置**: [`src/akshare_one/mcp/server.py`](src/akshare_one/mcp/server.py:1)

**用途**: 通过 Model Context Protocol (MCP) 协议提供数据接口，可以与 Claude、GPT 等 AI 工具集成。

**启动方式**：
```bash
akshare-one-mcp
```

**提供的工具**：
- `get_hist_data` - 获取历史数据（支持自动计算技术指标）
- `get_realtime_data` - 获取实时数据
- `get_balance_sheet` - 获取资产负债表
- `get_income_statement` - 获取利润表
- `get_cash_flow` - 获取现金流量表
- `get_basic_info` - 获取股票基本信息
- `get_news_data` - 获取个股新闻
- 其他 AKShare 原生接口

### 7. 缓存系统

**文件位置**: [`src/akshare_one/modules/cache.py`](src/akshare_one/modules/cache.py:1)

使用 `cachetools` 库实现了 LRU 缓存，减少重复请求，提高性能。

## 🔌 API 接口概览

### 基础数据接口

| 函数名 | 功能 | 支持的数据源 |
|--------|------|-------------|
| [`get_basic_info()`](src/akshare_one/__init__.py:77) | 股票基本信息 | eastmoney |
| [`get_hist_data()`](src/akshare_one/__init__.py:100) | 历史行情数据 | eastmoney_direct, eastmoney, sina, tencent, netease |
| [`get_realtime_data()`](src/akshare_one/__init__.py:141) | 实时行情数据 | eastmoney_direct, eastmoney, xueqiu |
| [`get_news_data()`](src/akshare_one/__init__.py:169) | 个股新闻 | eastmoney, sina |

### 财务数据接口

| 函数名 | 功能 | 支持的数据源 |
|--------|------|-------------|
| [`get_balance_sheet()`](src/akshare_one/__init__.py:189) | 资产负债表 | sina, eastmoney_direct, cninfo |
| [`get_income_statement()`](src/akshare_one/__init__.py:202) | 利润表 | sina, eastmoney_direct, cninfo |
| [`get_cash_flow()`](src/akshare_one/__init__.py:215) | 现金流量表 | sina, eastmoney_direct, cninfo |
| [`get_financial_metrics()`](src/akshare_one/__init__.py:228) | 财务指标 | sina, eastmoney_direct |

### 衍生品接口

| 函数名 | 功能 | 支持的数据源 |
|--------|------|-------------|
| `get_futures_hist_data()` | 期货历史数据 | sina |
| `get_futures_realtime_data()` | 期货实时数据 | sina |
| `get_futures_main_contracts()` | 期货主力合约 | sina |
| `get_options_chain()` | 期权链 | sina |
| `get_options_realtime()` | 期权实时数据 | sina |
| `get_options_hist()` | 期权历史数据 | sina |

### 其他接口

| 函数名 | 功能 | 支持的数据源 |
|--------|------|-------------|
| `get_inner_trade_data()` | 内部交易数据 | xueqiu |

### 多数据源接口（高级）

所有基础接口都有对应的 `_multi_source` 版本，返回 `ExecutionResult` 对象：

- `get_basic_info_multi_source()`
- `get_hist_data_multi_source()`
- `get_realtime_data_multi_source()`
- `get_news_data_multi_source()`
- `get_inner_trade_data_multi_source()`
- `get_financial_data_multi_source()`
- `get_financial_metrics_multi_source()`

## 🚀 使用示例

### 基础使用

```python
from akshare_one import get_hist_data, get_realtime_data

# 获取历史数据（日线，前复权）
df = get_hist_data(
    symbol="600000",           # 浦发银行
    interval="day",            # 日线
    adjust="qfq",              # 前复权
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 获取实时行情
df = get_realtime_data(symbol="600000")

# 获取财务报表
from akshare_one import get_balance_sheet, get_income_statement

balance = get_balance_sheet("600000")
income = get_income_statement("600000")
```

### 技术指标计算

```python
from akshare_one import get_hist_data
from akshare_one.indicators import (
    get_sma, get_ema, get_rsi, get_macd, 
    get_bollinger_bands, get_atr
)

# 获取数据
df = get_hist_data("600000", interval="day")

# 计算各种技术指标
df = get_sma(df, window=20)              # 20日均线
df = get_ema(df, window=12)              # 12日指数均线
df = get_rsi(df, window=14)              # 14日RSI
df = get_macd(df)                        # MACD
df = get_bollinger_bands(df)             # 布林带
df = get_atr(df, window=14)              # ATR波动率

print(df.tail())
```

### 多数据源使用

```python
from akshare_one import (
    create_historical_router,
    get_hist_data_multi_source
)

# 方式1：使用预定义路由器
result = get_hist_data_multi_source(
    symbol="600000",
    interval="day"
)

if result.success:
    print(f"成功从 {result.source} 获取数据")
    print(result.data.head())
else:
    print(f"所有源都失败: {result.error}")
    for source, error in result.error_details:
        print(f"  {source}: {error}")

# 方式2：自定义路由器
router = create_historical_router(
    symbol="600000",
    interval="day",
    sources=["sina", "eastmoney"]  # 自定义优先级
)

df = router.execute("get_hist_data")
```

### SSL 配置

```python
from akshare_one import configure_ssl_verification

# 在某些环境中可能需要禁用SSL验证
configure_ssl_verification(verify=False)

# 然后正常使用API
df = get_hist_data("600000")
```

## 📊 数据源对比

### 历史数据源特点

| 数据源 | 优势 | 劣势 | 推荐度 |
|--------|------|------|--------|
| eastmoney_direct | 速度快，数据全 | 可能有限流 | ⭐⭐⭐⭐⭐ |
| eastmoney | 稳定性好 | 速度较慢 | ⭐⭐⭐⭐ |
| sina | 老牌稳定 | 更新较慢 | ⭐⭐⭐ |
| tencent | 数据准确 | 接口较少 | ⭐⭐⭐ |
| netease | 数据格式好 | 速度一般 | ⭐⭐ |

### 实时数据源特点

| 数据源 | 优势 | 劣势 | 推荐度 |
|--------|------|------|--------|
| eastmoney_direct | 实时性强 | 限流风险 | ⭐⭐⭐⭐⭐ |
| eastmoney | 稳定可靠 | 延迟略高 | ⭐⭐⭐⭐ |
| xueqiu | 数据丰富 | 需要登录 | ⭐⭐⭐ |

## 🧪 测试覆盖

项目包含完整的测试套件：

```
tests/
├── test_stock.py                      # 基础功能测试
├── test_financial.py                  # 财务数据测试
├── test_futures.py                    # 期货数据测试
├── test_options.py                    # 期权数据测试
├── test_indicators.py                 # 技术指标测试
├── test_info.py                       # 基本信息测试
├── test_insider.py                    # 内部交易测试
├── test_news.py                       # 新闻数据测试
├── test_mcp.py                        # MCP服务器测试
├── test_multi_source_enhanced.py      # 多源增强功能测试
├── test_multi_source_comprehensive.py # 多源综合测试
└── test_new_data_sources.py          # 新数据源测试
```

**运行测试**：
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_stock.py

# 运行并查看覆盖率
pytest --cov=akshare_one --cov-report=html
```

## 📝 开发规范

### 代码质量工具

项目使用以下工具确保代码质量：

- **Ruff**: 代码检查和格式化（替代 flake8、isort、black）
- **MyPy**: 静态类型检查
- **Pyright**: 类型检查（VSCode 支持）
- **pre-commit**: Git 提交前自动检查

**配置文件**: [`pyproject.toml`](pyproject.toml:52)

### 添加新数据源的步骤

1. **创建提供者类**：
   ```python
   # 在 modules/historical/ 下创建新文件
   from .base import HistoricalDataProvider
   
   class NewSourceHistorical(HistoricalDataProvider):
       def get_hist_data(self) -> pd.DataFrame:
           # 实现数据获取逻辑
           pass
   ```

2. **在工厂中注册**：
   ```python
   # 在 factory.py 中添加
   _providers = {
       # ...
       "newsource": NewSourceHistorical,
   }
   ```

3. **编写测试**：
   ```python
   # 在 tests/ 中添加测试
   def test_newsource_historical():
       df = get_hist_data("600000", source="newsource")
       assert not df.empty
   ```

4. **更新文档**：
   - 更新 README.md
   - 添加 API 文档
   - 更新数据源对比表

详细指南请参考: [`docs/design/多源实现指南.md`](docs/design/多源实现指南.md:1)

## 🔄 项目演进

### 最近更新（2026-02-12）

**多源架构增强**：
- ✅ MultiSourceRouter 升级（结果验证、执行统计）
- ✅ ExecutionResult 类（详细错误跟踪）
- ✅ 新增 `execute_with_result()` 方法
- ✅ 完善的设计文档体系

### 未来计划

**第一优先级**（1-2周）：
1. 历史数据扩展 - 添加 tencent、163(网易) 源
2. 实时数据扩展 - 添加 tencent、ths 源
3. 财务数据扩展 - 添加 cninfo、eastmoney 源

**第二优先级**（2-4周）：
1. 基本信息多源 - 添加 sina、xueqiu 源
2. 新闻数据多源 - 添加 sina、163 源
3. 内部交易多源 - 添加 eastmoney、cninfo 源

详细计划请参考: [`docs/design/多源实现完成总结.md`](docs/design/多源实现完成总结.md:80)

## 📚 文档资源

### 核心文档

- [`README.md`](README.md:1) - 项目介绍（英文）
- [`README_zh.md`](README_zh.md:1) - 项目介绍（中文）
- [在线文档](https://zwldarren.github.io/akshare-one/) - 完整 API 文档

### 设计文档

- [`多数据源实现研究报告.md`](docs/design/多数据源实现研究报告.md:1) - AKShare 架构分析
- [`多源实现指南.md`](docs/design/多源实现指南.md:1) - 新数据源添加指南
- [`多源集成快速参考.md`](docs/design/多源集成快速参考.md:1) - 快速参考手册
- [`多源实现完成总结.md`](docs/design/多源实现完成总结.md:1) - 实现进展总结

### API 文档

```
docs/api/
├── overview.md        # API 概览
├── historical.md      # 历史数据 API
├── realtime.md        # 实时数据 API
├── financial.md       # 财务数据 API
├── futures.md         # 期货数据 API
├── options.md         # 期权数据 API
├── news.md            # 新闻数据 API
├── insider.md         # 内部交易 API
├── basic-info.md      # 基本信息 API
└── indicators.md      # 技术指标 API
```

## 🔧 技术栈

### 核心依赖

- **akshare** (>=1.17.80) - 底层数据接口
- **pandas** - 数据处理
- **requests** - HTTP 客户端
- **cachetools** (>=5.5.0) - 缓存系统

### 可选依赖

- **ta-lib** (>=0.6.4) - 技术指标计算（更准确）
- **fastmcp** (>=2.11.3) - MCP 服务器
- **pydantic** (>=2.0.0) - 数据验证
- **uvicorn** (>=0.35.0) - ASGI 服务器

### 开发依赖

- **pytest** - 单元测试
- **pytest-cov** - 测试覆盖率
- **ruff** - 代码检查和格式化
- **mypy** - 静态类型检查
- **pre-commit** - Git 钩子
- **mkdocs-material** - 文档生成

## 🎓 最佳实践

### 1. 数据获取建议

```python
# ✅ 推荐：使用默认数据源（已优化）
df = get_hist_data("600000")

# ✅ 推荐：使用多源接口（更可靠）
result = get_hist_data_multi_source("600000")

# ⚠️ 谨慎：频繁请求时注意限流
for symbol in symbols:
    df = get_hist_data(symbol)
    time.sleep(0.5)  # 添加延迟避免限流
```

### 2. 错误处理

```python
# ✅ 推荐：使用 execute_with_result
result = router.execute_with_result("get_hist_data")
if not result.success:
    # 详细错误处理
    logger.error(f"Failed: {result.error}")
    for source, error in result.error_details:
        logger.debug(f"{source}: {error}")

# ✅ 推荐：使用 try-except
try:
    df = get_hist_data("600000")
except ValueError as e:
    print(f"获取数据失败: {e}")
```

### 3. 性能优化

```python
# ✅ 推荐：批量获取后缓存
symbols = ["600000", "600001", "600002"]
data_cache = {}
for symbol in symbols:
    data_cache[symbol] = get_hist_data(symbol)

# ✅ 推荐：使用合适的时间范围
df = get_hist_data(
    "600000",
    start_date="2024-01-01",  # 限制日期范围
    end_date="2024-12-31"
)
```

## 🤝 贡献指南

### 贡献流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 规范
- 使用类型注解
- 编写文档字符串
- 添加单元测试
- 通过 pre-commit 检查

## 📊 项目统计

- **总代码行数**: ~8000+ 行
- **模块数量**: 8 个主要模块
- **支持的数据源**: 15+ 个
- **API 接口数**: 50+ 个
- **技术指标**: 38+ 种
- **测试文件**: 13 个
- **文档页面**: 20+ 页

## 🔗 相关链接

- **GitHub 仓库**: https://github.com/zwldarren/akshare-one
- **PyPI 包**: https://pypi.org/project/akshare-one/
- **在线文档**: https://zwldarren.github.io/akshare-one/
- **AKShare 项目**: https://github.com/akfamily/akshare

## 📄 许可证

MIT License - 详见 [`LICENSE`](LICENSE:1) 文件

---

**生成时间**: 2026-02-16
**文档版本**: 1.1
**对应代码版本**: 0.5.0
