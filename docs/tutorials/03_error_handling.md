# 错误处理教程

本教程教你如何正确处理 akshare-one 中的各种错误和异常。

## 错误类型

akshare-one 定义了以下异常类型：

| 异常 | 说明 | 常见原因 |
|------|------|----------|
| `InvalidParameterError` | 参数错误 | 股票代码格式错误、日期格式错误 |
| `NoDataError` | 无数据返回 | 时间范围内无数据、股票不存在 |
| `DataSourceUnavailableError` | 数据源不可用 | 网络故障、数据源维护 |
| `UpstreamChangedError` | 上游数据变化 | 数据源格式改变 |

## 导入异常

```python
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
    UpstreamChangedError
)
```

## 基础错误处理

### 完整的异常处理结构

```python
from akshare_one import get_hist_data
from akshare_one.modules.exceptions import (
    InvalidParameterError,
    NoDataError,
    DataSourceUnavailableError,
    UpstreamChangedError
)

try:
    df = get_hist_data(
        symbol="600000",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    # 处理数据
    if not df.empty:
        print(f"成功获取 {len(df)} 条数据")

except InvalidParameterError as e:
    # 参数错误
    print(f"参数错误: {e}")
    print("请检查股票代码和日期格式")

except NoDataError as e:
    # 无数据
    print(f"无数据: {e}")
    print("请检查时间范围是否正确")

except DataSourceUnavailableError as e:
    # 数据源不可用
    print(f"数据源不可用: {e}")
    print("请检查网络连接或稍后重试")

except UpstreamChangedError as e:
    # 上游数据变化
    print(f"数据源格式变化: {e}")
    print("请联系技术支持")

except Exception as e:
    # 其他未预期的错误
    print(f"未知错误: {e}")
    print("请联系技术支持")

finally:
    # 清理工作（可选）
    print("处理完成")
```

## 各类异常详解

### InvalidParameterError

**常见原因：**
- 股票代码格式错误（不是6位数字）
- 日期格式错误（不是YYYY-MM-DD）
- interval参数错误
- 其他参数值不合法

**示例：**

```python
try:
    # 错误的股票代码格式
    df = get_hist_data(symbol="60000")  # 只有5位

except InvalidParameterError as e:
    print(f"参数错误: {e}")
    # 输出：参数错误：股票代码格式不正确，应为6位数字
```

**处理方法：**
```python
# 1. 验证股票代码格式
symbol = "600000"
if not (len(symbol) == 6 and symbol.isdigit()):
    print("股票代码格式错误")

# 2. 验证日期格式
from datetime import datetime
try:
    datetime.strptime("2024-01-01", "%Y-%m-%d")
except ValueError:
    print("日期格式错误")
```

### NoDataError

**常见原因：**
- 股票不存在或已退市
- 时间范围内无交易数据
- 数据源未收录该股票

**示例：**

```python
try:
    # 获取退市股票数据
    df = get_hist_data(symbol="600001")  # 可能已退市

except NoDataError as e:
    print(f"无数据: {e}")
    # 输出：无数据：股票可能不存在或已退市
```

**处理方法：**
```python
# 1. 检查股票是否有效
from akshare_one import get_basic_info

try:
    info = get_basic_info(symbol="600000")
    if info.empty:
        print("股票不存在")
except:
    print("无法获取股票信息")

# 2. 扩大时间范围
try:
    df = get_hist_data(
        symbol="600000",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
except NoDataError:
    # 尝试更大的时间范围
    df = get_hist_data(
        symbol="600000",
        start_date="2023-01-01",
        end_date="2024-12-31"
    )
```

### DataSourceUnavailableError

**常见原因：**
- 网络连接失败
- 数据源服务器故障
- 数据源正在维护
- API限流

**示例：**

```python
try:
    df = get_hist_data(symbol="600000", source="eastmoney_direct")

except DataSourceUnavailableError as e:
    print(f"数据源不可用: {e}")
    # 输出：数据源不可用：eastmoney_direct 暂时无法访问
```

**处理方法：**

#### 1. 使用多数据源

```python
from akshare_one import get_hist_data_multi_source

# 自动切换数据源
df = get_hist_data_multi_source(
    symbol="600000",
    sources=["eastmoney_direct", "eastmoney", "sina"]
)
```

#### 2. 重试机制

```python
import time

max_retries = 3
retry_delay = 5  # 秒

for attempt in range(max_retries):
    try:
        df = get_hist_data(symbol="600000")
        break  # 成功则跳出循环

    except DataSourceUnavailableError as e:
        if attempt < max_retries - 1:
            print(f"第 {attempt+1} 次失败，{retry_delay}秒后重试...")
            time.sleep(retry_delay)
        else:
            print("所有重试失败，请稍后再试")
            raise
```

#### 3. 降级处理

```python
try:
    # 尝试获取详细数据
    df = get_hist_data(symbol="600000", source="eastmoney_direct")

except DataSourceUnavailableError:
    # 降级：使用其他数据源或简化数据
    try:
        df = get_hist_data(symbol="600000", source="sina")
        print("使用备用数据源成功")
    except:
        print("所有数据源都不可用")
```

