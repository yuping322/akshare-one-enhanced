# 性能优化指南

本文档提供了 AKShare One 的性能优化建议和最佳实践。

## 性能指标

### 基准性能

| 操作类型 | 平均耗时 | 95分位 | 备注 |
|---------|---------|--------|------|
| 历史数据查询 | <500ms | <1s | 带缓存 <1ms |
| 实时数据查询 | <300ms | <500ms | 带缓存 <1ms |
| 财务数据查询 | <1s | <2s | - |
| 技术指标计算 | <100ms | <200ms | TA-Lib 加速 |

### 缓存收益

| 场景 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| 重复请求 | 500ms | <1ms | **500x** |
| 批量查询 | 5s | 50ms | **100x** |
| 并发场景 | 线性增长 | 几乎无影响 | **几乎无限** |

## 优化策略

### 1. 使用缓存 ✅

缓存是最有效的优化手段：

```python
from akshare_one import get_hist_data

# 第一次查询（慢）
df = get_hist_data("600000")  # ~500ms

# 第二次查询（极快，从缓存）
df = get_hist_data("600000")  # <1ms
```

**缓存命中率目标**: >80%

### 2. 批量请求

尽量避免在循环中单条请求：

```python
# ❌ 低效做法
results = []
for symbol in symbols:
    df = get_hist_data(symbol)  # 每次都有开销
    results.append(df)

# ✅ 高效做法
# 如果API支持批量查询，使用批量接口
df = get_hist_data_batch(symbols)  # 单次请求

# 或者利用缓存
results = [get_hist_data(symbol) for symbol in symbols]  # 第二次开始极快
```

### 3. 合理设置时间范围

限制查询的时间范围可以减少数据处理量：

```python
# ✅ 只获取需要的日期范围
df = get_hist_data(
    symbol="600000",
    start_date="2024-01-01",
    end_date="2024-03-31"  # 限制在3个月内
)

# ❌ 避免获取过多历史数据
df = get_hist_data(symbol="600000")  # 可能获取20年数据
```

### 4. 选择合适的源优先级

将最快的源放在前面：

```python
from akshare_one import create_historical_router

# eastmoney_direct 最快放前面
router = create_historical_router(
    symbol="600000",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)

# 如果 eastmoney_direct 可用，立即返回，无需尝试其他源
df = router.execute("get_hist_data")
```

### 5. 控制请求频率

避免触发限流：

```python
import time
from akshare_one import get_hist_data

for symbol in symbols:
    try:
        df = get_hist_data(symbol)
        process(df)
    except Exception as e:
        if "rate limit" in str(e):
            time.sleep(60)  # 遇到限流，等待60秒
            continue
    
    time.sleep(0.5)  # 主动延迟，避免触发限流
```

### 6. 使用多线程/异步

对于大量独立请求，可以使用并发：

```python
from concurrent.futures import ThreadPoolExecutor
from akshare_one import get_hist_data

def fetch_data(symbol):
    return get_hist_data(symbol)

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_data, symbols))
```

### 7. 复用会话

在自定义 Provider 中复用 HTTP 会话：

```python
import requests

class MyProvider:
    _session = requests.Session()
    
    def __init__(self):
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; AKShare-One/1.0)'
        })
    
    def fetch_data(self):
        response = self._session.get(url)  # 复用连接
        return response
```

### 8. 配置 SSL 验证（可选）

在某些环境下，禁用SSL验证可以提升性能：

```python
from akshare_one import configure_ssl_verification

configure_ssl_verification(False)  # 不推荐生产环境使用
```

## 监控性能

### 使用日志记录耗时

```python
import time
import logging

logger = logging.getLogger(__name__)

def timed_fetch(symbol):
    start = time.time()
    df = get_hist_data(symbol)
    elapsed = time.time() - start
    logger.info(f"Fetch {symbol}: {elapsed:.3f}s")
    return df
```

### 查看缓存统计

