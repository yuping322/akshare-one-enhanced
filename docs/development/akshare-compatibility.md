# AkShare 函数漂移治理方案

## 背景

AkShare 作为上游数据源库，其 API 函数名在不同版本之间可能发生变更或废弃，导致硬编码的函数调用失败。典型的变更包括：

- `stock_zh_a_daily` → `stock_zh_a_hist`（函数重命名）
- `stock_dzjy_sctj` → `stock_dzjy_mrtj`（函数重命名）
- 函数参数签名变更
- 函数完全移除

## 解决方案

### 1. AkShareAdapter 适配器

创建 `src/akshare_one/akshare_compat.py` 模块，提供以下核心功能：

#### 功能特性

1. **运行时函数探测**
   - 使用 `hasattr()` 检测函数是否存在
   - 缓存检测结果避免重复检查

2. **版本适配表**
   - `FUNCTION_ALIASES` 字典映射旧函数名到新函数名
   - 支持多级降级路径

3. **降级路径**
   - 主函数失败时自动尝试 fallback 函数
   - 返回空 DataFrame 而不是硬失败

4. **清晰的错误提示**
   - 记录详细的错误日志
   - 提示函数版本变更信息

#### 使用方法

```python
from akshare_one.akshare_compat import call_akshare, get_adapter

# 方式1：便捷函数
df = call_akshare(
    "stock_zh_a_hist",
    symbol="600000",
    period="daily",
    fallback_func="stock_zh_a_daily"  # 旧版本降级
)

# 方式2：适配器实例
adapter = get_adapter()
df = adapter.call("stock_zh_a_hist", symbol="600000")

# 方式3：安全调用（不抛异常）
df = adapter.call_safe("stock_zh_a_hist", symbol="600000")

# 检查函数是否存在
exists = adapter.function_exists("stock_zh_a_hist")

# 获取函数信息
info = adapter.get_function_info("stock_zh_a_hist")
# {'name': 'stock_zh_a_hist', 'exists': True, 'alias': None, 'version': '1.12.0'}

# 健康检查
health = adapter.check_function_health([
    "stock_zh_a_hist",
    "stock_zh_a_hist_min_em"
])
```

### 2. 集成到 BaseProvider

在 `src/akshare_one/modules/base.py` 中集成适配器：

```python
from ..akshare_compat import get_adapter

class BaseProvider:
    def __init__(self, **kwargs):
        # 初始化适配器
        self.akshare_adapter = get_adapter()

    def _execute_api_mapped(self, method_name, *args, **kwargs):
        # 使用适配器调用，支持 fallback
        config = self._API_MAP[method_name]
        ak_func_name = config["ak_func"]
        fallback_func = config.get("fallback_func")

        raw_df = self.akshare_adapter.call(
            ak_func_name,
            fallback_func=fallback_func,
            **ak_params
        )

        # 失败时返回空 DataFrame，不硬失败
        return self.standardize_and_filter(raw_df, ...)
```

### 3. 模块级适配

修改关键模块使用适配器：

**示例：`historical/eastmoney.py`**

```python
# 旧代码（硬编码）
import akshare as ak
raw_df = ak.stock_zh_a_hist(symbol="600000", ...)

# 新代码（适配器）
from ...akshare_compat import call_akshare
raw_df = call_akshare(
    "stock_zh_a_hist",
    symbol="600000",
    fallback_func="stock_zh_a_daily"
)
```

### 4. _API_MAP 扩展

在 `_API_MAP` 中添加 `fallback_func` 字段：

```python
_API_MAP = {
    "get_main_fund_flow_rank": {
        "ak_func": "stock_individual_fund_flow_rank",
        "params": {"indicator": "indicator_raw"},
        "fallback_func": "stock_fund_flow_individual"  # 降级函数
    }
}
```

## 版本兼容性矩阵

记录 AkShare 版本变更历史：

| 版本 | 变更内容 | 处理方式 |
|------|---------|----------|
| 1.12.0 | `stock_zh_a_daily` → `stock_zh_a_hist` | FUNCTION_ALIASES 映射 |
| 1.13.0 | `stock_dzjy_sctj` → `stock_dzjy_mrtj` | FUNCTION_ALIASES 映射 |
| 1.14.0 | `stock_fund_flow_individual` → `stock_individual_fund_flow` | FUNCTION_ALIASES 映射 |

## 测试验证

运行兼容性测试：

```bash
python tests/test_akshare_compat.py
```

测试内容：
1. 函数存在性检测
2. 函数调用（带 fallback）
3. 健康检查
4. 降级函数处理
5. 错误处理
6. BaseProvider 集成

## 最佳实践

### 1. 添加新 AkShare 函数时

在 `FUNCTION_ALIASES` 中添加映射：

```python
FUNCTION_ALIASES = {
    "new_function_name": "new_function_name",  # 当前函数
    "old_function_name": "new_function_name",  # 旧函数映射
}
```

### 2. 在模块中调用时

优先使用适配器，提供 fallback：

```python
raw_df = call_akshare(
    "primary_function",
    **params,
    fallback_func="fallback_function"
)
```

### 3. 失败处理

适配器返回空 DataFrame，模块应优雅处理：

```python
if raw_df.empty:
    logger.warning("No data returned from AkShare")
    return self.create_empty_dataframe(columns)
```

## 监控和维护

### 1. 日志监控

适配器记录详细日志：
- 函数不存在警告
- 函数调用失败
- 降级路径使用

### 2. 健康检查

定期运行健康检查：

```python
adapter = get_adapter()
report = adapter.check_function_health(critical_functions)
```

### 3. 版本更新流程

1. AkShare 发布新版本时，检查 API 变更
2. 更新 `FUNCTION_ALIASES` 映射表
3. 更新 `VERSION_COMPATIBILITY_MATRIX`
4. 运行测试验证
5. 发布兼容性更新

## 验收标准

✅ 函数不存在时不会硬失败  
✅ 有清晰的错误提示和日志  
✅ 版本适配表覆盖常见函数变更  
✅ 自动降级到替代函数  
✅ 返回空 DataFrame 而不是抛异常  
✅ 关键接口仍能正常工作

## 示例输出

### 成功调用

```
INFO: Detected AkShare version: 1.12.0
INFO: Calling AkShare function 'stock_zh_a_hist' with args: {...}
INFO: Successfully called stock_zh_a_hist, got 100 rows
```

### 降级调用

```
WARNING: Function 'stock_zh_a_daily' not found, using alias 'stock_zh_a_hist' instead
INFO: Consider updating your code to use 'stock_zh_a_hist' directly
INFO: Successfully called stock_zh_a_hist (fallback)
```

### 失败处理

```
ERROR: AkShare function 'nonexistent_function' is not available in version 1.12.0
WARNING: This may be due to function renaming or removal
WARNING: Returning empty DataFrame due to AkShare API failure
```

## 未来改进

1. **自动版本检测**：定期检查 AkShare 更新并自动更新映射表
2. **社区维护**：邀请社区贡献函数变更信息
3. **智能降级**：基于历史成功率选择最佳降级路径
4. **API 签名适配**：处理参数签名变更（不仅仅是函数名）