#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpha 量化引擎示例程序

本示例展示如何使用 akshare-one 的 Alpha 量化引擎进行因子计算、信号生成、
风险管理和回测评估。

依赖：
- pandas
- numpy
- statsmodels

运行方式：
    python alpha_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#alpha
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from akshare_one.modules.alpha import (
    normalize_factor_name,
    global_factor_registry,
    align_to_trade_days,
    safe_divide,
    FactorRegistry,
    winsorize_med,
    standardlize,
    neutralize,
    compute_market_cap,
    compute_pb_ratio,
    compute_momentum,
    compute_rsrs,
    compute_ma_cross,
    compute_breakthrough,
    get_signal_for_sec,
    get_performance_metrics,
    print_performance_summary,
    compute_drawdown,
    compute_atr_stop_loss,
    get_position_size_fixed_risk,
    check_max_drawdown_limit,
)


def scenario_1_factor_registry():
    """场景 1：因子注册与名称规范化"""
    print("\n" + "=" * 80)
    print("场景 1：因子注册与名称规范化")
    print("=" * 80)

    print("\n1.1 因子名称规范化")
    test_names = ["PE_ratio", "pe_ratio", "PB_ratio", "momentum", "unknown_factor"]
    print("测试因子名称：")
    for name in test_names:
        normalized = normalize_factor_name(name)
        print(f"  {name} -> {normalized}")

    print("\n1.2 全局因子注册表")
    registered_factors = global_factor_registry.list_factors()
    print(f"已注册因子数量：{len(registered_factors)}")
    print("已注册因子列表：")
    for factor_name in registered_factors:
        meta = global_factor_registry._metadata.get(factor_name, {})
        desc = meta.get("description", "")
        window = meta.get("window")
        deps = meta.get("dependencies", [])
        print(f"  - {factor_name}: {desc} (window={window}, deps={deps})")

    print("\n1.3 自定义因子注册")

    def custom_factor(symbol: str, end_date: str = None, **kwargs) -> float:
        return 1.0

    local_registry = FactorRegistry()
    local_registry.register(
        "custom_factor", custom_factor, window=10, dependencies=["price_data"], description="自定义测试因子"
    )
    print(f"本地注册表因子：{local_registry.list_factors()}")
    func = local_registry.get("custom_factor")
    print(f"获取自定义因子函数：{func is not None}")


def scenario_2_factor_preprocessing():
    """场景 2：因子预处理（去极值、标准化、中性化）"""
    print("\n" + "=" * 80)
    print("场景 2：因子预处理")
    print("=" * 80)

    print("\n2.1 生成模拟因子数据")
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="B")
    securities = [f"sec_{i:03d}" for i in range(10)]
    data = pd.DataFrame(np.random.randn(len(dates), len(securities)) * 10 + 50, index=dates, columns=securities)
    data.iloc[::5, :] = data.iloc[::5, :] * 3
    print(f"原始数据形状：{data.shape}")
    print(f"原始数据均值范围：{data.mean().min():.2f} ~ {data.mean().max():.2f}")
    print(f"原始数据标准差范围：{data.std().min():.2f} ~ {data.std().max():.2f}")

    print("\n2.2 去极值处理 (MAD方法)")
    data_winsorized = winsorize_med(data, scale=3.0, inclusive=True)
    print(f"去极值后均值范围：{data_winsorized.mean().min():.2f} ~ {data_winsorized.mean().max():.2f}")
    print(f"去极值后标准差范围：{data_winsorized.std().min():.2f} ~ {data_winsorized.std().max():.2f}")

    print("\n2.3 标准化处理 (Z-Score)")
    data_standardized = standardlize(data_winsorized)
    print(f"标准化后均值：{data_standardized.mean().mean():.4f} (应接近0)")
    print(f"标准化后标准差：{data_standardized.std().mean():.4f} (应接近1)")

    print("\n2.4 中性化处理 (对市值因子)")
    market_cap = pd.Series(np.random.rand(len(securities)) * 1e10 + 1e9, index=securities)
    data_neutral = neutralize(data_standardized, how=["market_cap"], market_cap=market_cap)
    print(f"中性化后数据形状：{data_neutral.shape}")
    print(f"中性化后因子间相关性降低")


