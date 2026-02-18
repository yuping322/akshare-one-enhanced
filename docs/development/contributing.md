# 贡献指南

感谢您考虑为 AKShare One 项目做贡献！本文档提供了详细的开发指南和贡献流程。

## 行为准则

本项目遵守 [Contributor Covenant](https://www.contributor-covenant.org/)，旨在营造一个开放、包容的社区环境。

### 我们的承诺

- 使用友善和专业的语言
- 尊重不同的观点和经验
- 接受建设性批评
- 专注于社区的最佳利益

###  unacceptable 行为

- 使用性化语言或暗示
- 侮辱或贬低性评论
- 公开或私下骚扰
- 未经许可公开他人信息

## 如何贡献

### 报告 Bug

如果您发现 bug，请在 [GitHub Issues](https://github.com/zwldarren/akshare-one/issues) 创建 issue，包含以下信息：

1. **清晰标题** - 简明扼要描述问题
2. **重现步骤** - 详细说明如何重现 bug
3. **预期行为** - 描述预期结果
4. **实际行为** - 描述实际结果
5. **环境信息** - Python 版本、操作系统等
6. **附加信息** - 日志、截图等

**模板**：

```markdown
## 描述
[简明描述 bug]

## 重现步骤
1. [第一步]
2. [第二步]
3. [第三步]

## 预期行为
[描述预期结果]

## 实际行为
[描述实际结果]

## 环境
- Python: [版本]
- OS: [操作系统]
- AKShare One: [版本]

## 附加信息
[日志、截图等]
```

### 提出建议

我们欢迎新功能建议！请先：

1. 搜索 existing issues 避免重复
2. 查看项目路线图（见 [architecture.md](./architecture.md)）
3. 在 issue 中清晰描述：
   - 使用场景
   - 预期功能
   - 潜在影响

### 提交 Pull Request

#### 准备工作

1. **Fork 项目**

```bash
# 在 GitHub 上fork项目，然后克隆您的fork
git clone https://github.com/YOUR_USERNAME/akshare-one.git
cd akshare-one
```

2. **添加上游远程仓库**

```bash
git remote add upstream https://github.com/zwldarren/akshare-one.git
```

3. **创建特性分支**

```bash
git checkout -b feature/AmazingFeature
# 或
git checkout -b fix/issue-123
```

#### 开发流程

1. **设置开发环境**

```bash
# 安装依赖
pip install -e ".[dev]"

# 或手动安装
pip install -e .
pip install pytest pytest-cov ruff mypy pre-commit
```

2. **立即可用的pre-commit检查**

```bash
# 安装pre-commit钩子
pre-commit install

# 手动运行检查
pre-commit run --all-files
```

3. **编写代码**

遵循项目规范：

- ✅ 使用类型提示
- ✅ 编写文档字符串
- ✅ 遵循PEP 8
- ✅ 添加适当测试

4. **运行测试**

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_stock.py

# 查看覆盖率
pytest --cov=akshare_one --cov-report=html

# 打开覆盖率报告
open htmlcov/index.html
```

5. **代码质量检查**

```bash
# Ruff 格式化和检查
ruff format src/
ruff check src/

# MyPy 类型检查
mypy src/

# 确保所有检查通过
pre-commit run --all-files
```

6. **提交代码**

```bash
git add .
git commit -m "feat: add new data source support"

# 推送
git push origin feature/AmazingFeature
```

**Commit 规范**：

```
类型: 简短描述

详细描述（可选）

Closes #123
```

**类型**:
- `feat`: 新功能
- `fix`: bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 添加测试
- `chore`: 构建过程或辅助工具的变动

7. **创建 Pull Request**

- 访问 GitHub，点击 "Compare & pull request"
- 填写 PR 模板
- 关联相关 issue
- 等待代码审查

#### PR 审查流程

1. **自动化检查** - CI 运行测试和代码质量检查
2. **代码审查** - 维护者审查代码
3. **反馈修订** - 根据反馈修改代码
4. **合并** - 维护者合并 PR

### 开发规范

#### 代码风格

- 遵循 [PEP 8](https://pep8.org/)
- 使用 4 个空格缩进
- 最大行长度 88 字符（与 Ruff 兼容）
- 使用双引号字符串 `"`

```python
# ✅ 好的例子
def get_hist_data(
    symbol: str,
    interval: str = "day",
    start_date: str | None = None,
) -> pd.DataFrame:
    """获取历史数据"""
    pass
```

#### 类型提示

**必须使用类型提示**：

```python
# ✅ 好的类型提示
from typing import Optional
import pandas as pd

def get_data(
    symbol: str,
    start_date: Optional[str] = None,
) -> pd.DataFrame:
    pass
```

#### 文档字符串

使用 Google 风格 docstrings：

```python
def get_hist_data(
    symbol: str,
    interval: str = "day",
    start_date: str = "1970-01-01",
    end_date: str = "2030-12-31",
) -> pd.DataFrame:
    """获取股票历史行情数据
    
    Args:
        symbol: 股票代码（6位数字）
        interval: 时间粒度（day/week/month/minute）
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
    
    Returns:
        包含历史数据的DataFrame，字段包括：
        - timestamp: 时间戳
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
    
    Raises:
        InvalidParameterError: 参数无效时抛出
        DataSourceUnavailableError: 数据源不可用时抛出
    
    Example:
        >>> df = get_hist_data("600000", start_date="2024-01-01")
        >>> print(df.head())
    """
    pass
```

#### 异常处理

使用项目定义的异常类：

```python
from akshare_one.modules import (
    InvalidParameterError,
    DataSourceUnavailableError,
    NoDataError,
)

def get_data(symbol: str):
    if not symbol.isdigit() or len(symbol) != 6:
        raise InvalidParameterError(f"Invalid symbol: {symbol}")
    
    try:
        # 数据获取逻辑
        pass
    except requests.Timeout:
        raise DataSourceUnavailableError("Request timeout")
```

#### 日志记录

使用 `logging` 模块：

```python
import logging

logger = logging.getLogger(__name__)

def fetch_data():
    logger.debug("Fetching data for %s", symbol)
    try:
        data = api_call()
        logger.info("Successfully fetched %d records", len(data))
        return data
    except Exception as e:
        logger.error("Failed to fetch data: %s", e, exc_info=True)
        raise
```

### 测试要求

- ✅ 为新功能添加单元测试
- ✅ 覆盖率不下降
- ✅ 关键路径有集成测试
- ✅ 异常情况有测试覆盖
- ✅ 测试命名清晰

```python
def test_get_hist_data_with_dates():
    """Test get_hist_data with custom date range"""
    df = get_hist_data("600000", start_date="2024-01-01", end_date="2024-01-31")
    assert len(df) > 0

def test_invalid_symbol_raises():
    """Test that invalid symbol raises InvalidParameterError"""
    with pytest.raises(InvalidParameterError):
        get_hist_data("invalid")
```

## 添加新数据源

### 实现步骤

1. **创建 Provider 类**

```python
# src/akshare_one/modules/historical/my_source.py
from .base import HistoricalDataProvider

class MySourceHistorical(HistoricalDataProvider):
    """MySource 历史数据提供者"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_name = "my_source"
    
    def get_hist_data(self) -> pd.DataFrame:
        """获取历史数据"""
        # 实现数据获取逻辑
        # 返回标准格式的DataFrame
        pass
```

2. **在 Factory 注册**

```python
# src/akshare_one/modules/historical/factory.py
from .my_source import MySourceHistorical

class HistoricalDataFactory:
    _providers = {
        "eastmoney": EastMoneyHistorical,
        "eastmoney_direct": EastMoneyDirectHistorical,
        "sina": SinaHistorical,
        "my_source": MySourceHistorical,  # 添加
    }
```

3. **编写测试**

```python
# tests/test_my_source.py
def test_my_source_basic():
    from akshare_one.modules.historical.factory import HistoricalDataFactory
    
    provider = HistoricalDataFactory.get_provider(
        "my_source",
        symbol="600000",
        interval="day"
    )
    
    df = provider.get_hist_data()
    assert not df.empty
    assert all(col in df.columns for col in ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
```

4. **更新文档**

- 更新 `docs/api/` 中的对应文档
- 更新 `README.md` 的功能列表
- 如有必要，更新迁移指南

### 质量检查清单

- [ ] Provider 类继承正确的基类
- [ ] 实现必需的抽象方法
- [ ] 返回标准化的 DataFrame 格式
- [ ] 正确处理异常
- [ ] 使用类型提示
- [ ] 编写文档字符串
- [ ] 在 Factory 中注册
- [ ] 通过所有新测试
- [ ] 不影响现有功能
- [ ] 更新对应文档

## 项目结构

```
akshare-one/
├── src/akshare_one/
│   ├── __init__.py              # 主API导出
│   ├── http_client.py           # HTTP客户端
│   ├── indicators.py            # 技术指标
│   ├── mcp/                     # MCP服务器
│   └── modules/
│       ├── cache.py             # 缓存系统
│       ├── multi_source.py      # 多源路由器
│       ├── utils.py             # 工具函数
│       ├── historical/          # 历史数据模块
│       ├── realtime/            # 实时数据模块
│       ├── financial/           # 财务数据模块
│       └── ...                  其他模块
├── tests/                       # 测试
├── docs/                        # 文档
│   ├── getting-started/
│   ├── core-api/
│   ├── extended-modules/
│   ├── advanced/
│   ├── development/
│   └── migration/
├── examples/                    # 示例代码
├── pyproject.toml               # 项目配置
├── mkdocs.yml                   # 文档配置
└── README.md                    # 项目首页
```

## 开发工具

### 预提交钩子（pre-commit）

```bash
# 安装
pre-commit install

# 手动运行
pre-commit run --all-files
```

自动执行：
- Ruff 格式化和检查
- MyPy 类型检查
- 检查过大文件
- 检查 trailing whitespace

### 代码质量工具

```bash
# 格式化代码
ruff format src/

# 检查代码
ruff check src/

# 类型检查
mypy src/

# 所有检查
pre-commit run --all-files
```

### 调试工具

```bash
# 进入Python环境
python -i -c "import akshare_one; print(akshare_one.__version__)"

# 查看缓存统计
python -c "from akshare_one.modules.cache import get_cache_stats; print(get_cache_stats())"
```

## 发布流程

### 版本号规则

遵循 [语义化版本](https://semver.org/)：

```
主版本.次版本.修订号  (MAJOR.MINOR.PATCH)

示例：
1.0.0  - 首次发布
1.0.1  - bug修复
1.1.0  - 新功能，向后兼容
2.0.0  - 重大更新，可能不兼容
```

### 发布步骤

1. **更新版本号**

```python
# src/akshare_one/__init__.py
__version__ = "0.5.1"
```

2. **更新 CHANGELOG.md**

```markdown
## [0.5.1] - 2024-02-15

### Added
- 新增 XXX 数据源支持

### Fixed
- 修复 XXX 问题
```

3. **创建 Release PR**

```bash
git checkout -b release/v0.5.1
# 更新版本号和changelog
git commit -m "chore: prepare release v0.5.1"
git push origin release/v0.5.1
# 创建PR并合并到main
```

4. **创建Release**

```bash
git checkout main
git pull origin main
git tag -a v0.5.1 -m "Release v0.5.1"
git push origin v0.5.1
```

5. **PyPI上传**

```bash
# 构建包
python -m build

# 上传
twine upload dist/*
```

## 常见问题

### Q: 如何开始第一个贡献？

**A**:
1. 查看 [GitHub Issues](https://github.com/zwldarren/akshare-one/issues) 中的 `good first issue` 标签
2. 阅读相关文档，理解项目架构
3. 在 issue 中留言表示想参与
4. 按照开发流程进行

### Q: 运行测试时网络超时怎么办？

**A**: 设置合理的超时和重试：

```bash
# 增加超时
export AKSHARE_ONE_TIMEOUT=60

# 或在测试中使用mock数据
pytest --mock-data
```

### Q: 如何处理上游API变化？

**A**:
1. 更新对应的 Provider 实现
2. 添加 `UpstreamChangedError` 异常
3. 更新相关测试和数据验证
4. 在 changelog 中记录

### Q: 代码审查一般需要多长时间？

**A**: 我们会在 2-3 个工作日内进行初步审查。复杂功能可能需要更长时间。

## 获取帮助

- **文档**: 阅读 [docs/](./) 目录
- **Issues**: [GitHub Issues](https://github.com/zwldarren/akshare-one/issues)
- **Discussions**: [GitHub Discussions](https://github.com/zwldarren/akshare-one/discussions)
- **Email**: [项目维护者](mailto:zwldarren@gmail.com)

## 致谢

感谢所有贡献者！🎉

---

最后更新: 2024年2月
