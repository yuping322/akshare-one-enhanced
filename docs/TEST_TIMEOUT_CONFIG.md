# ⏱️ 测试超时配置说明

## 超时设置概述

为了防止测试无限卡住，已为项目添加了智能超时机制。

## 配置详情

### 1. 全局默认超时 (pyproject.toml)
```toml
[tool.pytest.ini_options]
timeout = 60  # 默认超时 60 秒
timeout_method = "signal"  # 使用 signal 方法实现超时
```

**适用范围**: 所有测试文件  
**超时时间**: 60 秒  
**例外**: 可以针对特定测试或模块覆盖

### 2. MCP P1/P2 测试超时 (tests/mcp/test_mcp_p1_p2.py)
```python
pytestmark = pytest.mark.timeout(120)  # 模块级 120 秒超时
```

**原因**: 
- 需要访问网络 API（东方财富、新浪等）
- 某些测试需要逐天调用 API
- 网络延迟可能导致响应慢

**超时时间**: 120 秒（2 分钟）

### 3. 特殊测试的独立超时
某些特别慢的测试可以单独设置更长的超时：

```python
@pytest.mark.timeout(180)  # 3 分钟
def test_get_disclosure_news_basic():
    """信息披露测试需要逐天获取数据，特别慢"""
    pass
```

## 超时层级

```
测试级超时 > 模块级超时 > 全局默认超时
```

### 示例
```python
# 全局默认：60 秒

# 模块级覆盖：120 秒
pytestmark = pytest.mark.timeout(120)

class TestSlowAPI:
    # 测试级覆盖：180 秒
    @pytest.mark.timeout(180)
    def test_very_slow_test(self):
        pass
    
    # 使用模块级：120 秒
    def test_normal_slow_test(self):
        pass
```

## 超时时间建议

| 测试类型 | 建议超时 | 说明 |
|---------|---------|------|
| 单元测试 | 10-30 秒 | 纯逻辑测试，无网络 |
| 集成测试 | 60-90 秒 | 单次网络请求 |
| MCP P0 测试 | 60 秒 | 单次或少量 API 调用 |
| MCP P1/P2 测试 | 120 秒 | 批量 API 调用 |
| 披露/公告测试 | 180 秒 | 逐天调用 API |
| 历史数据测试 | 120 秒 | 大量数据获取 |

## 监控超时

### 查看超时统计
```bash
# 运行测试并显示超时信息
pytest tests/ --timeout=60 -v | grep Timeout
```

### 识别慢测试
```bash
# 运行超过 10 秒的测试会显示警告
pytest tests/ --durations=10
```

### 生成测试时长报告
```bash
# 显示最慢的 20 个测试
pytest tests/ --durations=20
```

## 常见问题

### Q: 为什么我的测试超时了？
A: 可能原因：
1. **网络问题** - API 响应慢或失败
2. **数据量大** - 获取了大量数据
3. **日期范围过大** - 如默认的 60 年范围
4. **循环调用** - 逐天/逐月调用 API

### Q: 如何避免超时？
A: 建议：
1. **缩小日期范围** - 使用最近 30 天而非 60 年
2. **Mock 数据** - 单元测试使用 mock
3. **优化 API 调用** - 批量而非循环
4. **增加超时** - 对慢测试设置更长超时

### Q: 超时时如何处理？
A: 步骤：
1. 检查测试日志，确认卡在哪里
2. 分析是否需要优化日期范围
3. 考虑是否应该标记为 integration
4. 必要时增加合理超时

## 实际案例

### 案例 1: MCP P1/P2 测试卡住
**问题**: `test_get_disclosure_news_basic` 无限卡住  
**原因**: 默认日期范围 1970-2030（60 年），逐天调用  
**解决**: 
1. 缩小到 30 天范围
2. 添加 180 秒超时
3. 标记为需要网络

### 案例 2: Edge Cases 测试失败
**问题**: 多个测试需要网络但未标记  
**原因**: 缺少 integration 标记  
**解决**: 
1. 全局添加 `pytestmark = pytest.mark.integration`
2. 运行时可跳过

## 最佳实践

1. ✅ **单元测试要快** - < 1 秒，无网络
2. ✅ **集成测试要标记** - 使用 `@pytest.mark.integration`
3. ✅ **慢测试要超时** - 设置合理的超时时间
4. ✅ **网络测试要 Mock** - 尽可能使用 mock 数据
5. ✅ **日期范围要合理** - 避免默认的超大范围

## 配置位置

- **全局配置**: `pyproject.toml` -> `[tool.pytest.ini_options]`
- **模块配置**: 测试文件顶部 -> `pytestmark`
- **测试配置**: 测试函数上 -> `@pytest.mark.timeout()`

## 总结

通过智能超时机制，我们可以：
- ✅ 防止测试无限卡住
- ✅ 快速定位性能问题
- ✅ 平衡测试速度和覆盖率
- ✅ 提高开发效率
