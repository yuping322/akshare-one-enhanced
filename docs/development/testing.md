# 测试指南

本文档介绍 AKShare One 的测试框架、测试策略和最佳实践。

## 测试概览

### 测试统计

- **测试覆盖率**: >80%
- **测试文件数**: 13+
- **测试类型**: 单元测试、集成测试、契约测试
- **测试运行器**: pytest

### 测试目录结构

```
tests/
├── test_stock.py                      # 股票历史/实时数据测试
├── test_financial.py                  # 财务数据测试
├── test_futures.py                    # 期货数据测试
├── test_options.py                    # 期权数据测试
├── test_indicators.py                 # 技术指标测试
├── test_info.py                       # 基本信息测试
├── test_news.py                       # 新闻数据测试
├── test_insider.py                    # 内部交易测试
├── test_mcp.py                        # MCP服务器测试
├── test_multi_source_enhanced.py      # 多源增强功能测试
├── test_multi_source_comprehensive.py # 多源综合测试
├── test_new_data_sources.py          # 新数据源测试
└── conftest.py                        # 测试配置和fixture
```

## 运行测试

### 运行所有测试

```bash
# 基础运行
pytest

# 详细输出
pytest -v

# 显示print输出
pytest -s
```

### 运行特定测试文件

```bash
pytest tests/test_stock.py
pytest tests/test_financial.py -v
```

### 运行特定测试用例

```bash
# 通过节点ID
pytest tests/test_stock.py::test_get_hist_data

# 通过关键词
pytest -k "test_hist"
```

### 查看测试覆盖率

```bash
# 生成HTML覆盖率报告
pytest --cov=akshare_one --cov-report=html

# 查看覆盖率百分比
pytest --cov=akshare_one --cov-report=term-missing

# 打开HTML报告
open htmlcov/index.html
```

## 测试类型

### 1. 单元测试（Unit Tests）

测试单个函数或类的行为：

```python
def test_get_hist_data_basic():
    """Test basic historical data retrieval"""
    from akshare_one import get_hist_data
    
    df = get_hist_data("600000", interval="day")
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'timestamp' in df.columns
    assert 'close' in df.columns
```

### 2. 集成测试（Integration Tests）

测试多个组件的协作：

```python
def test_multi_source_failover():
    """Test automatic failover between sources"""
    from akshare_one import create_historical_router
    
    router = create_historical_router(
        symbol="600000",
        sources=["invalid_source", "eastmoney"]  # 第一个源会失败
    )
    
    # 应该自动切换到 eastmoney
    df = router.execute("get_hist_data")
    assert not df.empty
```

### 3. 契约测试（Contract Tests）

验证数据格式是否符合预期：

```python
def test_hist_data_schema():
    """Test that historical data follows expected schema"""
    from akshare_one import get_hist_data
    
    df = get_hist_data("600000")
    
    # 检查必需列
    required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    assert all(col in df.columns for col in required_columns)
    
    # 检查数据类型
    assert pd.api.types.is_datetime64_any_dtype(df['timestamp'])
    assert pd.api.types.is_float_dtype(df['close'])
    assert pd.api.types.is_integer_dtype(df['volume'])
```

### 4. 异常测试（Exception Tests）

测试错误处理：

```python
def test_invalid_symbol():
    """Test that invalid symbol raises proper exception"""
    from akshare_one.modules import InvalidParameterError
    
    with pytest.raises(InvalidParameterError, match="Invalid symbol"):
        get_hist_data("invalid_code")
```

## Fixture 使用

### 常用 Fixtures

```python
import pytest
import pandas as pd

@pytest.fixture
def sample_symbol():
    """提供一个测试用股票代码"""
    return "600000"

@pytest.fixture
def sample_date_range():
    """提供一个测试日期范围"""
    return {
        'start_date': '2024-01-01',
        'end_date': '2024-01-31'
    }

@pytest.fixture
def mock_data():
    """提供模拟数据"""
    return pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10),
        'open': [10.0] * 10,
        'high': [10.5] * 10,
        'low': [9.5] * 10,
        'close': [10.2] * 10,
        'volume': [1000] * 10,
    })
```

