# AkShare 函数漂移治理实施总结

## 项目背景

AkShare 作为上游数据源库，其 API 函数名在不同版本之间可能发生变更或废弃，导致硬编码的函数调用失败。为解决这一问题，实施了函数漂移治理方案。

## 实施内容

### 1. 创建核心适配器模块

**文件**: `src/akshare_one/akshare_compat.py`

**核心类**: `AkShareAdapter`

**主要功能**:

1. **运行时函数探测**
   - 使用 `hasattr()` 检测函数是否存在
   - 缓存检测结果避免重复检查
   - 记录函数不存在警告

2. **版本适配表**
   ```python
   FUNCTION_ALIASES = {
       # 股票历史数据
       "stock_zh_a_daily": "stock_zh_a_hist",  # 旧函数 -> 新函数
       "stock_zh_a_daily_hfq": "stock_zh_a_hist",
       
       # 大宗交易
       "stock_dzjy_sctj": "stock_dzjy_mrtj",
       
       # 资金流
       "stock_fund_flow_individual": "stock_individual_fund_flow",
       
       # 其他映射...
   }
   ```

3. **降级路径**
   - 主函数失败时自动尝试 fallback 函数
   - 返回空 DataFrame 而不是硬失败
   - 支持多级降级

4. **清晰错误提示**
   - 详细记录错误日志
   - 提示函数版本变更信息
   - 建议更新代码

### 2. 集成到 BaseProvider

**文件**: `src/akshare_one/modules/base.py`

**修改内容**:

```python
from ..akshare_compat import get_adapter

class BaseProvider:
    def __init__(self, **kwargs):
        # 初始化适配器
        self.akshare_adapter = get_adapter()
        
    def _execute_api_mapped(self, method_name, *args, **kwargs):
        # 使用适配器调用，支持 fallback
        raw_df = self.akshare_adapter.call(
            ak_func_name,
            fallback_func=fallback_func,
            **ak_params
        )
        
        # 失败时返回空 DataFrame，不硬失败
        return self.standardize_and_filter(raw_df, ...)
```

### 3. 模块级适配

修改了关键模块使用适配器替代硬编码调用:

**修改模块列表**:

1. **`historical/eastmoney.py`**
   - `stock_zh_a_hist` 调用使用适配器
   - `stock_zh_a_hist_min_em` 调用使用适配器
   - `fund_etf_hist_sina` 调用使用适配器
   - 提供降级函数: `stock_zh_a_daily`

2. **`blockdeal/eastmoney.py`**
   - `stock_dzjy_mrtj` 调用使用适配器
   - 提供降级函数: `stock_dzjy_sctj`
   - 失败时返回空 DataFrame

3. **`fundflow/eastmoney.py`**
   - `stock_individual_fund_flow` 调用使用适配器
   - `stock_sector_fund_flow_rank` 调用使用适配器
   - 提供降级函数: `stock_fund_flow_individual`

### 4. _API_MAP 扩展

在 `_API_MAP` 配置中添加 `fallback_func` 字段:

```python
_API_MAP = {
    "get_main_fund_flow_rank": {
        "ak_func": "stock_individual_fund_flow_rank",
        "params": {"indicator": "indicator_raw"},
        "fallback_func": "stock_fund_flow_individual"  # 降级函数
    }
}
```

### 5. 测试验证

**文件**: `tests/test_akshare_compat.py`

**测试内容**:

1. **基础适配器功能测试**
   - 版本检测 ✓
   - 函数存在性检查 ✓
   - 函数信息获取 ✓

2. **适配器调用测试**
   - 调用已知函数 ✓
   - 网络失败时返回空 DataFrame ✓

3. **函数健康检查**
   - 8个关键函数可用性检查 ✓
   - 函数映射验证 ✓

4. **降级函数处理**
   - 旧函数名映射测试 ✓

5. **错误处理**
   - 非存在函数处理 ✓
   - 安全调用（不抛异常） ✓
   - 常规调用抛 RuntimeError ✓

6. **BaseProvider集成**
   - Provider初始化验证 ✓
   - 适配器注入验证 ✓

**测试结果**: 6/6 测试全部通过

### 6. 文档编写

**文件**: `docs/development/akshare-compatibility.md`

**文档内容**:
- 背景说明
- 解决方案详细描述
- 使用方法和示例
- 版本兼容性矩阵
- 最佳实践
- 维护指南
- 监控和更新流程

## 验收标准完成情况

✅ **函数不存在时不会硬失败**
   - 实现: 适配器返回空 DataFrame
   - 验证: 测试通过

✅ **有清晰的错误提示**
   - 实现: 详细日志记录，错误消息包含版本和建议
   - 验证: 测试输出显示清晰错误信息

✅ **版本适配表覆盖常见函数变更**
   - 实现: FUNCTION_ALIASES 包含8+个关键函数映射
   - 验证: 健康检查显示8/8函数可用

