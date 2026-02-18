# MCP 独立包使用说明

## 概述

`akshare-one-mcp` 是一个独立的包，提供了基于 Model Context Protocol (MCP) 的股票数据访问工具。它可以与 Claude Desktop、Cursor 等支持 MCP 的 AI 助手集成。

## 安装

### 方式 1: 作为核心包的附加组件

```bash
pip install akshare-one[mcp]
```

### 方式 2: 仅安装 MCP 包（需要核心包）

```bash
pip install akshare-one
pip install fastmcp>=2.11.3 pydantic>=2.0.0 uvicorn>=0.35.0
```

## 启动 MCP 服务

### 命令行

```bash
akshare-one-mcp
```

或使用 Python:

```bash
python -m akshare_one_mcp
```

### Claude Desktop 配置

在 `claude_desktop_config.json` 中添加:

```json
{
  "mcpServers": {
    "akshare-one": {
      "command": "akshare-one-mcp",
      "env": {
        "PYTHONPATH": "/path/to/your/python/site-packages"
      }
    }
  }
}
```

### Cursor 配置

在 Cursor 设置中添加 MCP 服务器:

```json
{
  "mcpServers": [
    {
      "name": "akshare-one",
      "command": "akshare-one-mcp"
    }
  ]
}
```

## 可用工具

MCP 包提供了 47 个数据访问工具:

### 基础数据
- `get_hist_data` - 历史行情数据
- `get_realtime_data` - 实时行情数据
- `get_news_data` - 个股新闻
- `get_basic_info` - 基础信息

### 财务数据
- `get_balance_sheet` - 资产负债表
- `get_income_statement` - 利润表
- `get_cash_flow` - 现金流量表
- `get_financial_metrics` - 财务指标

### 资金流向
- `get_stock_fund_flow` - 个股资金流向
- `get_sector_fund_flow` - 板块资金流向
- `get_main_fund_flow_rank` - 主力资金排行
- `get_northbound_flow` - 北向资金流向
- `get_northbound_holdings` - 北向资金持仓

### 龙虎榜
- `get_dragon_tiger_list` - 龙虎榜列表
- `get_dragon_tiger_summary` - 龙虎榜统计
- `get_dragon_tiger_broker_stats` - 营业部统计

### 涨跌停
- `get_limit_up_pool` - 涨停池
- `get_limit_down_pool` - 跌停池
- `get_limit_up_stats` - 涨跌停统计

### 披露信息
- `get_disclosure_news` - 公告信息
- `get_dividend_data` - 分红数据
- `get_repurchase_data` - 回购数据
- `get_st_delist_data` - ST/退市风险

### 宏观经济
- `get_lpr_rate` - LPR利率
- `get_pmi_index` - PMI指数
- `get_cpi_data` - CPI数据
- `get_ppi_data` - PPI数据
- `get_m2_supply` - M2货币供应
- `get_shibor_rate` - Shibor利率
- `get_social_financing` - 社融数据

### 大宗交易
- `get_block_deal` - 大宗交易明细
- `get_block_deal_summary` - 大宗交易统计

### 融资融券
- `get_margin_data` - 融资融券明细
- `get_margin_summary` - 融资融券汇总

### 股权质押
- `get_equity_pledge` - 股权质押数据
- `get_equity_pledge_ratio_rank` - 质押比例排名

### 限售解禁
- `get_restricted_release` - 限售解禁数据
- `get_restricted_release_calendar` - 解禁日历

### 商誉
- `get_goodwill_data` - 商誉数据
- `get_goodwill_impairment` - 商誉减值
- `get_goodwill_by_industry` - 行业商誉

### ESG
- `get_esg_rating` - ESG评级
- `get_esg_rating_rank` - ESG排名

## 工具参数说明

所有工具都支持以下通用参数:

- `symbol`: 股票代码 (如 "600000")
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `recent_n`: 返回最近 N 条记录
- `columns`: 指定返回的列
- `row_filter`: 行过滤条件

## 示例用法

### 获取历史数据

```python
# 在 Claude/Cursor 中询问
"请帮我获取贵州茅台(600519)最近30天的日线数据"
```

AI 助手将调用:
```json
{
  "tool": "get_hist_data",
  "params": {
    "symbol": "600519",
    "interval": "day",
    "recent_n": 30
  }
}
```

### 获取资金流向

```python
"查看宁德时代(300750)最近一周的主力资金流向"
```

AI 助手将调用:
```json
{
  "tool": "get_stock_fund_flow",
  "params": {
    "symbol": "300750",
    "recent_n": 7
  }
}
```

### 获取北向资金

```python
"北向资金最近一个月都买了哪些股票？"
```

AI 助手将调用:
```json
{
  "tool": "get_northbound_top_stocks",
  "params": {
    "date": "2024-01-15",
    "top_n": 20
  }
}
```

## 故障排除

### 导入错误

如果遇到 `ModuleNotFoundError`:

```bash
# 确保安装路径正确
pip show akshare-one

# 添加 PYTHONPATH
export PYTHONPATH="/path/to/akshare-one/src:$PYTHONPATH"
```

### 数据获取失败

- 检查网络连接
- 验证股票代码格式
- 查看日志输出

### 服务启动失败

```bash
# 检查依赖
pip install --upgrade fastmcp pydantic uvicorn

# 测试导入
python -c "from akshare_one_mcp import mcp, run_server; print('OK')"
```

## 开发

### 本地测试

```bash
# 运行 MCP 测试
cd tests/mcp
pytest test_mcp.py test_mcp_p0.py test_mcp_p1_p2.py -v
```

### 添加新工具

1. 在 `src/akshare_one_mcp/server.py` 添加工具函数
2. 使用 `@mcp.tool` 装饰器
3. 在 `tests/mcp/` 添加测试

示例:
```python
@mcp.tool
def get_new_data(
    symbol: Annotated[str, Field(description="Stock symbol")],
) -> str:
    """Get new data."""
    from akshare_one.modules.new import get_new_data as _get_new_data
    df = _get_new_data(symbol=symbol)
    return df.to_json(orient="records") or "[]"
```

## 更多信息

- [MCP 协议文档](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [akshare-one 文档](../README.md)