```python
from akshare_one.modules.cache import get_cache_stats

stats = get_cache_stats()
print(f"实时缓存: {stats['realtime']['size']} 条目, 命中率 {stats['realtime']['hit_rate']:.2%}")
print(f"历史缓存: {stats['daily']['size']} 条目, 命中率 {stats['daily']['hit_rate']:.2%}")
```

### 性能分析工具

使用 `cProfile` 分析热点：

```python
import cProfile
import pstats
from akshare_one import get_hist_data

profiler = cProfile.Profile()
profiler.enable()

# 执行一些查询
for symbol in ["600000", "000001", "600519"]:
    get_hist_data(symbol)

profiler.disable()

# 输出统计
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(10)
```

## 网络优化

### 1. 连接池配置

```python
import requests
from requests.adapters import HTTPAdapter

session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=100)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

### 2. 超时设置

```python
# 设置合理的超时
response = requests.get(url, timeout=(5, 30))  # (连接超时, 读取超时)
```

### 3. 代理配置

```bash
# 使用更快的代理
export HTTP_PROXY=http://fast-proxy:端口
export HTTPS_PROXY=http://fast-proxy:端口
```

## 数据结构优化

### 1. 选择合适的数据类型

- 使用 `float32` 替代 `float64` 减少内存
- 将日期列转换为 `datetime64` 类型
- 对分类数据使用 `category` 类型

```python
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['volume'] = df['volume'].astype('int32')
```

### 2. 及时释放内存

```python
del large_df  # 及时删除大对象
import gc
gc.collect()  # 强制垃圾回收
```

## 实战案例

### 场景1: 批量获取100只股票日线

```python
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from akshare_one import get_hist_data

symbols = [...]  # 100只股票

# 方法1: 顺序执行（利用缓存）
results = []
for symbol in symbols:
    df = get_hist_data(symbol, start_date="2024-01-01")
    df['symbol'] = symbol
    results.append(df)
    
all_data = pd.concat(results, ignore_index=True)  # ~50s 第一次，<1s 第二次

# 方法2: 并发执行（注意限流）
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(get_hist_data, s, "2024-01-01") for s in symbols]
    results = [f.result() for f in futures]
```

### 场景2: 实时监控50只股票

```python
import schedule
import time
from akshare_one import get_realtime_data

def monitor():
    start = time.time()
    df = get_realtime_data(symbol=None)  # 一次性获取所有
    elapsed = time.time() - start
    
    # 筛选关注的股票
    watchlist = df[df['symbol'].isin(watch_symbols)]
    print(f"更新完成，耗时 {elapsed:.2f}s，{len(watchlist)} 只股票")

# 每30秒更新一次
schedule.every(30).seconds.do(monitor)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 性能调优检查清单

- [ ] 确认缓存已启用且命中率 >80%
- [ ] 限制查询时间范围到必要区间
- [ ] 批量请求而非单条循环
- [ ] 将最快的源设为默认优先级
- [ ] 添加请求间隔避免限流
- [ ] 复用 HTTP 会话
- [ ] 使用并发处理独立请求
- [ ] 及时清理不再使用的大对象
- [ ] 监控关键操作的耗时
- [ ] 定期检查缓存统计

## 性能瓶颈排查

### 1. 网络延迟高

- 检查是否使用了最优的数据源
- 考虑使用 CDN 或代理
- 调整超时设置避免等待

### 2. 缓存命中率低

- 检查缓存键是否包含所有参数
- 确认参数是否每次都变化
- 考虑扩大缓存容量

### 3. 内存占用高

- 限制缓存大小
- 及时释放大对象
- 使用适当的数据类型

### 4. CPU 使用率高

- 技术指标计算可能在纯Python模式，考虑安装TA-Lib
- 减少不必要的DataFrame操作
- 使用向量化操作而非循环

## 总结

AKShare One 通过多层优化确保高性能：

✅ **智能缓存** - 300-500x 性能提升
✅ **多源路由** - 自动选择最快源
✅ **连接复用** - 减少连接开销
✅ **并发支持** - 充分利用多核
✅ **内存优化** - 合理的数据结构

遵循本文档的建议，可以显著提升应用性能并提供更好的用户体验。
