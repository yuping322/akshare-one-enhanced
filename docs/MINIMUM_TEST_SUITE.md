# AKShare One 最小测试集指南

## 新用户快速验证流程

安装完成后，建议运行以下最小测试集验证系统功能。

### 1. 核心功能验证（必须）

**安装验证脚本**（推荐首选）：
```bash
python scripts/verify_installation.py
```

该脚本会自动测试：
- ✓ 模块导入
- ✓ 数据过滤
- ✓ Factory初始化
- ✓ 数据Schema
- ✓ Pandas兼容性
- ✓ 可选依赖（TA-Lib、MCP）

**预期结果**：所有7项测试通过（网络测试可选跳过）

---

### 2. 离线单元测试（推荐）

验证核心功能无需网络访问：
```bash
# 运行离线测试（跳过集成测试）
python -m pytest tests/ -m "not integration" --tb=no -q
```

**预期结果**：
- 通过率 ≥ 95%（当前：~830/891 = 93%）
- 主要测试类别：字段命名契约、参数验证、异常处理

**快速验证模式**（仅测试核心模块）：
```bash
python -m pytest tests/test_field_naming.py tests/test_api_field_contracts.py -v
```

---

### 3. 示例程序验证（可选）

验证API实际调用（需要网络）：
```bash
# 测试北向资金示例
python examples/northbound_example.py

# 测试资金流示例
python examples/fundflow_example.py
```

**预期输出**：
- 程序无错误退出
- 输出包含数据表格（DataFrame格式）
- 字段命名符合标准（date、symbol、close等）

**注意**：网络测试可能因代理或API变更失败，这属于外部因素，不影响核心功能。

---

### 4. 契约测试（开发验证）

验证API契约稳定性：
```bash
python -m pytest tests/test_api_contract.py tests/test_api_field_contracts.py -v
```

**预期结果**：
- 字段命名契约：102个测试全部通过
- API映射契约：23个测试通过

---

## 测试分层说明

AKShare One采用分层测试策略：

### Unit Tests（离线可运行）
- **标记**：无标记或 `-m "not integration"`
- **特点**：使用Mock数据，无需网络
- **覆盖率**：核心逻辑验证
- **稳定性**：100%通过（网络无关）

### Integration Tests（需要网络）
- **标记**：`@pytest.mark.integration`
- **特点**：真实API调用
- **覆盖率**：数据源兼容性验证
- **稳定性**：依赖网络和上游API状态

### Contract Tests（契约验证）
- **标记**：`@pytest.mark.contract`
- **特点**：验证API行为一致性
- **覆盖率**：字段命名、异常语义、返回结构
- **稳定性**：100%通过（Mock数据）

---

## 新用户验证基准

### 最低验收标准（产品级可用）

**必须在干净机器上达成**：
1. ✓ `pip install -e .` 成功完成
2. ✓ `python scripts/verify_installation.py` 全部通过（网络测试可跳过）
3. ✓ `python -m pytest tests/ -m "not integration"` 通过率 ≥ 95%
4. ✓ 至少1个示例程序运行成功（如 northbound_example.py）

### 完整验收标准（推荐）

**如果网络可用**：
1. ✓ 离线测试100%通过
2. ✓ Integration测试通过率 ≥ 90%（允许个别API失败）
3. ✓ 所有示例程序运行无错误
4. ✓ 契约测试125个全部通过

---

## 测试失败诊断

### 网络错误
**症状**：`ProxyError`, `ConnectionError`, `Timeout`
**原因**：网络环境限制
**解决**：使用离线测试模式 `-m "not integration"`

### Mock Fixture错误
**症状**：`fixture 'mocker' not found`
**原因**：pytest-mock未安装
**解决**：`pip install pytest-mock` 或 `pip install -e ".[dev]"`

### 字段类型错误
**症状**：`Price column must be float type`
**原因**：数值类型契约测试（标记为integration）
**解决**：这些测试需要网络，离线模式自动跳过

---

## 常见问题解答

### Q: 为什么有些测试需要网络？
A: Integration测试验证真实API调用，确保与上游数据源兼容。离线测试已覆盖核心功能。

### Q: 离线测试失败怎么办？
A: 检查错误类型：
- Mock相关：安装pytest-mock
- 其他失败：查看日志定位问题

### Q: 示例程序返回空数据怎么办？
A: 可能原因：
- 数据源API变更（已知AkShare版本兼容问题）
- 查询时间范围内无数据
- 网络限制

建议检查：
1. AkShare版本是否在支持范围（当前：1.18.23-1.18.51）
2. 查询参数是否合理
3. 使用其他数据源（如sina备用）

---

## 测试命令速查表

```bash
# 快速验证（推荐）
python scripts/verify_installation.py

# 离线测试（推荐）
pytest -m "not integration" -q

# 完整测试（需要网络）
pytest -v

# 仅契约测试
pytest -m contract -v

# 仅集成测试（需要网络）
pytest -m integration -v

# 特定模块测试
pytest tests/test_field_naming.py -v

# 覆盖率报告
pytest --cov=src/akshare_one --cov-report=html
```

---

**文档版本**：v0.5.0
**更新日期**：2026-04-04
**维护者**：AkShare One Team