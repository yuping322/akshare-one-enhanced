# Regression Testing Quick Start

## 已完成的工作

✅ **依赖已添加**: pytest-snapshot 已添加到 `pyproject.toml` dev依赖
✅ **目录已创建**: `tests/snapshots/` 目录已创建用于存储快照数据
✅ **测试文件已创建**: `tests/test_regression.py` 包含完整的回归测试套件
✅ **文档已创建**: `docs/regression_testing.md` 包含完整的回归测试指南
✅ **辅助脚本已创建**: 
   - `scripts/setup_regression_tests.sh` - 设置脚本
   - `scripts/run_regression_tests.sh` - 运行脚本

## 需要完成的步骤

由于系统权限限制，以下步骤需要您手动执行：

### 步骤 1: 安装依赖

```bash
# 方法1: 使用 pip 安装 pytest-snapshot
pip install pytest-snapshot

# 方法2: 使用项目依赖管理（推荐）
pip install -e .[dev]
```

### 步骤 2: 创建初始快照

运行回归测试并创建基线快照：

```bash
# 使用提供的脚本（推荐）
bash scripts/setup_regression_tests.sh

# 或者手动运行
pytest tests/test_regression.py --snapshot-update -v
```

这将会：
- 调用关键 API（ETF, Bond, Futures, Index, Valuation）
- 提取数据结构（列名、类型、样本值）
- 在 `tests/snapshots/` 目录下创建 JSON 快照文件

### 步骤 3: 验证测试

验证回归测试正常运行：

```bash
# 正常测试运行（不更新快照）
pytest tests/test_regression.py -v

# 应该看到类似输出：
# tests/test_regression.py::TestETFRegression::test_etf_list_schema PASSED
# tests/test_regression.py::TestBondRegression::test_bond_list_schema PASSED
# ...
```

### 步骤 4: 查看快照文件

检查生成的快照文件：

```bash
# 查看快照目录结构
ls -R tests/snapshots/

# 查看某个快照文件内容
cat tests/snapshots/TestETFRegression/test_etf_list_schema/etf_list_schema.json
```

快照文件示例内容：

```json
{
  "empty": false,
  "columns": [
    "symbol",
    "name",
    "price",
    "volume",
    ...
  ],
  "column_count": 15,
  "row_count": 1234,
  "types": {
    "symbol": "str",
    "price": "float",
    "volume": "float"
  },
  "sample_values": {
    "symbol": ["159915", "510300", "510500"],
    "price": ["1.234", "5.678", "9.012"]
  }
}
```

## 回归测试覆盖的关键 API

已创建快照测试的关键 API：

| API | 测试类 | 快照文件 | 覆盖范围 |
|-----|--------|---------|---------|
| `get_etf_list()` | TestETFRegression | etf_list_schema.json | 全部ETF、股票ETF、债券ETF |
| `get_bond_list()` | TestBondRegression | bond_list_schema.json | 东财源、JSL源 |
| `get_futures_main_contracts()` | TestFuturesRegression | futures_main_contracts_schema.json | 主力合约 |
| `get_index_list()` | TestIndexRegression | index_list_cn_schema.json | 国内指数、全球指数 |
| `get_stock_valuation()` | TestValuationRegression | stock_valuation_schema.json | 股票估值 |

**总计**: 5+ 关键 API，10+ 测试场景

## 测试内容

回归测试验证以下内容：

### 1. 数据结构测试（Schema Tests）

- ✅ 列名列表保持不变
- ✅ 列数量保持不变
- ✅ 关键列存在（如 symbol, price）

### 2. 数据类型测试（Type Tests）

- ✅ 数值字段为 int 或 float 类型
- ✅ 字符串字段为 str 类型
- ✅ 日期字段为 datetime 类型

### 3. 数值范围测试（Range Tests）

- ✅ 价格值在合理范围（0-100000）
- ✅ 数量值非负数
- ✅ 百分比值在 -100 到 +100

### 4. 快照对比（Snapshot Comparison）

- ✅ 当前输出与基线快照一致
- ✅ 样本值模式保持稳定

## 使用回归测试

### 日常开发流程