### UpstreamChangedError

**常见原因：**
- 数据源网页结构改变
- API接口格式变化
- 数据字段名称变化

**示例：**

```python
try:
    df = get_hist_data(symbol="600000")

except UpstreamChangedError as e:
    print(f"数据源格式变化: {e}")
    print("需要更新接口解析逻辑")
    # 建议：通知维护者更新代码
```

**处理方法：**

```python
# 1. 查看错误详情
import logging
logging.basicConfig(level=logging.DEBUG)

try:
    df = get_hist_data(symbol="600000")
except UpstreamChangedError as e:
    logging.error(f"上游数据变化: {e}")
    # 记录详细信息，便于排查

# 2. 使用其他数据源
try:
    df = get_hist_data(symbol="600000", source="sina")
except:
    print("所有数据源都有问题，请联系维护者")
```

## 最佳实践

### 1. 分级错误处理

```python
def get_stock_data_safe(symbol):
    """安全的获取股票数据"""

    # 第一级：参数验证
    if not (len(symbol) == 6 and symbol.isdigit()):
        raise ValueError("股票代码格式错误")

    # 第二级：多数据源获取
    try:
        from akshare_one import get_hist_data_multi_source

        df = get_hist_data_multi_source(
            symbol=symbol,
            sources=["eastmoney_direct", "eastmoney", "sina"]
        )

        # 第三级：数据验证
        if df.empty:
            raise NoDataError("返回数据为空")

        return df

    except DataSourceUnavailableError as e:
        # 第四级：错误恢复
        print(f"所有数据源不可用: {e}")
        return None
```

### 2. 批量操作的错误处理

```python
from akshare_one import get_hist_data

stocks = ["600000", "000001", "600519", "invalid"]

results = {}
failed = []

for symbol in stocks:
    try:
        df = get_hist_data(symbol=symbol)
        if not df.empty:
            results[symbol] = df
        else:
            failed.append((symbol, "无数据"))

    except InvalidParameterError as e:
        failed.append((symbol, f"参数错误: {e}"))

    except DataSourceUnavailableError as e:
        failed.append((symbol, f"数据源错误: {e}"))

    except Exception as e:
        failed.append((symbol, f"未知错误: {e}"))

print(f"成功: {len(results)}")
print(f"失败: {len(failed)}")

if failed:
    print("\n失败列表：")
    for symbol, reason in failed:
        print(f"  {symbol}: {reason}")
```

### 3. 日志记录

```python
import logging
from akshare_one import get_hist_data

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='akshare_one.log'
)

logger = logging.getLogger(__name__)

try:
    df = get_hist_data(symbol="600000")
    logger.info(f"成功获取数据: {len(df)} 条")

except Exception as e:
    logger.error(f"获取数据失败: {e}")
    raise
```

### 4. 用户友好的错误提示

```python
def get_data_with_hint(symbol):
    """提供友好的错误提示"""

    try:
        df = get_hist_data(symbol=symbol)
        return df

    except InvalidParameterError:
        print("❌ 股票代码格式错误")
        print("💡 提示：股票代码应为6位数字，如 600000")
        return None

    except NoDataError:
        print("❌ 未找到数据")
        print("💡 提示：股票可能不存在或已退市，请检查代码")
        return None

    except DataSourceUnavailableError:
        print("❌ 数据源暂时不可用")
        print("💡 提示：请检查网络连接，或稍后重试")
        return None

    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        print("💡 提示：如问题持续，请联系技术支持")
        return None
```

## 调试技巧

### 1. 查看详细错误信息

```python
import traceback

try:
    df = get_hist_data(symbol="600000")
except Exception as e:
    print(f"错误: {e}")
    print("\n详细堆栈信息：")
    traceback.print_exc()
```

### 2. 测试数据源可用性

```python
def test_data_source(source):
    """测试数据源是否可用"""
    try:
        from akshare_one import get_realtime_data

        df = get_realtime_data(symbol="600000", source=source)
        print(f"✓ {source} 可用")
        return True
    except:
        print(f"✗ {source} 不可用")
        return False

# 测试所有数据源
sources = ["eastmoney_direct", "eastmoney", "sina", "xueqiu"]
for source in sources:
    test_data_source(source)
```

### 3. 数据验证

```python
def validate_data(df):
    """验证返回的数据"""

    if df.empty:
        print("警告：数据为空")
        return False

    # 检查必需字段
    required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    missing_fields = [f for f in required_fields if f not in df.columns]

    if missing_fields:
        print(f"警告：缺少字段: {missing_fields}")
        return False

    # 检查数据完整性
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print(f"警告：数据包含空值: {null_counts[null_counts > 0]}")

    return True

# 使用示例
df = get_hist_data(symbol="600000")
if validate_data(df):
    print("数据验证通过")
```

## 下一步

- 查看 [最佳实践教程](04_best_practices.md) 学习更多技巧
- 查看 [FAQ](../FAQ.md) 查找常见问题解答
- 查看 [错误处理示例](../../examples/exception_usage_example.py)