### 使用 Fixtures

```python
def test_get_hist_data(sample_symbol):
    df = get_hist_data(sample_symbol)
    assert not df.empty

def test_date_range(sample_date_range):
    df = get_hist_data(
        "600000",
        start_date=sample_date_range['start_date'],
        end_date=sample_date_range['end_date']
    )
    assert len(df) <= 31  # 最多31天
```

## Mocking 外部依赖

### 使用 monkeypatch

```python
def test_provider_with_mock(monkeypatch):
    """Mock外部API调用"""
    from akshare_one.modules.historical import EastMoneyProvider
    
    # 模拟请求
    def mock_fetch(*args, **kwargs):
        return pd.DataFrame({
            'timestamp': ['2024-01-01'],
            'open': [10.0],
            'high': [10.5],
            'low': [9.5],
            'close': [10.2],
            'volume': [1000],
        })
    
    provider = EastMoneyProvider(symbol="600000", interval="day")
    monkeypatch.setattr(provider, '_fetch_data', mock_fetch)
    
    df = provider.get_hist_data()
    assert not df.empty
```

### 使用 responses 库

```python
import responses

@responses.activate
def test_http_request():
    """Mock HTTP响应"""
    responses.add(
        responses.GET,
        'https://api.example.com/data',
        json={'data': [...]},
        status=200
    )
    
    # 代码会使用mock的响应
    result = fetch_data()
    assert result is not None
```

## 参数化测试

使用 `@pytest.mark.parametrize` 测试多组参数：

```python
@pytest.mark.parametrize("symbol,expected_count", [
    ("600000", 1),      # 上证A股
    ("000001", 1),      # 深证A股
    ("300750", 1),      # 创业板
])
def test_different_symbols(symbol, expected_count):
    """测试不同股票代码"""
    df = get_basic_info(symbol)
    assert len(df) == expected_count

@pytest.mark.parametrize("interval", ["day", "week", "month"])
def test_different_intervals(interval):
    """测试不同时间粒度"""
    df = get_hist_data("600000", interval=interval)
    assert not df.empty
```

## 测试最佳实践

### 1. 测试命名

```python
# ✅ 好的命名
def test_get_hist_data_returns_correct_columns():
def test_invalid_symbol_raises_error():
def test_multi_source_failover_works():

# ❌ 不好的命名
def test_hist_data():
def test_error():
def test_1():
```

### 2. 单一职责

```python
# ✅ 每个测试只验证一件事
def test_data_structure():
    """验证返回的数据结构"""
    df = get_hist_data("600000")
    assert 'timestamp' in df.columns

def test_data_not_empty():
    """验证数据不为空"""
    df = get_hist_data("600000")
    assert not df.empty

# ❌ 测试太多事情
def test_all():
    df = get_hist_data("600000")
    assert not df.empty
    assert 'timestamp' in df.columns
    assert len(df) > 100
    assert df['close'].min() > 0
    # ... 更多断言
```

### 3. 使用断言消息

```python
# ✅ 清晰的断言消息
assert not df.empty, f"Expected non-empty DataFrame for symbol 600000"

# ❌ 无消息
assert not df.empty
```

### 4. 清理测试数据

```python
def test_with_cleanup():
    # 测试前准备
    temp_file = create_temp_file()
    
    try:
        # 测试逻辑
        result = process(temp_file)
        assert result.success
    finally:
        # 清理
        os.remove(temp_file)
```

### 5. 隔离测试

```python
# ✅ 使用 fixture 管理状态
@pytest.fixture
def clean_cache():
    """清理缓存的fixture"""
    yield
    clear_cache()  # 测试后清理

def test_something(clean_cache):
    # 测试在一个干净的环境中运行
    pass
```

## 编写新测试的检查清单