def scenario_3_technical_signals():
    """场景 3：技术信号计算"""
    print("\n" + "=" * 80)
    print("场景 3：技术信号计算")
    print("=" * 80)

    print("\n3.1 生成模拟行情数据")
    dates = pd.date_range(start="2024-01-01", periods=300, freq="B")
    close = pd.Series(100 + np.cumsum(np.random.randn(300) * 2), index=dates)
    high = close + np.random.rand(300) * 3
    low = close - np.random.rand(300) * 3
    print(f"行情数据长度：{len(close)} 个交易日")

    print("\n3.2 RSRS 阻力支撑相对强度信号")
    rsrs_signal = compute_rsrs(high, low, n=18, m=60)
    rsrs_latest = rsrs_signal.iloc[-1]
    rsrs_status = "看多" if rsrs_latest > 0.8 else ("看空" if rsrs_latest < -0.8 else "中性")
    print(f"RSRS 最新值：{rsrs_latest:.4f} -> {rsrs_status}")

    print("\n3.3 均线交叉信号 (MA5 vs MA20)")
    ma_cross_signal = compute_ma_cross(close, fast=5, slow=20)
    ma_latest = ma_cross_signal.iloc[-1]
    ma_status = {1: "金叉(看多)", -1: "死叉(看空)", 0: "中性"}.get(ma_latest, "未知")
    print(f"MA 交叉最新信号：{ma_latest} -> {ma_status}")

    print("\n3.4 突破信号 (20日高低点)")
    breakthrough_signal = compute_breakthrough(high, low, close, window=20)
    bt_latest = breakthrough_signal.iloc[-1]
    bt_status = {1: "向上突破", -1: "向下突破", 0: "盘整"}.get(bt_latest, "未知")
    print(f"突破信号最新值：{bt_latest} -> {bt_status}")


def scenario_4_performance_evaluation():
    """场景 4：回测绩效评估"""
    print("\n" + "=" * 80)
    print("场景 4：回测绩效评估")
    print("=" * 80)

    print("\n4.1 生成模拟收益率序列")
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", periods=252, freq="B")
    daily_returns = pd.Series(np.random.randn(252) * 0.02 + 0.0005, index=dates)
    print(f"收益率序列长度：{len(daily_returns)} 个交易日")
    print(f"累计收益率：{(1 + daily_returns).prod() - 1:.2%}")

    print("\n4.2 计算回撤序列")
    drawdown_df = compute_drawdown(daily_returns)
    max_drawdown = drawdown_df["drawdown"].min()
    print(f"最大回撤：{max_drawdown:.2%}")
    print(f"最大回撤发生日期：{drawdown_df['drawdown'].idxmin().strftime('%Y-%m-%d')}")

    print("\n4.3 计算绩效指标")
    metrics = get_performance_metrics(daily_returns, risk_free_rate=0.02)
    print(f"年化收益率：{metrics['annual_return']:.2%}")
    print(f"年化波动率：{metrics['annual_volatility']:.2%}")
    print(f"夏普比率：{metrics['sharpe_ratio']:.4f}")
    print(f"索提诺比率：{metrics['sortino_ratio']:.4f}")
    print(f"最大回撤：{metrics['max_drawdown']:.2%}")
    print(f"胜率：{metrics['win_rate']:.2%}")

    print("\n4.4 打印绩效汇总")
    print_performance_summary(metrics)


