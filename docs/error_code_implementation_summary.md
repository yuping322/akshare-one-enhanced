# Error Code System Implementation Summary

## 完成情况

本次任务已完整实现错误码体系和增强日志系统，所有验收标准均已满足。

## 实现内容

### 1. 统一错误码枚举 (src/akshare_one/error_codes.py)

已创建完整的错误码枚举系统：

- **错误码格式**: `E{Module}{Type}{Sequence}`
  - Module: 3位数字 (001-008)
  - Type: 2位数字 (00-99)
  - Sequence: 2位数字 (00-99)

- **错误码统计**: 67个错误码，分布在8个类别
  - E001xxx: 参数验证 (15个)
  - E002xxx: 数据源 (12个)
  - E003xxx: 网络 (12个)
  - E004xxx: 数据验证 (9个)
  - E005xxx: 配置 (6个)
  - E006xxx: 缓存 (4个)
  - E007xxx: 速率限制 (3个)
  - E008xxx: 数据处理 (6个)

- **辅助函数**:
  - `get_error_description()`: 获取用户友好的错误描述
  - `get_error_category_name()`: 获取错误类别名称

**示例**:
```python
from akshare_one.error_codes import ErrorCode, get_error_description

# 使用错误码
error_code = ErrorCode.INVALID_SYMBOL_FORMAT
print(error_code.value)  # "E00101001"
print(error_code.category)  # "001"
print(get_error_description(error_code))  # "Symbol format is invalid..."
```

### 2. 异常类增强 (src/akshare_one/modules/exceptions.py)

所有异常类已增强，包含以下属性：

- `message`: 原始错误消息
- `error_code`: ErrorCode枚举实例
- `context`: 上下文信息字典 (source, endpoint, symbol等)

**改进的异常类**:
- `MarketDataError` (基类)
- `InvalidParameterError`
- `DataSourceUnavailableError`
- `NoDataError`
- `UpstreamChangedError`
- `RateLimitError`
- `DataValidationError`

**改进的方法**:
- `map_to_standard_exception()`: 保留error_code和context属性
- `__str__()`: 格式化输出包含错误码 `[E00101001] message`

**示例**:
```python
from akshare_one.modules.exceptions import InvalidParameterError
from akshare_one.error_codes import ErrorCode

# 抛出带错误码的异常
raise InvalidParameterError(
    "Invalid symbol format: ABC",
    error_code=ErrorCode.INVALID_SYMBOL_FORMAT,
    context={"symbol": "ABC", "market_type": "a_stock"}
)

# 异常输出: "[E00101001] Invalid symbol format: ABC"
```

### 3. 日志格式增强 (src/akshare_one/logging_config.py)

增强了结构化日志系统：

- **StructuredFormatter**: JSON格式日志包含error_code字段
- **log_api_request()**: 新增error_code参数
- **log_exception()**: 新增统一异常日志函数，自动提取错误码

**日志格式示例**:
```json
{
  "timestamp": "2026-04-04T01:00:34.597Z",
  "level": "ERROR",
  "error_code": "E00101001",
  "logger": "akshare_one",
  "message": "Exception occurred: [E00101001] Invalid symbol format",
  "context": {
    "log_type": "exception",
    "source": "eastmoney",
    "endpoint": "get_hist_data",
    "symbol": "600000",
    "error_code": "E00101001"
  },
  "exception": {...}
}
```

### 4. 关键路径日志添加 (src/akshare_one/modules/base.py)

在关键位置添加了日志：

- **Provider初始化**: 记录provider创建和参数
- **API调用**: 记录成功/失败，包含duration_ms和rows
- **异常捕获**: 使用log_exception()记录完整上下文
- **参数验证**: 所有验证失败抛出带错误码的异常

**改进的验证方法**:
- `validate_symbol()`: 使用InvalidParameterError + ErrorCode
- `validate_date()`: 使用InvalidParameterError + ErrorCode
- `validate_date_range()`: 使用InvalidParameterError + ErrorCode

### 5. 错误码参考文档 (docs/error_codes.md)

创建了完整的错误码文档：

- **格式说明**: 错误码结构和含义
- **分类索引**: 8个类别，67个错误码
- **详细说明**: 每个错误码包含:
  - 名称和描述
  - 可能原因
  - 解决方案
  - 使用示例
- **使用指南**: 最佳实践和错误处理模式

## 验收标准验证

所有验收标准均已满足：

### ✓ 1. 所有异常包含错误码
验证结果：
- MarketDataError及其所有子类支持error_code参数
- 所有验证方法抛出的异常包含错误码
- 错误码在异常链中正确传递

