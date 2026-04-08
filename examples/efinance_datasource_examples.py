"""
Efinance数据源使用示例

本示例展示如何使用efinance作为数据源获取各类金融数据
"""

import sys

sys.path.insert(0, "src")

from akshare_one.modules.futures import get_futures_hist_data, get_futures_realtime_data
from akshare_one.modules.historical import get_hist_data
from akshare_one.modules.realtime import get_realtime_data
from akshare_one.modules.fund import (
    get_fund_quote_history,
    get_fund_info,
    get_fund_holdings,
    get_fund_industry_distribution,
)
from akshare_one.modules.bond import get_bond_spot, get_bond_hist


def example_futures_historical():
    """期货历史数据示例"""
    print("=" * 60)
    print("期货历史数据 - Efinance数据源")
    print("=" * 60)

    # 获取铜期货主力合约历史数据
    df = get_futures_hist_data(
        symbol="CU",
        contract="main",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-04-08",
        source="efinance",  # 指定使用efinance数据源
    )

    print(f"\n获取到 {len(df)} 条数据")
    print("\n前5条数据:")
    print(df.head())
    print("\n字段列表:", list(df.columns))


def example_futures_realtime():
    """期货实时行情示例"""
    print("\n" + "=" * 60)
    print("期货实时行情 - Efinance数据源")
    print("=" * 60)

    # 获取所有期货实时行情
    df = get_futures_realtime_data(source="efinance")

    print(f"\n获取到 {len(df)} 条数据")
    print("\n前5条数据:")
    print(df.head())


def example_stock_historical():
    """股票历史K线示例"""
    print("\n" + "=" * 60)
    print("股票历史K线数据 - Efinance数据源")
    print("=" * 60)

    # 获取贵州茅台历史数据
    df = get_hist_data(
        symbol="600519",
        interval="day",
        start_date="2024-01-01",
        end_date="2024-04-08",
        adjust="qfq",  # 前复权
        source="efinance",
    )

    print(f"\n获取到 {len(df)} 条数据")
    print("\n前5条数据:")
    print(df.head())

    # 支持非A股市场
    print("\n" + "-" * 60)
    print("美股示例 - 苹果公司")
    print("-" * 60)

    df_apple = get_hist_data(symbol="AAPL", interval="day", start_date="2024-01-01", source="efinance")

    print(f"\n获取到 {len(df_apple)} 条数据")
    print(df_apple.head())


def example_stock_realtime():
    """股票实时行情示例"""
    print("\n" + "=" * 60)
    print("股票实时行情 - Efinance数据源")
    print("=" * 60)

    # 获取所有A股实时行情
    df = get_realtime_data(source="efinance")

    print(f"\n获取到 {len(df)} 条数据")
    print("\n涨幅前10:")
    print(df.nlargest(10, "pct_change")[["symbol", "name", "price", "pct_change"]])

    # 获取单只股票实时行情
    print("\n" + "-" * 60)
    print("单只股票实时行情 - 平安银行")
    print("-" * 60)

    df_single = get_realtime_data(symbol="000001", source="efinance")

    print(df_single)


def example_fund_data():
    """基金数据示例"""
    print("\n" + "=" * 60)
    print("基金数据 - Efinance数据源")
    print("=" * 60)

    # 获取基金历史净值
    print("\n招商中证白酒指数基金 (161725) 历史净值:")
    df_nav = get_fund_quote_history(fund_code="161725", source="efinance")

    print(f"\n获取到 {len(df_nav)} 条数据")
    print(df_nav.head())

    # 获取基金基本信息
    print("\n" + "-" * 60)
    print("基金基本信息")
    print("-" * 60)

    df_info = get_fund_info(fund_codes=["161725", "005827"], source="efinance")

    print(df_info)

    # 获取基金持仓
    print("\n" + "-" * 60)
    print("基金持仓信息")
    print("-" * 60)

    df_holdings = get_fund_holdings(fund_code="161725", source="efinance")

    print(df_holdings)


def example_bond_data():
    """债券数据示例"""
    print("\n" + "=" * 60)
    print("可转债数据 - Efinance数据源")
    print("=" * 60)

    # 获取可转债实时行情
    df = get_bond_spot(source="efinance")

    print(f"\n获取到 {len(df)} 条可转债数据")
    print("\n涨幅前10:")
    print(df.nlargest(10, "pct_change")[["bond_code", "name", "price", "pct_change"]])

    # 获取可转债历史数据
    print("\n" + "-" * 60)
    print("东财转3 (123111) 历史数据")
    print("-" * 60)

    df_hist = get_bond_hist(bond_code="123111", start_date="2024-01-01", end_date="2024-04-08", source="efinance")

    print(f"\n获取到 {len(df_hist)} 条数据")
    print(df_hist.head())


def example_multi_source():
    """多数据源对比示例"""
    print("\n" + "=" * 60)
    print("多数据源对比")
    print("=" * 60)

    symbol = "600519"

    # 使用efinance
    df_efinance = get_hist_data(symbol=symbol, start_date="2024-03-01", end_date="2024-03-31", source="efinance")
    print(f"\nEfinance: {len(df_efinance)} 条记录")

    # 使用sina
    df_sina = get_hist_data(symbol=symbol, start_date="2024-03-01", end_date="2024-03-31", source="sina")
    print(f"Sina: {len(df_sina)} 条记录")

    # 自动选择（按注册顺序尝试）
    df_auto = get_hist_data(
        symbol=symbol,
        start_date="2024-03-01",
        end_date="2024-03-31",
        source=None,  # 自动选择
    )
    print(f"自动选择: {len(df_auto)} 条记录")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║        Efinance 数据源集成示例                             ║
║                                                           ║
║  已集成模块:                                               ║
║  1. futures  - 期货历史数据 & 实时行情                     ║
║  2. historical - 股票历史K线                              ║
║  3. realtime - 股票实时行情                               ║
║  4. fund - 基金净值、持仓、配置                           ║
║  5. bond - 可转债数据                                     ║
║                                                           ║
║  使用方式: source="efinance"                              ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行示例（取消注释以测试）

    # example_futures_historical()
    # example_futures_realtime()
    # example_stock_historical()
    # example_stock_realtime()
    # example_fund_data()
    # example_bond_data()
    # example_multi_source()

    print("\n请取消注释相应的示例函数来运行测试")
    print("注意：需要网络连接以访问efinance API")
