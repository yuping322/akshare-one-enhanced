#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算示例程序

本示例展示如何使用 akshare-one 的指标模块计算技术分析指标。

依赖：
- pandas
- numpy

运行方式：
    python indicators_example.py

相关文档：
- API 文档：docs/api/interfaces-reference.md#indicators
"""

import pandas as pd
import numpy as np

from akshare_one.modules.indicators import (
    IndicatorFactory,
    BaseIndicatorCalculator,
    SimpleIndicatorCalculator,
    TALIB_AVAILABLE,
)


def create_sample_data(days: int = 100) -> pd.DataFrame:
    """创建示例股票数据"""
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="D")
    np.random.seed(42)

    base_price = 100
    returns = np.random.normal(0.001, 0.02, days)
    close = base_price * np.exp(np.cumsum(returns))
    high = close * (1 + np.random.uniform(0, 0.02, days))
    low = close * (1 - np.random.uniform(0, 0.02, days))
    open_price = low + (high - low) * np.random.uniform(0, 1, days)
    volume = np.random.randint(1000000, 10000000, days)

    df = pd.DataFrame(
        {
            "date": dates,
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
    df.set_index("date", inplace=True)
    return df


def scenario_1_basic_indicators():
    """场景 1：计算基础技术指标"""
    print("\n" + "=" * 80)
    print("场景 1：计算基础技术指标")
    print("=" * 80)

    try:
        df = create_sample_data(100)
        print(f"\n原始数据：{len(df)} 条记录")
        print(df.tail(5))

        calculator = IndicatorFactory.get_calculator("simple")
        print(f"\n使用计算器：{type(calculator).__name__}")

        sma_20 = calculator.calculate_sma(df, 20)
        ema_20 = calculator.calculate_ema(df, 20)
        rsi_14 = calculator.calculate_rsi(df, 14)

        print("\nSMA(20) 结果（前5条）：")
        print(sma_20.head().to_string())

        print("\nEMA(20) 结果（前5条）：")
        print(ema_20.head().to_string())

        print("\nRSI(14) 结果（前5条）：")
        print(rsi_14.head().to_string())

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_2_macd_bollinger():
    """场景 2：计算 MACD 和布林带"""
    print("\n" + "=" * 80)
    print("场景 2：计算 MACD 和布林带")
    print("=" * 80)

    try:
        df = create_sample_data(100)

        calculator = SimpleIndicatorCalculator()

        macd = calculator.calculate_macd(df, fast=12, slow=26, signal=9)
        print("\nMACD 结果（最后5条）：")
        print(macd.tail().to_string())

        bollinger = calculator.calculate_bollinger_bands(df, window=20, std=2)
        print("\n布林带结果（最后5条）：")
        print(bollinger.tail().to_string())

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_3_momentum_indicators():
    """场景 3：计算动量指标"""
    print("\n" + "=" * 80)
    print("场景 3：计算动量指标")
    print("=" * 80)

    try:
        df = create_sample_data(100)

        calculator = SimpleIndicatorCalculator()

        stoch = calculator.calculate_stoch(df, window=14, smooth_d=3, smooth_k=3)
        print("\nKDJ 随机指标（最后5条）：")
        print(stoch.tail().to_string())

        cci = calculator.calculate_cci(df, window=20)
        print("\nCCI 顺势指标（最后5条）：")
        print(cci.tail().to_string())

        willr = calculator.calculate_willr(df, window=14)
        print("\n威廉指标（最后5条）：")
        print(willr.tail().to_string())

        mfi = calculator.calculate_mfi(df, window=14)
        print("\nMFI 资金流量指标（最后5条）：")
        print(mfi.tail().to_string())

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_4_talib_calculator():
    """场景 4：使用 TALIB 计算器（如可用）"""
    print("\n" + "=" * 80)
    print("场景 4：使用 TALIB 计算器")
    print("=" * 80)

    try:
        print(f"\nTALIB 可用状态：{TALIB_AVAILABLE}")

        df = create_sample_data(100)

        calculator = IndicatorFactory.get_calculator("talib")
        print(f"实际使用计算器：{type(calculator).__name__}")

        sma_20 = calculator.calculate_sma(df, 20)
        rsi_14 = calculator.calculate_rsi(df, 14)

        print("\nSMA(20) 结果（最后5条）：")
        print(sma_20.tail().to_string())

        print("\nRSI(14) 结果（最后5条）：")
        print(rsi_14.tail().to_string())

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_5_volatility_indicators():
    """场景 5：计算波动率指标"""
    print("\n" + "=" * 80)
    print("场景 5：计算波动率指标")
    print("=" * 80)

    try:
        df = create_sample_data(100)

        calculator = SimpleIndicatorCalculator()

        atr = calculator.calculate_atr(df, window=14)
        print("\nATR 平均真实波幅（最后5条）：")
        print(atr.tail().to_string())

        adx = calculator.calculate_adx(df, window=14)
        print("\nADX 趋势指标（最后5条）：")
        print(adx.tail().to_string())

    except Exception as e:
        print(f"发生错误：{e}")


def scenario_6_volume_indicators():
    """场景 6：计算成交量指标"""
    print("\n" + "=" * 80)
    print("场景 6：计算成交量指标")
    print("=" * 80)

    try:
        df = create_sample_data(100)

        calculator = SimpleIndicatorCalculator()

        obv = calculator.calculate_obv(df)
        print("\nOBV 能量潮（最后5条）：")
        print(obv.tail().to_string())

        ad = calculator.calculate_ad(df)
        print("\nAD 累积派散（最后5条）：")
        print(ad.tail().to_string())

        adosc = calculator.calculate_adosc(df, fast_period=3, slow_period=10)
        print("\nADOSC 异同离散指标（最后5条）：")
        print(adosc.tail().to_string())

    except Exception as e:
        print(f"发生错误：{e}")


def main():
    """运行所有场景"""
    print("=" * 80)
    print("技术指标计算示例程序")
    print("=" * 80)

    print(f"\nTALIB 可用：{TALIB_AVAILABLE}")

    scenario_1_basic_indicators()
    scenario_2_macd_bollinger()
    scenario_3_momentum_indicators()
    scenario_4_talib_calculator()
    scenario_5_volatility_indicators()
    scenario_6_volume_indicators()

    print("\n" + "=" * 80)
    print("所有场景运行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
