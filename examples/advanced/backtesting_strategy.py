#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级示例 1：简单的回测策略

本示例展示如何使用 akshare-one 的数据进行简单的策略回测，包括：
- 获取历史数据
- 计算技术指标
- 简单的策略回测
- 计算收益率

运行方式：
    python examples/advanced/backtesting_strategy.py

注意：本示例仅供学习参考，不构成投资建议
"""

import pandas as pd
import numpy as np
from datetime import datetime
from akshare_one import get_hist_data


class SimpleStrategy:
    """简单的均线策略"""

    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = None

    def load_data(self):
        """加载历史数据"""
        try:
            self.data = get_hist_data(
                symbol=self.symbol,
                interval="day",
                start_date=self.start_date,
                end_date=self.end_date,
                adjust="qfq",
                source="sina",
            )
            print(f"已加载 {len(self.data)} 条历史数据")
        except ConnectionError as e:
            print(f"网络连接错误：{e}")
            print("提示：请检查网络连接或稍后重试")
            self.data = pd.DataFrame()
        except Exception as e:
            print(f"加载数据失败：{e}")
            self.data = pd.DataFrame()

    def calculate_indicators(self):
        """计算技术指标"""
        if self.data is None or self.data.empty:
            print("数据为空，无法计算指标")
            return

        # 计算均线
        self.data["ma5"] = self.data["close"].rolling(window=5).mean()
        self.data["ma10"] = self.data["close"].rolling(window=10).mean()
        self.data["ma20"] = self.data["close"].rolling(window=20).mean()

        # 计算涨跌幅
        self.data["pct_change"] = self.data["close"].pct_change() * 100

        # 计算成交量均线
        self.data["volume_ma5"] = self.data["volume"].rolling(window=5).mean()

        print("已计算技术指标：MA5, MA10, MA20, 成交量MA5")

    def generate_signals(self):
        """生成买卖信号"""
        if self.data is None or self.data.empty:
            print("数据为空，无法生成信号")
            return

        # 策略：MA5上穿MA20买入，MA5下穿MA20卖出
        self.data["signal"] = 0

        # MA5上穿MA20（买入信号）
        self.data.loc[
            (self.data["ma5"] > self.data["ma20"]) & (self.data["ma5"].shift(1) <= self.data["ma20"].shift(1)), "signal"
        ] = 1

        # MA5下穿MA20（卖出信号）
        self.data.loc[
            (self.data["ma5"] < self.data["ma20"]) & (self.data["ma5"].shift(1) >= self.data["ma20"].shift(1)), "signal"
        ] = -1

        print(f"已生成买卖信号")
        print(f"买入信号数: {len(self.data[self.data['signal'] == 1])}")
        print(f"卖出信号数: {len(self.data[self.data['signal'] == -1])}")

    def backtest(self):
        """执行回测"""
        if self.data is None or self.data.empty:
            print("数据为空，无法回测")
            return None

        # 初始化
        position = 0  # 持仓数量
        cash = 100000  # 初始资金10万
        total_value = cash  # 总资产

        trades = []  # 交易记录
        daily_values = []  # 每日资产价值

        for i, row in self.data.iterrows():
            date = row["timestamp"]
            close = row["close"]
            signal = row["signal"]

            # 买入
            if signal == 1 and position == 0:
                # 全仓买入
                shares = int(cash / close / 100) * 100  # 买入手数（100股为一手）
                cost = shares * close
                position = shares
                cash -= cost
                trades.append({"date": date, "action": "买入", "price": close, "shares": shares, "cost": cost})

            # 卖出
            elif signal == -1 and position > 0:
                # 全仓卖出
                revenue = position * close
                cash += revenue
                trades.append({"date": date, "action": "卖出", "price": close, "shares": position, "revenue": revenue})
                position = 0

            # 记录每日资产价值
            total_value = cash + position * close
            daily_values.append(
                {
                    "date": date,
                    "cash": cash,
                    "position": position,
                    "position_value": position * close,
                    "total_value": total_value,
                }
            )

        # 最后如果还持仓，按最后价格清仓
        if position > 0:
            final_price = self.data.iloc[-1]["close"]
            cash += position * final_price
            position = 0
            total_value = cash

        # 转换为DataFrame
        self.trades_df = pd.DataFrame(trades)
        self.daily_values_df = pd.DataFrame(daily_values)

        # 计算收益率
        initial_capital = 100000
        final_capital = total_value
        total_return = (final_capital - initial_capital) / initial_capital * 100

        print("\n回测结果：")
        print(f"初始资金: {initial_capital:.2f}元")
        print(f"最终资金: {final_capital:.2f}元")
        print(f"总收益率: {total_return:.2f}%")
        print(f"交易次数: {len(trades)}")

        return {
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "total_return": total_return,
            "num_trades": len(trades),
        }

    def show_trades(self):
        """显示交易记录"""
        if hasattr(self, "trades_df") and not self.trades_df.empty:
            print("\n交易记录：")
            print(self.trades_df.to_string(index=False))
        else:
            print("没有交易记录")

    def show_daily_values(self):
        """显示资产变化"""
        if hasattr(self, "daily_values_df") and not self.daily_values_df.empty:
            # 显示每月末的资产价值
            monthly = self.daily_values_df.groupby(self.daily_values_df["date"].str[:7]).last()

            print("\n月末资产价值：")
            print(monthly[["total_value"]].to_string())

    def show_statistics(self):
        """显示统计信息"""
        if hasattr(self, "daily_values_df") and not self.daily_values_df.empty:
            df = self.daily_values_df

            # 计算最大回撤
            df["cummax"] = df["total_value"].cummax()
            df["drawdown"] = (df["total_value"] - df["cummax"]) / df["cummax"]
            max_drawdown = df["drawdown"].min()

            # 计算夏普比率（简化版）
            df["daily_return"] = df["total_value"].pct_change()
            avg_return = df["daily_return"].mean()
            std_return = df["daily_return"].std()
            sharpe_ratio = avg_return / std_return * np.sqrt(252) if std_return > 0 else 0

            print("\n风险指标：")
            print(f"最大回撤: {max_drawdown:.2%}")
            print(f"夏普比率: {sharpe_ratio:.2f}")


def main():
    """运行回测"""
    print("=" * 60)
    print("简单均线策略回测")
    print("=" * 60)
    print("\n策略说明：")
    print("- MA5上穿MA20时买入")
    print("- MA5下穿MA20时卖出")
    print("- 全仓操作，无杠杆")
    print("- 注意：本示例仅供学习，不构成投资建议")
    print("=" * 60)

    try:
        strategy = SimpleStrategy(symbol="600000", start_date="2023-01-01", end_date="2024-12-31")

        strategy.load_data()

        if strategy.data.empty:
            print("未能加载数据，回测无法继续")
            return

        strategy.calculate_indicators()
        strategy.generate_signals()
        result = strategy.backtest()
        strategy.show_trades()
        strategy.show_statistics()

        print("\n" + "=" * 60)
        print("回测完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n回测过程出错：{e}")
        print("提示：请检查网络连接或数据可用性")
    print("简单均线策略回测")
    print("=" * 60)
    print("\n策略说明：")
    print("- MA5上穿MA20时买入")
    print("- MA5下穿MA20时卖出")
    print("- 全仓操作，无杠杆")
    print("- 注意：本示例仅供学习，不构成投资建议")
    print("=" * 60)

    # 创建策略
    strategy = SimpleStrategy(symbol="600000", start_date="2023-01-01", end_date="2024-12-31")

    # 加载数据
    strategy.load_data()

    # 计算指标
    strategy.calculate_indicators()

    # 生成信号
    strategy.generate_signals()

    # 执行回测
    result = strategy.backtest()

    # 显示结果
    strategy.show_trades()
    strategy.show_statistics()

    print("\n" + "=" * 60)
    print("回测完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
