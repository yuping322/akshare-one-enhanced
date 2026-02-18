# 缓存系统

AKShare One 内置了智能缓存系统，能够显著提升数据获取性能并减少对上游数据源的请求压力。

## 核心特性

- **LRU 缓存** - 使用 `cachetools` 库实现最近最少使用缓存
- **智能键生成** - 区分实时缓存和每日缓存
- **自动失效** - 实时数据短TTL，历史数据长TTL
- **线程安全** - 支持并发访问
- **可配置** - 支持自定义缓存大小和TTL

## 缓存装饰器

### @smart_cache

主要的缓存装饰器，根据数据类型自动选择缓存策略：

```python
from akshare_one.modules.cache import smart_cache

class MyProvider:
    @smart_cache(
        realtime_key="realtime_cache",    # 实时数据缓存命名空间
        daily_key="daily_cache",          # 历史数据缓存命名空间
        key=lambda self: f"my_{self.symbol}_{self.interval}"  # 缓存键生成器
    )
    def get_data(self) -> pd.DataFrame:
        # 数据获取逻辑
        pass
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `realtime_key` | str | 必填 | 实时数据缓存命名空间 |
| `daily_key` | str | 必填 | 历史数据缓存命名空间 |
| `key` | Callable | 自动生成 | 缓存键生成函数 |
| `ttl` | int | None | 自定义TTL（秒） |
| `maxsize` | int | 默认值 | 缓存最大条目数 |

## 缓存策略

### 实时数据

- **TTL**: 通常 5-10 分钟
- **用途**: 实时行情、快照数据
- **命名空间**: `realtime_*`

### 历史数据

- **TTL**: 通常 24 小时或更长
- **用途**: 历史行情、财务数据
- **命名空间**: `daily_*`

## 缓存管理

### 查看缓存统计

```python
from akshare_one.modules.cache import get_cache_stats

stats = get_cache_stats()
print(f"实时缓存命中率: {stats['realtime']['hit_rate']:.2%}")
print(f"历史缓存条目数: {stats['daily']['size']}")
```

### 清理缓存

```python
from akshare_one.modules.cache import clear_cache

# 清理所有缓存
clear_cache()

# 清理特定命名空间
clear_cache(namespace="realtime_cache")
```

### 禁用缓存

```python
import os
os.environ["AKSHARE_ONE_CACHE_ENABLED"] = "False"
```

或在代码中：

```python
from akshare_one.modules.cache import disable_cache, enable_cache

disable_cache()  # 临时禁用
# ... 执行不需要缓存的代码 ...
enable_cache()   # 重新启用
```

## 缓存键规则

缓存键自动生成，包含：

1. **函数名** - 区分不同函数
2. **参数值** - 所有参数的哈希
3. **时间戳**（实时数据）- 确保数据新鲜度

示例：
```
realtime_hist_data_600000_day_20240215
daily_balance_sheet_600000_2024q4
```

## 性能影响

### 缓存收益

| 场景 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| 重复历史数据请求 | 500ms | <1ms | **500x** |
| 重复实时数据请求 | 300ms | <1ms | **300x** |
| 连续相同请求 | 500ms | <1ms | **500x** |

### 内存占用

- **实时缓存**: 约 50MB (默认1000条)
- **历史缓存**: 约 200MB (默认500条)
- **总计**: ~250MB (可配置)

## 最佳实践

### 1. 合理设置TTL

```python
# 实时数据用短TTL
@smart_cache(realtime_key="quote", ttl=300)  # 5分钟
def get_realtime_quote(self):
    pass

# 历史数据用长TTL  
@smart_cache(daily_key="hist", ttl=86400)  # 24小时
def get_historical_data(self):
    pass
```

### 2. 选择合适的缓存键

```python
# ✅ 好的做法：包含所有关键参数
key=lambda self: f"hist_{self.symbol}_{self.interval}_{self.adjust}"

# ❌ 避免：缺少关键参数
key=lambda self: f"hist_{self.symbol}"  # 丢失了 interval 和 adjust
```

### 3. 监控缓存命中率

```python
stats = get_cache_stats()
if stats['hit_rate'] < 0.1:
    logger.warning("缓存命中率过低，可能需要调整缓存策略")
```

### 4. 避免缓存大对象

```python
# ✅ 缓存DataFrame而不是原始JSON
@smart_cache(...)
def get_data(self):
    df = fetch_and_process()  # 返回处理好的DataFrame
    return df

# ❌ 避免缓存过多无关数据
@smart_cache(...)
def get_data(self):
    raw = fetch_raw()  # 原始大JSON
    return raw  # 占用更多内存
```

## 缓存失效策略

### 时间驱动失效

```python
@smart_cache(ttl=3600)  # 1小时后自动失效
def get_data(self):
    pass
```

### 手动失效

```python
from akshare_one.modules.cache import invalidate_cache

# 使特定缓存失效
invalidate_cache("hist_600000_day")
```

## 分布式缓存（未来）

计划支持 Redis 等分布式缓存后端：

```python
from akshare_one.modules.cache import distributed_cache

@distributed_cache(redis_url="redis://localhost:6379")
def get_shared_data(self):
    pass
```

## 调试技巧

### 查看缓存命中情况

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 缓存的命中/未命中会输出DEBUG日志
```

### 性能分析

```python
import time

# 第一次调用（缓存未命中）
start = time.time()
df1 = provider.get_data()
print(f"第一次: {time.time() - start:.3f}s")

# 第二次调用（缓存命中）
start = time.time()
df2 = provider.get_data()
print(f"第二次: {time.time() - start:.3f}s")
```

## 常见问题

### Q: 缓存数据过期怎么办？

**A**: 设置合适的TTL，或使用手动失效。实时数据建议5-10分钟，历史数据建议24小时。

### Q: 内存占用过高怎么办？

**A**: 调整 `maxsize` 参数，或定期清理缓存：

```python
@smart_cache(maxsize=100)  # 限制条目数
def get_data(self):
    pass
```

### Q: 如何验证缓存是否工作？

**A**: 启用DEBUG日志，观察缓存命中/未命中消息。

## 总结

AKShare One 的缓存系统提供了：

✅ **自动缓存** - 装饰器方式，使用简单
✅ **智能策略** - 区分实时/历史数据
✅ **高性能** - 300-500倍性能提升
✅ **可配置** - TTL、大小、键生成都可定制
✅ **易监控** - 统计信息和DEBUG日志
✅ **线程安全** - 支持高并发场景

合理使用缓存可以显著提升应用性能并减少对数据源的压力。
