# 架构设计

本文档介绍 AKShare One 的整体架构设计、核心组件和多数据源实现方案。

## 项目概览

AKShare One 是基于 AKShare 开发的中国A股数据接口库，旨在：

- 统一不同数据源的股票代码格式
- 标准化返回数据结构
- 简化 API 参数设计
- 提供多数据源自动故障转移

### 核心特性

- 📊 统一的股票代码格式 (6位数字)
- 🏗️ 标准化的 DataFrame 输出
- 🛠️ Factory + Provider 模式
- 🔄 MultiSourceRouter 智能路由
- ⏱️ 内置 LRU 缓存系统
- 🧪 80%+ 测试覆盖率

## 整体架构

```
akshare-one/
├── src/akshare_one/
│   ├── __init__.py              # 统一API导出
│   ├── http_client.py           # HTTP客户端（支持SSL配置）
│   ├── indicators.py            # 技术指标模块
│   ├── mcp/                     # MCP服务器实现
│   └── modules/                 # 核心数据模块
│       ├── cache.py             # 缓存系统 (@smart_cache)
│       ├── multi_source.py      # 多数据源路由器 ⭐
│       ├── utils.py             # 工具函数
│       ├── historical/          # 历史数据模块
│       │   ├── base.py          # HistoricalDataProvider 基类
│       │   ├── factory.py       # HistoricalDataFactory
│       │   ├── eastmoney_direct.py
│       │   ├── eastmoney.py
│       │   └── sina.py
│       ├── realtime/            # 实时数据模块
│       │   ├── base.py          # RealtimeDataProvider 基类
│       │   ├── factory.py       # RealtimeDataFactory
│       │   ├── eastmoney_direct.py
│       │   ├── eastmoney.py
│       │   └── xueqiu.py
│       ├── financial/           # 财务数据模块
│       │   ├── base.py          # FinancialDataProvider 基类
│       │   ├── factory.py       # FinancialDataFactory
│       │   └── sina.py
│       ├── futures/             # 期货数据模块
│       ├── options/             # 期权数据模块
│       ├── news/                # 新闻数据模块
│       ├── insider/             # 内部交易模块
│       ├── info/                # 基本信息模块
│       └── indicators/          # 技术指标计算器
├── docs/                        # 文档
├── tests/                       # 测试
└── examples/                    # 示例代码
```

## 设计模式

### 1. Factory Pattern（工厂模式）

每个模块都有对应的工厂类，用于创建和管理数据提供者。

```python
# 示例：HistoricalDataFactory
class HistoricalDataFactory:
    _providers = {
        "eastmoney": EastMoneyHistorical,
        "eastmoney_direct": EastMoneyDirectHistorical,
        "sina": SinaHistorical,
    }
    
    @classmethod
    def get_provider(cls, provider_name: str, **kwargs):
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        return provider_class(**kwargs)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """动态注册新数据源"""
        cls._providers[name.lower()] = provider_class
```

**优势**：
- 易于扩展新数据源
- 统一的创建接口
- 支持运行时动态注册

### 2. Abstract Base Class（抽象基类）

所有数据提供者都继承自抽象基类，确保接口一致性。

```python
from abc import ABC, abstractmethod

class HistoricalDataProvider(ABC):
    def __init__(self, symbol: str, interval: str, **kwargs):
        self.symbol = symbol
        self.interval = interval
    
    @abstractmethod
    def get_hist_data(self) -> pd.DataFrame:
        """返回标准格式：timestamp, open, high, low, close, volume"""
        pass
    
    def validate_symbol(self):
        """通用验证逻辑"""
        if not re.match(r'^\d{6}$', self.symbol):
            raise InvalidParameterError(f"Invalid symbol: {self.symbol}")
```

### 3. Strategy Pattern（策略模式）

MultiSourceRouter 实现了策略模式，支持多个数据源策略。

```python
# 配置多个数据源，按优先级自动选择
router = MultiSourceRouter([
    ("eastmoney_direct", provider1),  # 优先级1
    ("eastmoney", provider2),          # 优先级2
    ("sina", provider3),               # 优先级3
])

# 执行时自动尝试，直到成功
df = router.execute("get_hist_data")
```

### 4. Decorator Pattern（装饰器模式）

缓存系统使用装饰器模式，透明地添加缓存功能。

```python
from akshare_one.modules.cache import smart_cache

class MyProvider(HistoricalDataProvider):
    @smart_cache(
        realtime_key="hist_cache",
        daily_key="hist_daily_cache",
    )
    def get_hist_data(self) -> pd.DataFrame:
        # 实际数据获取逻辑
        pass
```

## 核心组件详解

### MultiSourceRouter（多数据源路由器）

**文件**: `src/akshare_one/modules/multi_source.py`

#### 核心功能

