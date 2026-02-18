# 多数据源架构

## 概述

AKShare One 采用多数据源架构，通过 MultiSourceRouter 提供自动故障转移、结果验证和执行统计功能。这大大提高了系统的可靠性和可用性。

## 核心特性

### MultiSourceRouter 升级亮点

| 功能 | 说明 | 使用场景 |
|------|------|---------|
| **结果验证** | 必需列检查、最小行数检查 | 数据质量保证 |
| **执行统计** | 追踪每个源的成功/失败次数 | 性能监控 |
| **详细跟踪** | `ExecutionResult` 包含执行信息 | 故障诊断 |
| **无异常执行** | `execute_with_result()` 不抛异常 | 容错流程 |
| **智能故障转移** | 按优先级自动切换源 | 高可用性 |

### 预期收益

```
单源 → 多源升级

数据可用性:  90% → 95%+  (+5%)
源平均数:    1.5 → 3-4   (+150%)
故障恢复:    手动 → <1秒 (自动)
支持接口:    21 → 100+   (+380%)
```

## 核心组件

### ExecutionResult 类

```python
from dataclasses import dataclass
from typing import Optional, List, Tuple
import pandas as pd

@dataclass
class ExecutionResult:
    """执行结果包装类"""
    success: bool                              # 是否成功
    data: Optional[pd.DataFrame]               # 返回数据
    source: Optional[str]                      # 成功的数据源
    error: Optional[str]                       # 错误信息
    attempts: int                              # 尝试次数
    error_details: List[Tuple[str, str]]       # 详细错误列表 [(source, error), ...]
```

### MultiSourceRouter 类

```python
class MultiSourceRouter:
    def __init__(
        self,
        providers: List[Tuple[str, Any]],
        required_columns: Optional[List[str]] = None,
        min_rows: int = 1,
    ):
        """
        初始化多源路由器
        
        Args:
            providers: (源名称, 提供者实例) 列表
            required_columns: 必需列验证
            min_rows: 最小行数要求
        """
    
    def execute(self, method_name: str, *args, **kwargs) -> pd.DataFrame:
        """执行方法，失败时抛出异常"""
    
    def execute_with_result(self, method_name: str, *args, **kwargs) -> ExecutionResult:
        """执行方法，返回详细结果，不抛异常"""
    
    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """获取每个源的执行统计"""
```

## 使用示例

### 基本用法

```python
from akshare_one import create_historical_router

# 自动尝试多个源
router = create_historical_router(
    symbol="600000",
    interval="day",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)

df = router.execute("get_hist_data")
print(df.head())
```

### 获取详细信息

```python
result = router.execute_with_result("get_hist_data")

if result.success:
    print(f"✅ 数据源: {result.source}")
    print(f"📊 数据行数: {len(result.data)}")
    df = result.data
else:
    print(f"❌ 失败，尝试次数: {result.attempts}")
    for source, error in result.error_details:
        print(f"   {source}: {error}")
```

### 查看执行统计

```python
stats = router.get_stats()
# 输出示例:
# {
#   'eastmoney_direct': {'success': 10, 'failure': 2},
#   'eastmoney': {'success': 5, 'failure': 0},
#   'sina': {'success': 3, 'failure': 1}
# }
```

## 数据验证

路由器支持数据验证，确保返回的数据质量：

```python
router = MultiSourceRouter(
    providers=[...],
    required_columns=["timestamp", "open", "high", "low", "close", "volume"],
    min_rows=10,  # 至少返回10行数据
)
```

### 验证规则

1. **必需列检查**：确保 DataFrame 包含所有必需列
2. **最小行数检查**：确保返回足够的数据量
3. **数据类型检查**：验证列的数据类型（可选）

## 配置数据源优先级

### 默认优先级

各模块有预定义的默认优先级：

**历史数据**：
1. `eastmoney_direct` - 最快、最完整
2. `eastmoney` - 备用、数据一致
3. `sina` - 应急备用
4. `tencent` - 特定需求

**实时数据**：
1. `eastmoney_direct`
2. `eastmoney`
3. `xueqiu`
4. `tencent`

### 自定义优先级

```python
# 自定义源顺序
router = create_historical_router(
    symbol="600000",
    sources=["sina", "eastmoney_direct", "tencent"]  # 新浪优先
)
```

## 架构设计原则

### 1. 透明故障转移

用户调用不变，自动尝试多个源，第一个成功源返回。

### 2. 质量保证

- 必需列验证
- 最小行数检查
- 数据类型验证

### 3. 易于扩展

- Factory Pattern
- 支持动态注册
- 标准基类接口

### 4. 向后兼容

- 现有 API 不变
- 新增功能可选
- 渐进式升级

## 添加新数据源

### 步骤概述

1. **创建提供者类** - 继承对应的基类
2. **实现核心方法** - `get_hist_data()` 等
3. **在工厂中注册** - 更新 `factory.py`
4. **更新路由器配置** - 添加到默认源列表
5. **编写测试** - 单元测试和集成测试

### 详细指南

- [开发文档/架构设计](../development/architecture.md)
- [开发文档/贡献指南](../development/contributing.md)
- [异常处理](./error-handling.md)
- [缓存系统](./cache.md)

## 总结

多数据源架构是 AKShare One 的核心特性，它提供了：

✅ **高可用性** - 单点故障不影响整体服务
✅ **智能路由** - 自动选择最佳数据源
✅ **质量保证** - 严格的数据验证
✅ **易于维护** - 清晰的架构设计
✅ **性能优化** - 内置缓存和连接复用

通过合理配置和使用 MultiSourceRouter，可以显著提升数据获取的可靠性和效率。