def scenario_5_risk_management():
    """场景 5：风险管理与仓位计算"""
    print("\n" + "=" * 80)
    print("场景 5：风险管理与仓位计算")
    print("=" * 80)

    print("\n5.1 生成模拟行情数据")
    dates = pd.date_range(start="2024-01-01", periods=100, freq="B")
    close = pd.Series(100 + np.cumsum(np.random.randn(100) * 0.5), index=dates)
    high = close + np.random.rand(100) * 2
    low = close - np.random.rand(100) * 2
    print(f"行情数据长度：{len(close)} 个交易日")

    print("\n5.2 ATR 止损价位计算")
    atr_stop = compute_atr_stop_loss(high, low, close, window=14, multiplier=2.0)
    atr_stop_latest = atr_stop.iloc[-1]
    close_latest = close.iloc[-1]
    print(f"当前收盘价：{close_latest:.2f}")
    print(f"ATR 止损价：{atr_stop_latest:.2f}")
    print(f"潜在损失：{(atr_stop_latest / close_latest - 1):.2%}")

    print("\n5.3 固定风险仓位计算")
    portfolio_value = 1_000_000.0
    risk_per_trade = 0.02
    entry_price = 100.0
    stop_loss_price = 95.0
    position_size = get_position_size_fixed_risk(portfolio_value, risk_per_trade, entry_price, stop_loss_price)
    risk_amount = portfolio_value * risk_per_trade
    print(f"账户净值：{portfolio_value:,.2f}")
    print(f"单笔风险比例：{risk_per_trade:.0%}")
    print(f"单笔风险金额：{risk_amount:,.2f}")
    print(f"买入价格：{entry_price:.2f}")
    print(f"止损价格：{stop_loss_price:.2f}")
    print(f"建议仓位数量（手）：{position_size // 100} 手 ({position_size} 股)")

    print("\n5.4 最大回撤限制检查")
    test_drawdowns = [-0.05, -0.08, -0.10, -0.12, -0.15]
    default_limit = -0.10
    print(f"默认回撤限制：{default_limit:.0%}")
    for dd in test_drawdowns:
        breached = check_max_drawdown_limit(dd, limit=default_limit)
        status = "触发风控" if breached else "正常"
        print(f"  当前回撤 {dd:.0%} -> {status}")


def scenario_6_safe_divide():
    """场景 6：安全除法运算"""
    print("\n" + "=" * 80)
    print("场景 6：安全除法运算")
    print("=" * 80)

    print("\n6.1 基本安全除法")
    a = np.array([10, 20, 30, 40])
    b = np.array([2, 5, 0, 4])
    result = safe_divide(a, b)
    print(f"分子：{a}")
    print(f"分母：{b}")
    print(f"结果：{result}")
    print(f"注：0 除以 0 时返回 nan，而非 inf")

    print("\n6.2 含 NaN 的安全除法")
    a_nan = np.array([10, np.nan, 30, 40])
    b_nan = np.array([2, 5, 0, np.nan])
    result_nan = safe_divide(a_nan, b_nan)
    print(f"分子：{a_nan}")
    print(f"分母：{b_nan}")
    print(f"结果：{result_nan}")


def scenario_7_align_to_trade_days():
    """场景 7：交易日对齐"""
    print("\n" + "=" * 80)
    print("场景 7：交易日对齐")
    print("=" * 80)

    print("\n7.1 创建非交易日数据并对齐")
    all_dates = pd.date_range(start="2024-01-01", end="2024-01-31", freq="D")
    non_trade_dates = [d for d in all_dates if d.weekday() >= 5]
    df = pd.DataFrame({"date": [d.strftime("%Y-%m-%d") for d in non_trade_dates], "value": range(len(non_trade_dates))})
    print(f"原始数据（仅非交易日）：{len(df)} 条")

    df_aligned = align_to_trade_days(df, date_col="date", fill_method="ffill")
    print(f"对齐后数据：{len(df_aligned)} 条")
    print(f"前5条：\n{df_aligned.head()}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("Alpha 量化引擎示例程序")
    print("=" * 80)

    scenario_1_factor_registry()
    scenario_2_factor_preprocessing()
    scenario_3_technical_signals()
    scenario_4_performance_evaluation()
    scenario_5_risk_management()
    scenario_6_safe_divide()
    scenario_7_align_to_trade_days()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