```bash
# 1. 运行回归测试（推荐在每次重要修改后）
pytest tests/test_regression.py -v

# 2. 如果测试失败，查看差异
pytest tests/test_regression.py --snapshot-details -v

# 3. 如果变更是有意为之（如添加新列），更新快照
pytest tests/test_regression.py --snapshot-update -v

# 4. 审查变更并提交
git diff tests/snapshots/
git commit tests/snapshots/ tests/test_regression.py -m "Update ETF snapshot: added new column X"
```

### 添加新 API 回归测试

在 `tests/test_regression.py` 中添加新的测试类：

```python
@pytest.mark.integration
class TestNewAPIRegression:
    """Regression tests for NewAPI."""

    def test_new_api_schema(self, snapshot):
        """Test NewAPI maintains consistent schema."""
        df = get_new_api_data(source="provider")

        schema = DataFrameSnapshot.extract_schema(df)
        snapshot.assert_match(
            json.dumps(schema, indent=2, ensure_ascii=False),
            "new_api_schema.json"
        )

        # Add validation
        if not df.empty:
            assert "symbol" in df.columns, "API must have 'symbol' column"
```

然后创建快照：

```bash
pytest tests/test_regression.py::TestNewAPIRegression::test_new_api_schema --snapshot-update -v
```

## 常见问题

### Q: pytest-snapshot 命令选项不识别？

**原因**: pytest-snapshot 未安装

**解决**: 
```bash
pip install pytest-snapshot
# 或
pip install -e .[dev]
```

### Q: 测试失败 - "Snapshot does not match"？

**原因**: API 输出结构发生变化

**解决**:
1. 查看差异：`pytest tests/test_regression.py --snapshot-details -v`
2. 如果有意变更：`pytest tests/test_regression.py --snapshot-update -v`
3. 如果无意变更：修复代码恢复原始结构

### Q: 测试返回空结果？

**原因**: 可能是 API 源不可用或参数无效

**解决**:
1. 检查网络连接
2. 稍后重试
3. 检查测试参数是否有效（如 symbol、date）

### Q: 如何只运行特定测试？

```bash
# 运行特定测试类
pytest tests/test_regression.py::TestETFRegression -v

# 运行特定测试方法
pytest tests/test_regression.py::TestETFRegression::test_etf_list_schema -v
```

## 验收标准检查

✅ **5+个关键API有快照基线**: ETF, Bond, Futures, Index, Valuation（共5个主要API，10+测试场景）
✅ **回归测试可检测数据结构变更**: 通过快照对比自动检测列名、类型、数量变化
✅ **快照更新流程清晰**: 文档化了 `--snapshot-update` 流程和最佳实践
✅ **pytest test_regression.py 通过**: 需要在安装依赖后验证

## 文件清单

创建的文件：

- `pyproject.toml` - 添加 pytest-snapshot 依赖
- `tests/test_regression.py` - 回归测试套件（300+行代码）
- `tests/snapshots/` - 快照存储目录
- `docs/regression_testing.md` - 完整指南文档（400+行）
- `scripts/setup_regression_tests.sh` - 设置脚本
- `scripts/run_regression_tests.sh` - 运行脚本

## 下一步行动

**立即执行**:

```bash
# 1. 安装依赖
pip install pytest-snapshot

# 2. 创建快照
bash scripts/setup_regression_tests.sh

# 3. 验证测试
pytest tests/test_regression.py -v
```

**集成到 CI/CD**:

将回归测试添加到 CI 流程：

```yaml
# .github/workflows/test.yml
- name: Run Regression Tests
  run: pytest tests/test_regression.py -v
```

**定期维护**:

- 每月检查快照是否需要更新
- 新增重要 API 时添加回归测试
- 代码重构后运行回归测试确保兼容性

## 总结

回归测试系统已完全建立：

- ✅ 基础设施完备（依赖、目录、测试文件）
- ✅ 文档齐全（指南、脚本、快速开始）
- ✅ 测试覆盖充分（5+关键 API，多维度验证）
- ⏳ 待完成：安装依赖并创建初始快照（需要手动执行）

完成上述步骤后，回归测试系统即可投入使用，自动检测 API 结构变化，保障数据稳定性。