1. **自动故障转移** - 主源失败自动切换到备用源
2. **结果验证** - 必需列、最小行数检查
3. **执行统计** - 跟踪每个源的成功/失败次数
4. **详细错误跟踪** - 记录每个源的错误信息

#### ExecutionResult 类

```python
@dataclass
class ExecutionResult:
    success: bool
    data: Optional[pd.DataFrame]
    source: Optional[str]
    error: Optional[str]
    attempts: int
    error_details: List[Tuple[str, str]]  # [(source, error), ...]
```

#### 使用示例

```python
from akshare_one import create_historical_router

# 创建路由器
router = create_historical_router(
    symbol="600000",
    interval="day",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)

# 方式1：抛出异常（向后兼容）
df = router.execute("get_hist_data")

# 方式2：返回详细结果
result = router.execute_with_result("get_hist_data")
if result.success:
    print(f"数据源: {result.source}")
    df = result.data
else:
    print(f"失败: {result.error}")
    for source, error in result.error_details:
        print(f"  {source}: {error}")
```

### 缓存系统（Cache System）

**文件**: `src/akshare_one/modules/cache.py`

#### 核心特性

- **LRU 缓存** - 基于 `cachetools` 实现
- **智能键生成** - 区分实时/历史缓存
- **自动TTL** - 不同数据类型不同过期时间
- **线程安全** - 支持高并发

#### 缓存策略

| 数据类型 | TTL | 命名空间 |
|---------|-----|----------|
| 实时数据 | 5-10分钟 | `realtime_*` |
| 历史数据 | 24小时 | `daily_*` |
| 财务数据 | 24小时 | `daily_*` |

#### 性能收益

| 场景 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| 重复请求 | 500ms | <1ms | **500x** |
| 批量查询 | 5s | 50ms | **100x** |

### 数据格式标准化

#### 标准化的历史数据格式

```python
standard_hist_df = pd.DataFrame({
    'timestamp': pd.DatetimeIndex([...]),  # 时间戳
    'open': [float, ...],                  # 开盘价
    'high': [float, ...],                  # 最高价
    'low': [float, ...],                   # 最低价
    'close': [float, ...],                 # 收盘价
    'volume': [int, ...],                  # 成交量
    'amount': [float, ...],                # 成交额（可选）
})
```

#### 标准化的实时数据格式

```python
standard_realtime_df = pd.DataFrame({
    'symbol': ["600000", ...],             # 股票代码
    'price': [float, ...],                 # 最新价
    'change': [float, ...],                # 涨跌额
    'pct_change': [float, ...],            # 涨跌幅
    'timestamp': [str/datetime, ...],      # 更新时间
    'volume': [int, ...],                  # 成交量
    'amount': [float, ...],                # 成交额
})
```

#### 标准化的财务数据格式

```python
balance_sheet_df = pd.DataFrame({
    'report_date': [str, ...],             # 报告期 YYYY-MM-DD
    'total_assets': [float, ...],          # 资产总计
    'total_liabilities': [float, ...],     # 负债合计
    'shareholders_equity': [float, ...],   # 股东权益
    # ... 其他标准字段
})
```

## 数据流

### 用户请求 → 数据返回

```
用户调用
    ↓
MultiSourceRouter 接收
    ↓
按优先级遍历 Providers
    ↓
尝试 provider.get_data()
    ↓
数据验证（必需列、最小行数）
    ↓
✅ 验证通过 → 返回数据
❌ 验证失败 → 继续下一个 Provider
    ↓
所有 Provider 都失败 → 抛出异常，包含详细错误
```

### 缓存流程

```
请求到达
    ↓
生成缓存键 (基于函数名 + 参数)
    ↓
查找缓存
    ↓
缓存命中 → 立即返回 ✅
缓存未命中 → 执行实际请求
    ↓
结果写入缓存（带TTL）
    ↓
返回数据
```

## 扩展性设计

### 添加新数据源的步骤

1. **创建 Provider 类**

```python
# modules/historical/my_source.py
from .base import HistoricalDataProvider

class MySourceHistorical(HistoricalDataProvider):
    def get_hist_data(self) -> pd.DataFrame:
        # 实现数据获取
        # 返回标准格式
        pass
```

2. **在 Factory 中注册**

```python
# modules/historical/factory.py
from .my_source import MySourceHistorical

class HistoricalDataFactory:
    _providers = {
        # ... 现有源
        "my_source": MySourceHistorical,
    }
```

3. **更新路由器配置**（可选）

```python
# 在 create_historical_router 的默认列表中添加
def create_historical_router(..., sources=None):
    if sources is None:
        sources = ["eastmoney_direct", "eastmoney", "sina", "my_source"]
```

4. **编写测试**

```python
def test_my_source():
    provider = MySourceHistorical(symbol="600000", interval="day")
    df = provider.get_hist_data()
    assert not df.empty
```

### 动态注册

支持运行时注册自定义 Provider：