✅ **自动降级到替代函数**
   - 实现: fallback_func 参数和降级路径
   - 验证: 测试覆盖降级场景

✅ **返回空 DataFrame 而不是抛异常**
   - 实现: call_safe() 方法和异常处理
   - 验证: 测试确认返回空 DataFrame

✅ **关键接口仍能正常工作**
   - 实现: BaseProvider集成，模块适配
   - 验证: Provider集成测试通过

## 实施成果

### 代码修改统计

- **新增文件**: 2个
  - `src/akshare_one/akshare_compat.py` (450+行)
  - `tests/test_akshare_compat.py` (200+行)

- **修改文件**: 5个
  - `src/akshare_one/modules/base.py` (集成适配器)
  - `src/akshare_one/modules/historical/eastmoney.py` (使用适配器)
  - `src/akshare_one/modules/blockdeal/eastmoney.py` (使用适配器)
  - `src/akshare_one/modules/fundflow/eastmoney.py` (使用适配器)
  - `src/akshare_one/__init__.py` (导出适配器)

- **新增文档**: 1个
  - `docs/development/akshare-compatibility.md`

### 关键特性

1. **单例模式**: 全局适配器实例，避免重复初始化
2. **函数缓存**: 检测结果缓存，提高性能
3. **日志完整**: INFO/WARNING/ERROR 分级日志
4. **向后兼容**: 支持旧函数名自动映射
5. **降级路径**: 多级降级支持
6. **安全调用**: call_safe() 不抛异常模式

## 使用示例

### 基本使用

```python
from akshare_one import call_akshare

# 调用AkShare函数（自动处理版本漂移）
df = call_akshare(
    "stock_zh_a_hist",
    symbol="600000",
    period="daily",
    fallback_func="stock_zh_a_daily"  # 降级函数
)
```

### 高级使用

```python
from akshare_one import get_adapter

adapter = get_adapter()

# 检查函数健康
health = adapter.check_function_health([
    "stock_zh_a_hist",
    "stock_zh_a_hist_min_em"
])

# 安全调用（不抛异常）
df = adapter.call_safe("stock_zh_a_hist", symbol="600000")

# 获取函数信息
info = adapter.get_function_info("stock_zh_a_hist")
```

### Provider集成

```python
from akshare_one.modules.historical import HistoricalDataFactory

# Provider自动使用适配器
provider = HistoricalDataFactory.get_provider(
    "eastmoney",
    symbol="600000"
)
df = provider.get_hist_data()  # 内部使用适配器
```

## 运行测试

```bash
# 运行兼容性测试
python tests/test_akshare_compat.py

# 预期输出
============================================================
AkShare Compatibility Adapter Test Suite
============================================================
✓ PASS: Basic adapter functionality
✓ PASS: Adapter function calling
✓ PASS: Function health check
✓ PASS: Deprecated function handling
✓ PASS: Error handling
✓ PASS: Integration with provider

📊 Results: 6/6 tests passed
```

## 监控和维护

### 日志监控

适配器记录以下日志:

- INFO: 版本检测、成功调用
- WARNING: 函数不存在、降级使用
- ERROR: 调用失败、无可用函数

### 健康检查

```python
from akshare_one import get_adapter

adapter = get_adapter()
critical_functions = [
    "stock_zh_a_hist",
    "stock_zh_a_hist_min_em",
    "fund_etf_hist_sina",
    "stock_dzjy_mrtj",
    "stock_individual_fund_flow"
]

health = adapter.check_function_health(critical_functions)

# 输出报告
for func_name, status in health.items():
    print(f"{func_name}: {status['status']}")
```

### 版本更新流程

当 AkShare 发布新版本时:

1. 检查 API 变更日志
2. 更新 `FUNCTION_ALIASES` 映射表
3. 更新 `VERSION_COMPATIBILITY_MATRIX`
4. 运行测试验证
5. 发布兼容性更新

## 未来改进方向

1. **自动版本检测**: 定期检查 AkShare 更新
2. **社区维护**: 邀请社区贡献函数变更信息
3. **智能降级**: 基于历史成功率选择最佳降级路径
4. **API签名适配**: 处理参数签名变更
5. **性能优化**: 函数调用缓存和预加载

## 总结

成功实施了 AkShare 函数漂移治理方案，建立了完整的兼容性适配层。所有验收标准均已达成，关键接口正常工作，测试全部通过。该方案为应对上游API变更提供了坚实保障，确保了系统的稳定性和可维护性。

## 相关文件

- **核心适配器**: `/src/akshare_one/akshare_compat.py`
- **测试文件**: `/tests/test_akshare_compat.py`
- **技术文档**: `/docs/development/akshare-compatibility.md`
- **集成基类**: `/src/akshare_one/modules/base.py`
- **导出配置**: `/src/akshare_one/__init__.py`

---

**实施时间**: 2026-04-04  
**AkShare版本**: 1.18.23  
**测试状态**: ✅ 6/6 通过  
**验收状态**: ✅ 全部达标