- [ ] 测试文件以 `test_` 开头或以 `_test.py` 结尾
- [ ] 测试函数以 `test_` 开头
- [ ] 测试类以 `Test` 开头且不包含 `__init__`
- [ ] 使用断言验证预期结果
- [ ] 包含异常测试
- [ ] 使用 fixtures 避免重复代码
- [ ] 测试是独立的，不依赖执行顺序
- [ ] 使用有意义的断言消息
- [ ] 保持测试简单，只测试一件事
- [ ] 运行测试并确保通过

## 持续集成

测试在 GitHub Actions 中自动运行：

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=akshare_one
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 性能测试

### 基准测试

```python
import time

def test_performance():
    start = time.perf_counter()
    
    df = get_hist_data("600000")
    
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0, f"Query took too long: {elapsed}s"
```

### 使用 pytest-benchmark

```python
def test_benchmark(benchmark):
    result = benchmark(get_hist_data, "600000")
    assert result is not None
```

## 测试覆盖率报告

运行覆盖率并生成报告：

```bash
# 生成HTML报告
pytest --cov=akshare_one --cov-report=html

# 生成XML报告（CI使用）
pytest --cov=akshare_one --cov-report=xml

# 只计算覆盖率，不运行测试
pytest --collect-only
```

### 覆盖率阈值

在 `pyproject.toml` 中设置：

```toml
[tool.coverage.report]
fail_under = 80  # 覆盖率低于80%视为失败
exclude_lines = [
    'pragma: no cover',
    'def __repr__',
    'raise AssertionError',
    'raise NotImplementedError',
]
```

## 常见测试问题

### Q: 测试太慢怎么办？

**A**:
1. 使用 `@pytest.mark.slow` 标记慢测试
2. 运行测试时跳过慢测试：`pytest -m "not slow"`
3. 使用缓存减少重复请求

### Q: 如何处理外部API依赖？

**A**: 使用 mocking 隔离外部依赖：

```python
@patch('akshare_one.modules.historical.eastmoney.requests.get')
def test_with_mock(mock_get):
    mock_get.return_value.json.return_value = {...}
    # 测试...
```

### Q: 测试数据不一致怎么办？

**A**: 使用固定日期范围，避免实时数据变化：

```python
def test_snapshot():
    df = get_hist_data("600000", start_date="2024-01-01", end_date="2024-01-05")
    # 固定日期范围，结果稳定
```

### Q: 如何调试失败的测试？

**A**:
```bash
# 只运行失败的测试
pytest --last-failed

# 在失败时进入pdb调试
pytest --pdb

# 显示print输出
pytest -s

# 详细输出
pytest -vv
```

## 贡献测试

### 为新功能添加测试

1. 创建或修改对应的测试文件
2. 添加单元测试覆盖所有分支
3. 添加集成测试验证流程
4. 添加异常测试验证错误处理
5. 确保覆盖率不下降

### 测试模板

```python
"""Tests for <module_name>"""

import pytest
import pandas as pd
from akshare_one.modules import <module>

class Test<ModuleName>:
    """Test suite for <module_name>"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Arrange
        symbol = "600000"
        
        # Act
        result = <module>.function(symbol)
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
    
    def test_invalid_parameters(self):
        """Test error handling for invalid parameters"""
        with pytest.raises(InvalidParameterError):
            <module>.function("invalid")
    
    def test_data_format(self):
        """Test output data format"""
        df = <module>.function("600000")
        required = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        assert all(col in df.columns for col in required)
```

## 总结

AKShare One 的测试体系提供：

✅ **高覆盖率** - >80% 代码覆盖率
✅ **全面测试** - 单元、集成、契约测试
✅ **易于运行** - `pytest` 一键执行
✅ **持续集成** - GitHub Actions 自动测试
✅ **性能监控** - 基准测试和性能断言
✅ **易于贡献** - 清晰的测试模板和指南

编写高质量的测试是保证代码可靠性的关键，请务必为新功能添加完整的测试。