```python
from akshare_one.modules.historical.factory import HistoricalDataFactory
from my_package import MyCustomProvider

HistoricalDataFactory.register_provider("custom", MyCustomProvider)
```

## 异常处理

所有异常继承自 `MarketDataError`：

```
MarketDataError
├── InvalidParameterError     # 参数无效
├── DataSourceUnavailableError # 数据源不可用
├── NoDataError               # 无数据
├── UpstreamChangedError      # 上游API变更
├── RateLimitError            # 限流
└── DataValidationError       # 数据验证失败
```

### 使用建议

```python
from akshare_one.modules import (
    InvalidParameterError,
    DataSourceUnavailableError,
    MarketDataError,
)

try:
    df = get_data(...)
except InvalidParameterError:
    # 参数错误，立即返回
    return {"error": "INVALID_PARAMS"}
except DataSourceUnavailableError:
    # 数据源问题，可以重试或切换源
    return {"error": "SOURCE_UNAVAILABLE"}
except MarketDataError:
    # 其他市场数据错误
    logger.error(...)
```

详细异常说明请参考 [错误处理](./error-handling.md)。

## 配置与部署

### 环境变量

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `AKSHARE_ONE_CACHE_ENABLED` | `True` | 启用/禁用缓存 |
| `AKSHARE_ONE_LOG_LEVEL` | `WARNING` | 日志级别 |
| `AKSHARE_ONE_TIMEOUT` | `30` | 默认超时时间（秒） |

### SSL 配置

```python
from akshare_one import configure_ssl_verification

# 禁用 SSL 验证（仅调试用）
configure_ssl_verification(False)
```

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 性能考量

### 缓存策略

- **实时数据**: TTL 5-10 分钟，容量 1000 条
- **历史数据**: TTL 24 小时，容量 500 条

### 内存管理

- 及时释放大对象（`del df; gc.collect()`）
- 使用适当的数据类型（`int32` 而非 `int64`）
- 监控缓存大小，避免内存溢出

### 网络优化

- 使用会话复用（`requests.Session()`）
- 设置合理超时（连接5s，读取30s）
- 配置代理减少延迟

详细性能优化指南请参考 [性能优化](./performance.md)。

## 测试策略

### 测试层次

1. **单元测试** - 单个 Provider 功能
2. **集成测试** - MultiRouter 故障转移
3. **契约测试** - 数据格式一致性
4. **性能测试** - 响应时间和并发

### 测试覆盖率目标

- 核心模块: >80%
- 工具函数: >90%
- 异常路径: >70%

运行测试：

```bash
pytest tests/ -v --cov=akshare_one --cov-report=html
```

详细测试指南请参考 [测试文档](./testing.md)。

## 数据源优先级

### 历史数据源

| 优先级 | 数据源 | 特点 | 推荐度 |
|-------|--------|------|--------|
| 1 | eastmoney_direct | 最快、数据最全 | ⭐⭐⭐⭐⭐ |
| 2 | eastmoney | 稳定性好 | ⭐⭐⭐⭐ |
| 3 | sina | 老牌稳定 | ⭐⭐⭐ |
| 4 | tencent | 实时性强 | ⭐⭐⭐ |

### 实时数据源

| 优先级 | 数据源 | 特点 | 推荐度 |
|-------|--------|------|--------|
| 1 | eastmoney_direct | 实时性强 | ⭐⭐⭐⭐⭐ |
| 2 | eastmoney | 稳定可靠 | ⭐⭐⭐⭐ |
| 3 | xueqiu | 数据丰富 | ⭐⭐⭐ |
| 4 | tencent | 响应快 | ⭐⭐⭐ |

## 未来规划

### 短期（1-2个月）

- [ ] 添加更多数据源（tencent、ths、cninfo）
- [ ] 实现分布式缓存（Redis）
- [ ] 增强监控和告警
- ✅ 性能基准测试已包含在 [性能优化指南](../advanced/performance.md)

### 中期（3-6个月）

- [ ] 支持 WebSocket 实时推送
- [ ] 实现数据质量评分系统
- [ ] 添加 GraphQL 接口
- [ ] 优化内存使用

### 长期（6个月+）

- [ ] 支持更多国际市场
- [ ] 实现机器学习特征工程模块
- [ ] 构建数据血缘追踪系统
- [ ] 提供 SaaS 服务版本

## 总结

AKShare One 的架构设计遵循以下原则：

✅ **模块化** - 清晰的模块划分，依赖最小化
✅ **可扩展** - Factory 模式便于添加新数据源
✅ **高可用** - MultiSourceRouter 提供自动故障转移
✅ **高性能** - 智能缓存和连接复用
✅ **易维护** - 统一的异常处理和日志记录
✅ **向后兼容** - 新增功能不影响现有用户

通过这套架构，AKShare One 能够在提供简洁 API 的同时，保证系统的稳定性、可扩展性和高性能。