### ✓ 2. 日志可追踪到具体错误类型
验证结果：
- JSON日志包含error_code字段
- 日志context包含source、endpoint、symbol等信息
- log_exception()自动提取并记录错误码

### ✓ 3. 错误码文档完备（至少20个错误码）
验证结果：
- 定义了67个错误码（远超20个要求）
- 文档覆盖所有错误码
- 每个错误码包含描述、原因、解决方案

### ✓ 4. 示例错误消息清晰可读
验证结果：
- 异常消息格式：`[E00101001] Invalid symbol format: ABC`
- 用户友好描述函数可用
- JSON日志结构清晰，易于解析

## 测试验证

创建了多个测试脚本验证实现：

### test_error_codes.py
- 测试错误码枚举
- 测试异常创建和属性
- 测试异常映射保留错误码
- 测试日志记录包含错误码
- 测试错误码覆盖率

**结果**: 所有测试通过 ✓

### verify_error_codes.py
- 验证validate_symbol包含错误码
- 验证validate_date包含错误码
- 验证validate_date_range包含错误码
- 验证所有异常类型支持错误码
- 验证错误码数量满足要求

**结果**: 所有验证通过 ✓

### examples/error_codes_demo.py
演示实际使用场景：
- 错误码结构和使用
- 异常创建和属性访问
- 异常映射保留错误码
- 结构化日志输出
- 常见错误处理模式

**结果**: 演示成功运行 ✓

## 使用示例

### 基本使用

```python
from akshare_one import get_hist_data
from akshare_one.modules.exceptions import InvalidParameterError
from akshare_one.error_codes import ErrorCode, get_error_description

try:
    df = get_hist_data("ABC")  # 无效的股票代码
except InvalidParameterError as e:
    # 检查错误码
    if e.error_code == ErrorCode.INVALID_SYMBOL_FORMAT:
        print(f"Error: {e}")  # [E00101001] Invalid symbol format...
        print(f"Description: {get_error_description(e.error_code)}")
        print(f"Context: {e.context}")
```

### 日志记录

```python
from akshare_one.logging_config import setup_logging, log_exception

logger = setup_logging(log_level="INFO", json_format=True)

try:
    # 业务逻辑
    ...
except InvalidParameterError as e:
    # 自动记录错误码和上下文
    log_exception(
        logger, e,
        source="eastmoney",
        endpoint="get_hist_data",
        symbol="600000"
    )
```

### 异常映射

```python
from akshare_one.modules.exceptions import map_to_standard_exception

try:
    # 内部操作抛出InvalidParameterError
    ...
except InvalidParameterError as e:
    # 映射为标准异常，保留错误码
    mapped = map_to_standard_exception(e, {"source": "eastmoney"})
    # mapped是ValueError，但保留error_code属性
    print(mapped.error_code)  # E00101001
    raise mapped  # 外部调用者捕获ValueError
```

## 主要优势

1. **唯一标识**: 每个错误有唯一代码，便于追踪和查询
2. **结构化日志**: JSON格式便于日志分析和监控
3. **错误分类**: 8个类别便于分类处理和统计
4. **上下文保留**: source、endpoint、symbol等便于定位问题
5. **异常链传递**: 错误码在异常转换中不丢失
6. **文档完备**: 67个错误码均有详细说明和解决方案

## 文件清单

新增文件：
- src/akshare_one/error_codes.py (246行)
- docs/error_codes.md (465行)
- test_error_codes.py (235行)
- verify_error_codes.py (183行)
- examples/error_codes_demo.py (322行)

修改文件：
- src/akshare_one/modules/exceptions.py (增强所有异常类)
- src/akshare_one/logging_config.py (增强日志格式和函数)
- src/akshare_one/modules/base.py (添加日志和错误码)

## 后续建议

1. **监控集成**: 可将error_code字段接入监控系统，统计各类错误频率
2. **告警规则**: 基于错误类别设置告警（如网络错误、数据源错误）
3. **文档更新**: 在API文档中列出可能返回的错误码
4. **国际化**: 可扩展多语言错误描述

## 总结

本次实现完整、规范、可验证，所有验收标准均满足：
- ✓ 67个错误码（远超20个要求）
- ✓ 所有异常包含error_code属性
- ✓ 结构化日志包含error_code字段
- ✓ 错误码在异常链中传递
- ✓ 文档完备，每个错误码有说明和解决方案

系统已准备好投入使用，可显著提升错误追踪和调试效率。