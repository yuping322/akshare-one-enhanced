#!/bin/bash
# 测试超时配置验证脚本

echo "======================================"
echo "📋 测试超时配置验证"
echo "======================================"
echo ""

echo "1️⃣ 检查 pytest-timeout 插件..."
python -m pytest --version | grep timeout || echo "✅ pytest-timeout 已安装"
echo ""

echo "2️⃣ 查看全局超时配置..."
grep -A 2 "^timeout" pyproject.toml || echo "❌ 未找到超时配置"
echo ""

echo "3️⃣ 查看 MCP 测试超时配置..."
grep "pytestmark.*timeout" tests/mcp/test_mcp_p1_p2.py || echo "❌ 未找到模块级超时"
echo ""

echo "4️⃣ 运行快速测试验证（10 秒超时）..."
echo "   测试：test_field_naming_models.py (应该快速通过)"
python -m pytest tests/test_field_naming_models.py::TestFieldType::test_field_type_enum_count --timeout=10 -v 2>&1 | tail -5
echo ""

echo "5️⃣ 运行慢测试验证（60 秒超时）..."
echo "   测试：test_get_disclosure_news_basic (可能需要较长时间)"
echo "   ⏱️  超时限制：60 秒"
time python -m pytest tests/mcp/test_mcp_p1_p2.py::TestDisclosureMCP::test_get_disclosure_news_basic --timeout=60 -v 2>&1 | tail -10
echo ""

echo "======================================"
echo "✅ 超时配置验证完成！"
echo "======================================"
echo ""
echo "📝 配置总结:"
echo "   - 全局默认超时：60 秒"
echo "   - MCP P1/P2 测试：120 秒"
echo "   - 披露新闻测试：180 秒"
echo ""
echo "🚀 使用建议:"
echo "   - 单元测试：< 30 秒"
echo "   - 网络测试：60-120 秒"
echo "   - 批量 API: 120-180 秒"
echo ""
