# 贡献指南

感谢您考虑为 AKShare One 项目做贡献！本指南将帮助您了解如何参与项目开发。

## 快速开始

1. **Fork 项目** - 在 GitHub 上fork仓库
2. **克隆代码** - `git clone https://github.com/YOUR_USERNAME/akshare-one.git`
3. **安装依赖** - `pip install -e ".[dev]"`
4. **运行测试** - `pytest` 确保环境正常
5. **创建分支** - `git checkout -b feature/YourFeature`

## 行为准则

本项目遵守 [Contributor Covenant](https://www.contributor-covenant.org/)，旨在营造一个开放、包容的社区环境。

请使用友善和专业的语言，尊重不同的观点和经验。

## 如何贡献

### 报告 Bug

如果您发现 bug，请在 [GitHub Issues](https://github.com/zwldarren/akshare-one/issues) 创建 issue，包含以下信息：

- **重现步骤** - 如何复现问题
- **预期行为** - 预期结果
- **实际行为** - 实际结果
- **环境信息** - Python版本、操作系统等
- **附加信息** - 日志、截图等

### 提出新功能建议

1. 先搜索 existing issues 避免重复
2. 查看项目路线图（见 [docs/development/architecture.md](./docs/development/architecture.md)）
3. 在 issue 中清晰描述使用场景和预期功能

### 提交 Pull Request

#### 开发前准备

```bash
# 1. 克隆您的fork
git clone https://github.com/YOUR_USERNAME/akshare-one.git
cd akshare-one

# 2. 添加上游仓库
git remote add upstream https://github.com/zwldarren/akshare-one.git

# 3. 安装开发依赖
pip install -e ".[dev]"

# 4. 安装pre-commit钩子
pre-commit install
```

#### 开发流程

1. **创建特性分支**

```bash
git checkout -b feature/AmazingFeature
# 或修复bug
git checkout -b fix/issue-123
```

2. **编写代码**

遵循项目规范：
- ✅ 使用类型提示
- ✅ 编写文档字符串
- ✅ 遵循PEP 8
- ✅ 添加适当测试

3. **运行测试和检查**

```bash
# 运行所有测试
pytest

# 查看覆盖率
pytest --cov=akshare_one --cov-report=html

# 代码质量检查
ruff format src/
ruff check src/
mypy src/

# 或使用pre-commit运行所有检查
pre-commit run --all-files
```

4. **提交代码**

```bash
git add .
git commit -m "feat: add new data source support"
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
- `style`: 代码格式
- `refactor`: 重构
- `test`: 添加测试
- `chore`: 构建或工具变更

5. **推送并创建PR**

```bash
git push origin feature/AmazingFeature
```

然后在GitHub上创建Pull Request，填写模板并关联相关issue。

## 开发规范

### 代码风格

- 遵循 [PEP 8](https://pep8.org/)
- 4个空格缩进
- 最大行长度88字符
- 使用双引号字符串 `"`

### 类型提示

**所有函数都必须使用类型提示**：

```python
from typing import Optional
import pandas as pd

def get_hist_data(
    symbol: str,
    interval: str = "day",
    start_date: Optional[str] = None,
) -> pd.DataFrame:
    """获取历史数据"""
    pass
```

### 文档字符串

使用 Google 风格：

```python
def get_hist_data(symbol: str, interval: str = "day") -> pd.DataFrame:
    """获取历史数据
    
    Args:
        symbol: 股票代码（6位数字）
        interval: 时间粒度（day/week/month）
    
    Returns:
        包含历史数据的DataFrame
    
    Raises:
        InvalidParameterError: 参数无效时抛出
    
    Example:
        >>> df = get_hist_data("600000")
    """
    pass
```

### 异常处理

使用项目定义的异常类：

```python
from akshare_one.modules import (
    InvalidParameterError,
    DataSourceUnavailableError,
    NoDataError,
)

if not symbol.isdigit():
    raise InvalidParameterError(f"Invalid symbol: {symbol}")
```

### 测试要求

- ✅ 为新功能添加单元测试
- ✅ 覆盖率不下降（目标>80%）
- ✅ 关键路径有集成测试
- ✅ 异常情况有测试覆盖

**模板**：

```python
def test_get_hist_data():
    """Test basic functionality"""
    df = get_hist_data("600000")
    assert not df.empty
    assert 'timestamp' in df.columns

def test_invalid_symbol():
    """Test error handling"""
    with pytest.raises(InvalidParameterError):
        get_hist_data("invalid")
```

## 添加新数据源

### 实现步骤

1. **创建 Provider 类**（继承对应基类）

```python
# src/akshare_one/modules/historical/my_source.py
from .base import HistoricalDataProvider

class MySourceHistorical(HistoricalDataProvider):
    def get_hist_data(self) -> pd.DataFrame:
        # 实现
        pass
```

2. **在 Factory 注册**

```python
# src/akshare_one/modules/historical/factory.py
from .my_source import MySourceHistorical

class HistoricalDataFactory:
    _providers = {
        # ... 现有源
        "my_source": MySourceHistorical,
    }
```

3. **编写测试**

```python
def test_my_source():
    provider = HistoricalDataFactory.get_provider("my_source", symbol="600000")
    df = provider.get_hist_data()
    assert not df.empty
```

4. **更新文档**
   - 更新 API 文档
   - 更新 README 功能列表
   - 更新迁移指南（如适用）

### 质量检查清单

- [ ] Provider 继承正确的基类
- [ ] 实现所有必需方法
- [ ] 返回标准化的 DataFrame
- [ ] 使用类型提示和文档字符串
- [ ] 在 Factory 中注册
- [ ] 通过所有测试
- [ ] 不影响现有功能
- [ ] 更新相关文档

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
│       ├── historical/          # 历史数据
│       ├── realtime/            # 实时数据
│       ├── financial/           # 财务数据
│       └── ...                  其他模块
├── tests/                       # 测试
├── docs/                        # 文档
├── examples/                    # 示例
├── pyproject.toml               # 项目配置
├── mkdocs.yml                   # 文档配置
└── README.md                    # 项目首页
```

## 工具和脚本

### 开发依赖

```bash
# 核心依赖
pip install -e ".[dev]"

# 或手动安装
pip install pytest pytest-cov
pip install ruff mypy pre-commit
pip install build twine  # 发布
```

### 常用命令

```bash
# 测试
pytest                           # 所有测试
pytest tests/test_stock.py       # 特定文件
pytest -v                        # 详细输出
pytest --cov=akshare_one         # 覆盖率

# 代码质量
ruff format src/                 # 格式化
ruff check src/                  # 检查
mypy src/                        # 类型检查
pre-commit run --all-files       # 所有检查

# 构建和发布
python -m build                   # 构建包
twine check dist/*               # 检查包
twine upload dist/*              # 上传PyPI
```

### 预提交钩子

```bash
# 自动在git commit时运行检查
pre-commit install

# 手动运行
pre-commit run --all-files
```

包括：
- Ruff 格式化和检查
- MyPy 类型检查
- 文件大小检查
- trailing whitespace检查

## 获取帮助

- **文档**: 阅读 [docs/](./docs/) 目录
- **Issues**: [GitHub Issues](https://github.com/zwldarren/akshare-one/issues)
- **Discussions**: [GitHub Discussions](https://github.com/zwldarren/akshare-one/discussions)
- **示例**: 查看 [examples/](./examples/) 目录

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

---

**感谢您的贡献！** 🎉

有问题？随时在 issue 中提问。

最后更新: 2024年2月
